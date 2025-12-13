import socket
import threading
import time
import os, sys
import subprocess
from datetime import datetime
sys.path.append("../..")
from common	import utils

system_config =	utils.load_json_file("config.json")
system_settings	= utils.load_json_file("settings.json")

VIDEO_STREAMING_PORT = system_config["server_address"]["video_stream_port"]
INTERCONNECT_PATH =	utils.get_abs_path("streaming_interconnect")
VIDEO_RECORDINGS_DIR = utils.get_abs_path("video_recordings")
SEGMENT_DURATION = system_settings["video_streaming"].get("recording_max_duration",	900) 
FRAMERATE =	system_settings["video_streaming"].get("framerate",	15)	

# TODO: genericize for audio
# TODO: clean up, error handling, logging, etc.
# TODO: Device ID handshake and multi-device support

class Video_Stream_Server:
	def	__init__(self):
		self.current_file =	None
		self.current_h264_file = None
		self.segment_start_time	= None
		self.video_writer =	None
		self.ffmpeg_process	= None
		self.dashboard_clients = []
		self.dashboard_lock	= threading.Lock()
		self.graceful_shutdown = False
		
		os.makedirs(VIDEO_RECORDINGS_DIR, exist_ok = True)
		
		if os.path.exists(INTERCONNECT_PATH):
			os.remove(INTERCONNECT_PATH)
		
		self.dashboard_interconnect	= socket.socket(socket.AF_UNIX,	socket.SOCK_STREAM)
		self.dashboard_interconnect.bind(INTERCONNECT_PATH)
		self.dashboard_interconnect.settimeout(2)
		self.dashboard_interconnect.listen()

		self.video_source = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.video_source.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.video_source.bind(("0.0.0.0", VIDEO_STREAMING_PORT))
		self.video_source.settimeout(2)
		self.video_source.listen(1)
	
	def	get_segment_filename(self):
		timestamp =	datetime.now().strftime("%Y%m%d_%H%M%S")
		h264_file =	os.path.join(VIDEO_RECORDINGS_DIR, f"video_{timestamp}.h264")
		mp4_file = os.path.join(VIDEO_RECORDINGS_DIR, f"video_{timestamp}.mp4")
		return h264_file, mp4_file
	
	def	convert_to_mp4(self, h264_file,	mp4_file):
		try:
			print(f"Converting {h264_file} to MP4...")
			subprocess.run([
				'ffmpeg', '-y', '-r',
				'-i', h264_file,
				'-c:v',	'copy',	
				'-movflags', '+faststart',
				mp4_file
			], check = True, capture_output = True)
			
			os.remove(h264_file)
			print(f"Conversion complete: {mp4_file}")
		except subprocess.CalledProcessError as	e:
			print(f"Error converting to	MP4: {e}")
			print(f"stderr:	{e.stderr.decode()}")
			print(f"Keeping	H.264 file:	{h264_file}")
		except Exception as	e:
			print(f"Error during conversion: {e}")
	
	def	rotate_segment(self):
		if self.video_writer:
			self.video_writer.close()
			print(f"Closed segment:	{self.current_h264_file}")
			
			h264_file =	self.current_h264_file
			mp4_file = self.current_file
			threading.Thread(target = self.convert_to_mp4, args = (h264_file, mp4_file), daemon = True).start()
		
		self.current_h264_file,	self.current_file =	self.get_segment_filename()
		self.video_writer =	open(self.current_h264_file, 'wb')
		self.segment_start_time	= time.time()
		print(f"Started	new	segment: {self.current_h264_file}")

	def	broadcast_to_dashboard(self, data):
		with self.dashboard_lock:
			dead_clients = []
			for	client in self.dashboard_clients:
				if self.graceful_shutdown:
					return

				try:
					client.sendall(data)
				except socket.timeout:
					continue
				except Exception as e:
					dead_clients.append(client)
			
			for	client in dead_clients:
				self.dashboard_clients.remove(client)
				try:
					client.close()
				except Exception as e:
					print(f"Error closing dead client socket: {e}")
	
	
	def	handle_camera_stream(self, conn):
		try:
			self.rotate_segment()

			while True:
				if self.graceful_shutdown:
					return
			
				try:
					data = conn.recv(8192)
				except socket.timeout:
					continue
				if not data:
					break
				
				self.video_writer.write(data)
				self.broadcast_to_dashboard(data)
				
				if time.time() - self.segment_start_time >=	SEGMENT_DURATION:
					self.rotate_segment()
		
		except Exception as	e:
			print(f"Error handling stream: {e}")
		
		finally:
			if self.video_writer:
				self.video_writer.close()
			conn.close()
			self.rotate_segment()
			print("Camera disconnected")
	
	def	wait_dashboard_clients(self):
		while True:
			if self.graceful_shutdown:
				return	
			try:
				client,	_ =	self.dashboard_interconnect.accept()
				with self.dashboard_lock:
					self.dashboard_clients.append(client)
				print(f"Dashboard client connected.	Total clients: {len(self.dashboard_clients)}")
			except socket.timeout:
				continue
			except Exception as	e:
				print(f"Error accepting	Dashboard client: {e}")
	
	def	run(self):
		dashboard_thread = threading.Thread(target = self.wait_dashboard_clients)
		dashboard_thread.start()

		while True:
			if self.graceful_shutdown:
				break
			try:
				conn, addr = self.video_source.accept()
				print(f"Connection from	{addr}")
			except socket.timeout:
				continue

			self.handle_camera_stream(conn)

		dashboard_thread.join()

		try: 
			self.video_source.close()
		except Exception as e:
			print(f"Error closing server sockets: {e}")

		with self.dashboard_lock:
			for client in self.dashboard_clients:
				try:
					client.close()
				except Exception as e:
					print(f"Error closing client socket: {e}")

	def shutdown(self):
		self.graceful_shutdown = True
	

if __name__	== '__main__':
	server = Video_Stream_Server()

	try:
		server.run()
	except KeyboardInterrupt:
		print("Shutting down video server...")
	except Exception as e:
		print(f"Unhandled exception in video server: {e}")
	finally:
		server.shutdown()
