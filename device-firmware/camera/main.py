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

class Camera_State:
	INACTIVE = 0
	MOTION_DETECT_IDLE = 1
	MOTION_DETECT_START_PENDING = 2
	MOTION_DETECT_RECORDING = 4
	MOTION_DETECT_SHUTTING_DOWN = 8
	STREAMING_ACTIVE = 16
	UNHANDLED_ERROR = 32

class Camera_Manager:
	def __init__(self):
		self.picam2 = Picamera2()
		self.camera_state = Camera_State.INACTIVE
		self.settings = utils.load_json_file("settings.json")

		self.low_res_size = (320, 240)
		self.high_res_size = (1920, 1080)
		self.motion_detect_config = self.picam2.create_video_configuration(
			main = { "size": self.high_res_size, "format": "RGB888" },
			lores = { "size": self.low_res_size, "format": "YUV420" }
		)
		# self.streaming_config = self.picam2.create_video_configuration
		self.encoder = H264Encoder(repeat = True)

		self.motion_detect_thread = None
		self.streaming_thread = None

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

		self.motion_detect_start_pending = False
	
	def start_motion_detection(self):
		if self.motion_detect_thread is None:
			self.motion_detect_thread = threading.Thread(target = self.motion_detector.run)
			self.motion_detect_thread.start()
			self.camera_state = Camera_State.MOTION_DETECT_IDLE
			print("Camera_State.MOTION_DETECT_IDLE")
			self.motion_detect_start_pending = False
		else:
			self.camera_state = Camera_State.MOTION_DETECT_START_PENDING

			if not self.camera_state == Camera_State.MOTION_DETECT_START_PENDING:
				print("Camera_State.MOTION_DETECT_START_PENDING")

			self.motion_detect_start_pending = True

	def stop_motion_detection(self):
		self.motion_detect_start_pending = False

		if self.motion_detect_thread is not None:
			if not self.motion_detect_thread.is_alive():
				self.motion_detect_thread = None
				self.camera_state = Camera_State.INACTIVE
				print("Camera_State.INACTIVE")
			else:
				self.queue_outbound.put("halt", block = False)
				self.camera_state = Camera_State.MOTION_DETECT_SHUTTING_DOWN
				print("Camera_State.MOTION_DETECT_SHUTTING_DOWN")
		else:
			self.camera_state = Camera_State.INACTIVE
			print("Camera_State.INACTIVE")

	def start_stream(self):
		pass

	def stop_stream(self):
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

		return self.camera_state

	def handle_server_message_get(self, attr_id):
		if attr_id == defs.attribute_id("CAMERA_ATTR_CAMERA_STATE"):
			return self.camera_state
		elif attr_id == defs.attribute_id("CAMERA_ATTR_MOTION_DETECT_ENABLED"):
			return int(self.settings["motion_detect"]["enabled"])

		return 0

	def handle_server_message_set(self, attr_id, value):
		if attr_id == defs.attribute_id("CAMERA_ATTR_MOTION_DETECT_ENABLED"):
			return self.handle_motion_detect_enable(value)

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

			print("Camera_State.INACTIVE")
			self.camera_state = Camera_State.INACTIVE

		if self.motion_detect_start_pending:
			self.start_motion_detection()
	
		# TODO: REMOVE AFTER DEBUG
		if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
			c = sys.stdin.read(1)
			if c == 'q':
				print("q: starting motion detect")
				self.start_motion_detection()
			if c == 'p':
				print("p: stop detect")
				self.stop_motion_detection()

	def shutdown(self):
		self.stop_motion_detection()
		if self.motion_detect_thread:
			self.motion_detect_thread.join()

		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
	init_log_file("camera-main.log")

	try:
		camera_manager = Camera_Manager()

		if camera_manager.settings["motion_detection"]["enabled"]:
			camera_manager.start_motion_detection()

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
		# send_email("Device manager has crashed! Check logs for details.", subject="EasyDen Critical Error")
		exit(1)
