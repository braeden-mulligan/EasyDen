from flask import Response,	jsonify
import socket
import threading
import queue
import subprocess
import sys

sys.path.append("..")
from common	import utils 

system_config =	utils.load_json_file("config.json")
system_settings	= utils.load_json_file("settings.json")

INTERCONNECT_PATH =	utils.get_abs_path("streaming_interconnect")
FRAMERATE =	system_settings["video_streaming"].get("framerate",	15)	
JPEG_QUALITY = 85 

class MJPEGStreamManager:
	def	__init__(self):
		self.clients = []
		self.clients_lock =	threading.Lock()
		self.connected = False
		self.ffmpeg_process	= None
		self.current_frame = None
		self.frame_lock	= threading.Lock()
		
		threading.Thread(target=self.receive_from_server, daemon=True).start()
	
	def	receive_from_server(self):
		while True:
			try:
				sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
				sock.connect(INTERCONNECT_PATH)
				print("Connected to	video server")
				self.connected = True
				
				self.ffmpeg_process	= subprocess.Popen([
					"ffmpeg",
					"-i", "pipe:0",
					"-f", "image2pipe",
					"-vcodec", "mjpeg",
					"-q:v",	str(JPEG_QUALITY),
					"-r", str(FRAMERATE), 
					"pipe:1" 
				], stdin = subprocess.PIPE,	stdout = subprocess.PIPE, stderr = subprocess.DEVNULL, bufsize = 10**8)
				
				# Thread to	feed H.264 data	to ffmpeg
				def	feed_ffmpeg():
					try:
						while True:
							data = sock.recv(8192)
							if not data:
								break
							self.ffmpeg_process.stdin.write(data)
							self.ffmpeg_process.stdin.flush()
					except:
						pass
					finally:
						try:
							self.ffmpeg_process.stdin.close()
						except:
							pass
				
				threading.Thread(target=feed_ffmpeg, daemon=True).start()
				
				while True:
					# Read frame size (JPEG	starts with	FFD8, ends with	FFD9)
					frame_data = b""
					
					while True:
						byte = self.ffmpeg_process.stdout.read(1)
						if not byte:
							raise Exception("FFmpeg	stream ended")
						if byte	== b"\xff":
							next_byte =	self.ffmpeg_process.stdout.read(1)
							if next_byte ==	b"\xd8":  #	JPEG SOI marker
								frame_data = b"\xff\xd8"
								break
					
					# Read until JPEG end marker
					while True:
						byte = self.ffmpeg_process.stdout.read(1)
						if not byte:
							raise Exception("FFmpeg	stream ended")
						frame_data += byte
						if len(frame_data) >= 2	and	frame_data[-2:]	== b"\xff\xd9":	 # JPEG	EOI	marker
							break
					
					with self.frame_lock:
						self.current_frame = frame_data
					
					with self.clients_lock:
						for	client_queue in	self.clients:
							try:
								client_queue.put_nowait(frame_data)
							except queue.Full:
								pass
			
			except Exception as	e:
				print(f"Connection error: {e}. Reconnecting	in 5 seconds...")
				self.connected = False
				if self.ffmpeg_process:
					try:
						self.ffmpeg_process.terminate()
					except:
						pass
				import time
				time.sleep(5)
	
	def	add_client(self):
		client_queue = queue.Queue(maxsize=30)
		with self.clients_lock:
			self.clients.append(client_queue)
		print(f"MJPEG client connected.	Total clients: {len(self.clients)}")
		return client_queue
	
	def	remove_client(self,	client_queue):
		with self.clients_lock:
			if client_queue	in self.clients:
				self.clients.remove(client_queue)
		print(f"MJPEG client disconnected. Total clients: {len(self.clients)}")

stream_manager = MJPEGStreamManager()

def	stream_mjpeg():
	def	generate():
		client_queue = stream_manager.add_client()
		try:
			while True:
				frame =	client_queue.get()
				yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" +	frame +	b"\r\n")
		except GeneratorExit:
			stream_manager.remove_client(client_queue)
	
	return Response(
		generate(),
		mimetype="multipart/x-mixed-replace; boundary=frame",
		headers={
			"Cache-Control": "no-cache,	no-store, must-revalidate",
			"Pragma": "no-cache",
			"Expires": "0",
			"Connection": "close"
		}
	)

# @app.route("/api/snapshot.jpg")
# def snapshot():
#	  """Get a single JPEG snapshot"""
#	  with stream_manager.frame_lock:
#		  if stream_manager.current_frame:
#			  return Response(
#				  stream_manager.current_frame,
#				  mimetype="image/jpeg",
#				  headers={"Cache-Control":	"no-cache"}
#			  )
#	  return jsonify({"error": "No frame available"}), 404

def	status():
	return jsonify({
		"connected": stream_manager.connected,
		"clients": len(stream_manager.clients)
	})

# Serve	React app (if build	exists)
# @app.route("/", defaults={"path":	""})
# @app.route("/<path:path>")
# def serve(path):
#	  if path != ""	and	os.path.exists(app.static_folder + "/" + path):
#		  return send_from_directory(app.static_folder,	path)
#	  else:
#		  return send_from_directory(app.static_folder,	"index.html")

# if __name__ == "__main__":
#	  print("Flask MJPEG app starting...")
#	  print("MJPEG stream endpoint:	http://localhost:5000/api/stream.mjpeg")
#	  print("Snapshot endpoint:	http://localhost:5000/api/snapshot.jpg")
#	  print("Status	endpoint: http://localhost:5000/api/status")
#	  app.run(host="0.0.0.0", port=5000, threaded=True)
