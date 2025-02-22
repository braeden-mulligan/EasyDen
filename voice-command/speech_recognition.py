import subprocess
from vosk import Model, KaldiRecognizer

import queue, sys, json, requests, os, logging, pyaudio
sys.path.append("..")

from common.log_handler import logger as log, init_log_file
from common import server_config
from common import device_definitions as defs

audio_data = queue.Queue()

#TODO: configurable and force into lowercase.
ASSISTANT_NAME = "edward"

AUDIO_INPUT_DEVICE = "TONOR TM20"
SAMPLERATE = 48000

AUDIO_OUTPUT_DEVICE = "hw:CARD=PCH,DEV=0"
WAKE_TONE = ""
CONFIRM_TONE = ""
ERROR_TONE = ""

def check_wake_word(transcription):
	log.debug("Transcription: " + transcription)
	if not transcription:
		return
	
	words = transcription.lower().split()
	
	if ASSISTANT_NAME in words:
		return True
	
	return False
	
def parse_command(transcription):
	command_keywords = ["set", "switch", "switched", "turn", "change"]

	words = transcription.lower().split()

	for keyword in command_keywords:
		if keyword in words:
			break
	else:
		return False

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
		setting = 0
	else:
		return False

	device_fetch_url = "http://" + server_config.SERVER_ADDR + "/device/{}/refresh"
	
	#TODO: error handle 
	devices = json.loads(requests.get(device_fetch_url.format("thermostat")).text)
	devices += json.loads(requests.get(device_fetch_url.format("poweroutlet")).text)

	for d in devices:
		if d["name"].lower() in transcription:
			issue_command(d, specifiers, setting)

	return True

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
			log.debug(status) 
		audio_data.put(bytes(data_in))
		return (bytes(frames), pyaudio.paContinue)

	istream = pa.open(input_device_index = find_mic_index(AUDIO_INPUT_DEVICE), format = pyaudio.paInt16, channels = 1, rate = SAMPLERATE, input = True, frames_per_buffer = 1024, stream_callback = istream_callback, start = True)

	woke = False

	while True:
		if recog.AcceptWaveform(audio_data.get()):
			result = json.loads(recog.Result())["text"]

			if woke:
				if parse_command(result):
					subprocess.Popen(["aplay", "-D", AUDIO_OUTPUT_DEVICE, CONFIRM_TONE])
				else:
					subprocess.Popen(["aplay", "-D", AUDIO_OUTPUT_DEVICE, ERROR_TONE])
				woke = False

			elif check_wake_word(result):
				subprocess.Popen(["aplay", "-D", AUDIO_OUTPUT_DEVICE, WAKE_TONE])
				woke = True

def run():
	init_log_file("voice-command.log")

	try:
		log.debug("Starting voice command recognition.")
		recognize_speech()
	except KeyboardInterrupt:
		raise
	except:
		logging.exception("Voice command recognizer crashed!", stack_info = True)
		raise

if __name__ == "__main__":
	run()
