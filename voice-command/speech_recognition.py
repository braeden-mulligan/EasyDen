from vosk import Model, KaldiRecognizer

import queue, sys, json, requests, os, logging
import sounddevice as sd

sys.path.append("..")
from configs import server_config
from configs import device_definitions as defs

audio_data = queue.Queue()
ASSISTANT_NAME = "jarvis"

#def issue_command():

def match_command(transcription):
	#print(transcription)
	if not transcription:
		return

	device_fetch_url = "http://" + server_config.SERVER_ADDR + "/device/{}/refresh"

	devices = json.loads(requests.get(device_fetch_url.format("thermostat")).text)
	devices += json.loads(requests.get(device_fetch_url.format("poweroutlet")).text)

	words = transcription.lower().split()
	
	if ASSISTANT_NAME not in words:
		return

	if "set" in words:
		command_word_index = words.index("set")
	else:
		return

	for d in devices:
		l = len(d["name"].split())
		command_phrase = words[command_word_index + 1 + l : ]
		
		if d["name"].lower() == " ".join(words[command_word_index + 1 : command_word_index + 1 + l]):
			print("BINGO")
			#issue_command(d, command_phrase)

def recognize_speech():
	def sd_istream_callback(data_in, frames, time, status):
		if status:
			print(status, file = sys.stderr)
		audio_data.put(bytes(data_in))

	device_info = sd.query_devices(kind = "input")
	samplerate = int(device_info["default_samplerate"])
	model = Model(lang="en-us")

	with sd.RawInputStream(samplerate = samplerate, blocksize = 8000, dtype = "int16", channels = 1, callback = sd_istream_callback):
		recog = KaldiRecognizer(model, samplerate)
		
		while True:
			if recog.AcceptWaveform(audio_data.get()):
				result = json.loads(recog.Result())
				match_command(result["text"])

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