from vosk import Model, KaldiRecognizer

import queue, sys, json, requests, os, logging, pyaudio

sys.path.append("..")
from configs import server_config
from configs import device_definitions as defs

audio_data = queue.Queue()

#TODO: configurable and force into lowercase.
ASSISTANT_NAME = "edward"

DEVICE_NAME = "TONOR TM20"
SAMPLERATE = 48000

def parse_command(transcription):
	print(transcription)
	if not transcription:
		return

	words = transcription.lower().split()
	
	detected_device_type = None

	if ASSISTANT_NAME not in words:
		return

	command_keywords = ["set", "switch", "switched", "turn", "change"]

	for keyword in command_keywords:
		if keyword in words:
			break
	else:
		return

	specifiers = []
	specifier_keywords = ["outlet", "socket", "outlets", "sockets"]
	specifier_map = {"one": 1, "two": 2, "three": 3, "four": 4, "first": 1, "second": 2, "third": 3, "fourth": 4}

	for keyword in specifier_keywords:
		if keyword in words:
			for k, v in specifier_map.items():
				if k in words:
					specifiers.append(v)

	setting = None

	if "on" in words:
		setting = 1
	elif "off" in words:
		if setting:
			return
		setting = 0
	else:
		return

	device_fetch_url = "http://" + server_config.SERVER_ADDR + "/device/{}/refresh"
	
	#TODO: error handle 
	devices = json.loads(requests.get(device_fetch_url.format("thermostat")).text)
	devices += json.loads(requests.get(device_fetch_url.format("poweroutlet")).text)

	for d in devices:
		if d["name"].lower() in transcription:
			issue_command(d, specifiers, setting)

# Only handling poweroutlets for now.
def issue_command(device, specifiers, setting):
	if device["type"] != defs.type_id("SH_TYPE_POWEROUTLET"):
		return
		
	new_state = device["attributes"]["socket_states"]["value"]

	if not specifiers:
		new_state = [setting] * len(new_state)
	else:
		for spec in specifiers:
			if spec > len(new_state):
				continue
			new_state[spec - 1] = setting

	update_attribute = {
	  "register": defs.register_id("POWEROUTLET_REG_STATE"),
	  "attribute_data": new_state
	}

	#TODO: error handle 
	command_url = "http://" + server_config.SERVER_ADDR + "/device/poweroutlet/command?id=" + str(device["id"])
	requests.put(command_url, data = json.dumps(update_attribute))


def recognize_speech():
	model = Model(lang="en-us")
	recog = KaldiRecognizer(model, SAMPLERATE)

	pa = pyaudio.PyAudio()

	def find_mic_index(device_name):
		for i in range(pa.get_device_count()):
			device = pa.get_device_info_by_index(i)
			if device_name in device["name"]:
				return device["index"]
		return None

	def istream_callback(data_in, frames, time, status):
		if status:
			print(status, file = sys.stderr)
		audio_data.put(bytes(data_in))
		return (bytes(frames), pyaudio.paContinue)

	istream = pa.open(input_device_index = find_mic_index(DEVICE_NAME), format = pyaudio.paInt16, channels = 1, rate = SAMPLERATE, input = True, frames_per_buffer = 1024, stream_callback = istream_callback, start = True)

	while True:
		if recog.AcceptWaveform(audio_data.get()):
			result = json.loads(recog.Result())
			parse_command(result["text"])


def run():
	log_dir = os.path.dirname(__file__) + "/logs"
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
	logging.basicConfig(filename=log_dir + "/speech_recognition.log", level = logging.DEBUG, format = "[%(asctime)s %(levelname)s %(name)s %(message)s] : ")
	logger = logging.getLogger(__name__)

	try:
		print("Starting voice command recognition.")
		recognize_speech()
	except KeyboardInterrupt:
		raise
	except:
		print("Caught unhandled exception. Check logs for details.")
		logging.exception("Voice command recognizer crashed!")
		raise

if __name__ == "__main__":
	run()
