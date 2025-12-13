import socket, time
from picamera2.outputs import PyavOutput

class Video_Streamer:
	# TODO: put this in global config to sync with server
	FRAMERATE = 15

	def __init__(self, picam2, encoder, config, settings, queue_inbound, queue_oubound):
		self.picam2 = picam2
		self.encoder = encoder
		self.config = config
		self.settings = settings
		self.queue_inbound = queue_inbound
		self.queue_outbound = queue_oubound

	def run(self):
		self.picam2.stop_recording()
		self.picam2.configure(self.config)
		self.picam2.set_controls({"FrameRate": self.FRAMERATE})  
		soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			soc.connect(self.config["server_address"])
			# TODO: ID confirmation handshake 

			output = PyavOutput(soc.makefile("wb"), format = "h264")

			self.picam2.start_recording(self.encoder, output)

			while True:
				if not self.queue_inbound.empty():
					if self.queue_inbound.get(block = False) == "halt":
						break

				time.sleep(0.5)
				
			soc.shutdown(socket.SHUT_RDWR)

		finally:
			self.picam2.stop_recording()
			soc.close()

