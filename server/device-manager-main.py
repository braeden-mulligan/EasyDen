import threading
from device_manager import device_nexus
from device_manager import video_streaming

if __name__ == "__main__":
	stream_server = video_streaming.Video_Stream_Server()
	stream_thread = threading.Thread(target = stream_server.run)
	stream_thread.start()

	try:
		device_nexus.run()
	except KeyboardInterrupt:
		pass
	finally:
		stream_server.shutdown()

