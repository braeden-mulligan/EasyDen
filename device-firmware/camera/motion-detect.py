from PIL import Image
from picamera2.outputs import CircularOutput

import os, sys, datetime, socket, subprocess

import time

file_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(file_location + "/../..")

RECORDINGS_FILENAME_PREFIX = socket.gethostname() + "-"
RECORDINGS_FILE_LOCATION = os.path.realpath(file_location + "/../..") + "/files/recordings/"

if not os.path.exists(RECORDINGS_FILE_LOCATION):
	os.makedirs(RECORDINGS_FILE_LOCATION)

def _calculate_image_diff(frame1, frame2):
	image1 = Image.fromarray(frame1)
	image2 = Image.fromarray(frame2)
	hist1 = image1.histogram()
	hist2 = image2.histogram()

	return sum([abs(c - p) for c, p in zip(hist1, hist2)]) / len(hist1)

class Motion_Detector: 
	FRAMERATE = 15

	def __init__(self, picam2, encoder, config, settings, queue_inbound, queue_oubound):
		self.picam2 = picam2
		self.encoder = encoder
		self.config = config
		self.settings = settings
		self.queue_inbound = queue_inbound
		self.queue_outbound = queue_oubound

		self.picam2.configure(config)
		self.picam2.set_controls({"FrameRate": self.FRAMERATE})  
		self.encoder.output = CircularOutput()

		self.recording = False
		self.last_recording_start_time = datetime.datetime.now()
		self.last_recording_filepath = None
	
	def _capture_frame(self):
		w, h = self.config["lores"]["size"]
		frame = self.picam2.capture_buffer("lores")
		frame = frame[:w * h].reshape(h, w)
		return frame

	def _start_recording(self):
		self.last_recording_start_time = datetime.datetime.now()
		self.last_recording_filepath = RECORDINGS_FILE_LOCATION + RECORDINGS_FILENAME_PREFIX + self.last_recording_start_time.isoformat().split(".")[0] + ".h264"
		self.encoder.output.fileoutput = self.last_recording_filepath
		self.encoder.output.start()
		self.recording = True

	def _stop_recording(self):
		self.encoder.output.stop()
		subprocess.run([
			"ffmpeg", "-y", "-r", str(self.FRAMERATE), "-i", self.last_recording_filepath,
			"-c", "copy", #"-movflags", "+faststart",
			self.last_recording_filepath.split(".")[0] + ".mp4"
		])
		os.remove(self.last_recording_filepath)
		self.recording = False
	
	def shutdown(self):
		if self.recording:
			self._stop_recording()

		self.picam2.stop()
		self.picam2.stop_encoder(self.encoder)

	def run(self):
		self.picam2.start_encoder(self.encoder)
		self.picam2.start()
		time.sleep(1)
	
		previous_frame = None
		recording_end_time = datetime.datetime.now()

		while True:
			if not self.queue_inbound.empty():
				if self.queue_inbound.get(block = False) == "halt":
					break
			
			if previous_frame is None:
				previous_frame = self._capture_frame()
			current_frame = self._capture_frame()

			diff = _calculate_image_diff(current_frame, previous_frame)

			if diff > self.settings["motion_sensitivity"]:
				max_recording = self.last_recording_start_time + datetime.timedelta(seconds = self.settings["max_recording_time"])
				idle_time_end = datetime.datetime.now() + datetime.timedelta(seconds = self.settings["idle_return_delay"])
				recording_end_time = min(max_recording, idle_time_end)

				if not self.recording:
					self.queue_outbound.put("motion detect start", block = False)

					print("thread start recording")

					self._start_recording()

				elif datetime.datetime.now() > recording_end_time:
					self._stop_recording()
					self.queue_outbound.put("file ready " + self.last_recording_filepath, block = False)
					previous_frame = None
					continue
			else:
				if self.recording and datetime.datetime.now() > recording_end_time:
					print("thread stop recording")
					self._stop_recording()
					self.queue_outbound.put("file ready " + self.last_recording_filepath, block = False)
					previous_frame = None
					continue

			previous_frame = current_frame

		print("thread shutdown")

		self.shutdown()
