import os, sys, importlib, threading, queue

import time
import select
import tty
import termios

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())


base_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(base_path + "/../..")
sys.path.append(base_path + "/..")

from libraries.linux.messaging_framework import Messaging_Framework
from libraries.linux.helpers import store_settings 
from common.log_handler import logger as log, init_log_file
from common import device_definitions as defs, utils
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

Motion_Detector = importlib.import_module("motion-detect").Motion_Detector
Video_Streamer = importlib.import_module("video-streaming").Video_Streamer

# TODO: make this shit thread-safe
class Camera_State:
	INACTIVE = 0
	MOTION_DETECT_IDLE = 1
	MOTION_DETECT_START_PENDING = 2
	MOTION_DETECT_RECORDING = 4
	MOTION_DETECT_SHUTTING_DOWN = 8
	VIDEO_STREAM_START_PENDING = 16
	VIDEO_STREAM_ACTIVE= 32
	VIDEO_STREAM_SHUTTING_DOWN = 64
	UNHANDLED_ERROR = 128

class Camera_Manager:
	def __init__(self):
		self.picam2 = Picamera2()
		self.settings = utils.load_json_file("settings.json")
		self.system_config = utils.load_json_file("config.json")
		self.low_res_size = (320, 240)
		self.med_res_size = (1280, 720)
		self.high_res_size = (1920, 1080)
		self.motion_detect_config = self.picam2.create_video_configuration(
			main = { "size": self.high_res_size, "format": "RGB888" },
			lores = { "size": self.low_res_size, "format": "YUV420" }
		)
		self.streaming_config = self.picam2.create_video_configuration(
			main = { "size": self.med_res_size, "format": "RGB888" },
			lores = { "size": self.low_res_size, "format": "YUV420" }
		)
		self.streaming_config["server_address"] = (
			self.system_config["server_address"][self.system_config["environment"]],
			self.system_config["server_address"]["video_stream_port"]
		)
		self.encoder = H264Encoder(repeat = True)
		self.queue_outbound = queue.Queue(maxsize = 3)
		self.queue_inbound = queue.Queue(maxsize = 3)

		self.motion_detector = Motion_Detector(
			self.picam2,
			self.encoder,
			self.motion_detect_config,
			self.settings["motion_detection"],
			self.queue_outbound,
			self.queue_inbound,
		)
		self.video_streamer = Video_Streamer(
			self.picam2,
			self.encoder,
			self.streaming_config,
			self.settings["video_streaming"],
			self.queue_outbound,
			self.queue_inbound,
		)

		self.camera_state = Camera_State.INACTIVE
		self.motion_detect_thread = None
		self.video_stream_thread = None
		self.motion_detect_start_pending = False
		self.video_stream_start_pending = False
	
	def start_motion_detection(self):
		if self.motion_detect_thread is None and self.video_stream_thread is None:
			self.motion_detect_thread = threading.Thread(target = self.motion_detector.run)
			self.motion_detect_thread.start()
			print("Started motion detect thread ", self.motion_detect_thread)
			self.camera_state = Camera_State.MOTION_DETECT_IDLE
			print("Camera_State.MOTION_DETECT_IDLE")
			self.motion_detect_start_pending = False
		else:
			self.stop_video_stream()
			self.camera_state = Camera_State.MOTION_DETECT_START_PENDING
			if not self.camera_state == Camera_State.MOTION_DETECT_START_PENDING:
				print("Camera_State.MOTION_DETECT_START_PENDING")

			self.video_stream_start_pending = False
			self.motion_detect_start_pending = True

	def stop_motion_detection(self):
		self.motion_detect_start_pending = False

		if self.motion_detect_thread is not None:
			if not self.motion_detect_thread.is_alive():
				self.motion_detect_thread = None
				self.camera_state = Camera_State.INACTIVE
				print("1 Camera_State.INACTIVE")
			elif self.camera_state != Camera_State.MOTION_DETECT_SHUTTING_DOWN:
				self.queue_outbound.put("halt", block = False)
				self.camera_state = Camera_State.MOTION_DETECT_SHUTTING_DOWN
				print("2 Camera_State.MOTION_DETECT_SHUTTING_DOWN")
		else:
			self.camera_state = Camera_State.INACTIVE
			print("3 Camera_State.INACTIVE")

	def start_video_stream(self):
		if self.video_stream_thread is None and self.motion_detect_thread is None:
			self.video_stream_thread = threading.Thread(target = self.video_streamer.run)
			self.video_stream_thread.start()
			self.camera_state = Camera_State.VIDEO_STREAM_ACTIVE
			print("Camera_State.VIDEO_STREAM_ACTIVE")
			self.video_stream_start_pending = False
		else:
			self.stop_motion_detection()
			self.camera_state = Camera_State.VIDEO_STREAM_START_PENDING
			if not self.camera_state == Camera_State.VIDEO_STREAM_START_PENDING:
				print("Camera_State.VIDEO_STREAM_START_PENDING")

			self.motion_detect_start_pending = False
			self.video_stream_start_pending = True

	def stop_video_stream(self):
		self.video_stream_start_pending = False

		# TODO check resume motion detect

		if self.video_stream_thread is not None:
			if not self.video_stream_thread.is_alive():
				self.video_stream_thread = None
				self.camera_state = Camera_State.INACTIVE
				print("4 Camera_State.INACTIVE")
			elif self.camera_state != Camera_State.VIDEO_STREAM_SHUTTING_DOWN:
				self.queue_outbound.put("halt", block = False)
				self.camera_state = Camera_State.VIDEO_STREAM_SHUTTING_DOWN
				print("Camera_State.VIDEO_STREAM_SHUTTING_DOWN")
		else:
			self.camera_state = Camera_State.INACTIVE
			print(" 5 Camera_State.INACTIVE")
		pass

	#define CAMERA_ATTR_NOTIFICATIONS_GLOBAL 0x80
	#define CAMERA_ATTR_NOTIFY_MOTION_START 0x81
	#define CAMERA_ATTR_NOTIFY_FILE_READY 0x82
	#define CAMERA_ATTR_NOTIFY_INCLUDE_ATTACHMENT 0x83
	#define CAMERA_ATTR_CAMERA_STATE 0x84
	#define CAMERA_ATTR_MOTION_DETECT_ENABLED 0x85
	#define CAMERA_ATTR_IDLE_RETURN_DELAY 0x87
	#define CAMERA_ATTR_MIN_IDLE_TIME 0x88
	#define CAMERA_ATTR_CAPTURE_STILL 0x89
	#define CAMERA_ATTR_MAX_RECORDING_TIME 0x8A
	#define CAMERA_ATTR_MOTION_SENSITIVITY 0x8B

	def handle_motion_detect_enable(self, value):
		if value:
			self.start_motion_detection()
			self.settings["motion_detection"]["enabled"] = True
		else:
			self.stop_motion_detection()
			self.settings["motion_detection"]["enabled"] = False

		store_settings(self.settings)

		return int(self.settings["motion_detection"]["enabled"])

	def handle_server_message_get(self, attr_id):
		if attr_id == defs.attribute_id("GENERIC_ATTR_ENABLED"):
			pass
		elif attr_id == defs.attribute_id("CAMERA_ATTR_CAMERA_STATE"):
			return self.camera_state
		elif attr_id == defs.attribute_id("CAMERA_ATTR_MOTION_DETECT_ENABLED"):
			return int(self.settings["motion_detection"]["enabled"])
		elif attr_id == defs.attribute_id("CAMERA_ATTR_VIDEO_STREAM"):
			if self.camera_state == Camera_State.VIDEO_STREAM_ACTIVE:
				return 1
			else:
				return 0

		return 0

	def handle_server_message_set(self, attr_id, value):
		if attr_id == defs.attribute_id("CAMERA_ATTR_MOTION_DETECT_ENABLED"):
			return self.handle_motion_detect_enable(value)
		elif attr_id == defs.attribute_id("CAMERA_ATTR_VIDEO_STREAM"):

			if value:
				print("Starting video stream from server set")
				self.start_video_stream()
				return 1
			else:
				print("Stopping video stream from server set")
				self.stop_video_stream()
				return 0

		return 0

	def _process_queue(self):
		if self.queue_inbound.empty():
			return

		message = self.queue_inbound.get()

		# TODO fire notifications accordingly
		if "motion detect start" in message:
			self.camera_state = Camera_State.MOTION_DETECT_RECORDING
			print("Camera_State.MOTION_DETECT_RECORDING")
		elif "file ready" in message:
			self.camera_state = Camera_State.MOTION_DETECT_IDLE
			print("Camera_State.MOTION_DETECT_IDLE")

	def app_monitor(self):
		self._process_queue()

		if self.motion_detect_thread and not self.motion_detect_thread.is_alive():
			self.motion_detect_thread = None

			print("HERE Camera_State.INACTIVE")
			self.camera_state = Camera_State.INACTIVE

		if self.video_stream_thread and not self.video_stream_thread.is_alive():
			self.video_stream_thread = None

			print("THERE Camera_State.INACTIVE")
			self.camera_state = Camera_State.INACTIVE

		if self.motion_detect_start_pending:
			self.start_motion_detection()
		
		if self.video_stream_start_pending:
			self.start_video_stream()
	
		# TODO: REMOVE AFTER DEBUG
		if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
			c = sys.stdin.read(1)
			if c == 'm':
				print("m: starting motion detect")
				self.start_motion_detection()
			if c == 'n':
				print("n: stop detect")
				self.stop_motion_detection()
			if c == 'v':
				print("v: starting video stream")
				self.start_video_stream()
			if c == 'w':
				print("w: stop video stream")
				self.stop_video_stream()
			if c == 's':
				print("State: " + str(self.camera_state))
			if c == 't':
				print("Motion detect thread: " + str(self.motion_detect_thread))
				print("Motion detect alive: " + str(self.motion_detect_thread.is_alive() if self.motion_detect_thread else "N/A"))
				print("Video stream thread: " + str(self.video_stream_thread))
				print("Video stream alive: " + str(self.video_stream_thread.is_alive() if self.video_stream_thread else "N/A"))

	def shutdown(self):
		self.stop_motion_detection()
		self.stop_video_stream()

		if self.motion_detect_thread:
			self.motion_detect_thread.join()
		if self.video_stream_thread:
			self.video_stream_thread.join()

		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
	init_log_file("camera-main.log")

	try:
		camera_manager = Camera_Manager()

		if camera_manager.settings["motion_detection"]["enabled"]:
			camera_manager.start_motion_detection()
			print("cam manager thread", camera_manager.motion_detect_thread)

		messaging_framework = Messaging_Framework(
			server_message_get_handler = camera_manager.handle_server_message_get,
			server_message_set_handler = camera_manager.handle_server_message_set,
			app_jobs = camera_manager.app_monitor,
			max_app_interval = 0.5,
			logger = log,
		)

		messaging_framework.run()

	except KeyboardInterrupt:
		print("cam shutdown")
		camera_manager.shutdown()

	except:
		log.critical("Caught unhandled exception; device manager has crashed!", exc_info = True)
		exit(1)
