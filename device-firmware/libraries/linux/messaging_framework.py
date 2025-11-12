import select, socket, sys, time, os

file_location = os.path.dirname(os.path.realpath(__file__))
root_path = file_location + "/../../.."
sys.path.append(root_path)

from .protocol import AttrPacket, parse_attr_packet, format_attr_packet
from common import device_definitions as defs
from common.utils import load_json_file

class Messaging_Framework:
	poll_opts = select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL

	def __init__(self, 
	  server_message_get_handler = lambda *args: 0, 
	  server_message_set_handler = lambda *args: 0, 
	  app_jobs = lambda: None,
	  logger = None,
	  reconnect_delay = 30,
	  poll_timeout = 30000,
	  max_app_interval = 1
	):
		self.socket = None
		self.connected = False

		self._message_get_handler = server_message_get_handler
		self._message_set_handler = server_message_set_handler
		self._app_jobs = app_jobs

		self.poller = select.poll()

		self.logger = logger
		self.reconnect_delay = reconnect_delay
		self.poll_timeout = poll_timeout
		self.max_app_interval = max_app_interval
		self.metadata = load_json_file("device_metadata.json")
		self.config = load_json_file("config.json")
	
	def _establish_connection(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.poller.register(self.socket, self.poll_opts)

		try:
			self.socket.setblocking(True)
			self.socket.connect((self.config["server_address"][self.config["environment"]], self.config["server_address"]["device_connection_port"]))
			self.socket.setblocking(False)
			self.connected = True
			return True

		except Exception as e:
			self.logger and self.logger.info("Connection attempt failed.", exc_info = True)
			return False
	
	def _close_connection(self):
		try:
			self.connected = False
			self.poller.unregister(self.socket.fileno())
			self.socket.shutdown(socket.SHUT_RDWR)
			self.socket.close()
			return True

		except:
			self.logger and self.logger.info("Exception trying to close socket.", exc_info = True)
			return False

	def _socket_recv(self):
		if self.connected:
			try:
				msg = self.socket.recv(2048).decode()
				if msg == "":
					self._close_connection()
					self.logger and self.logger.info("Socket closed by server.")
					return False
				self.logger and self.logger.info("Received message from server: " + msg)
				return msg
				
			except Exception as e:
				self.logger and self.logger.info("Socket recv failed.", exc_info = True)
				return False

		return None

	def _socket_send(self, message):
		if self.connected:
			try:
				self.socket.send(message.encode())
				return True 

			except Exception as e:
				self.logger and self.logger.info("Socket send failed.", exc_info = True)
				return False

		return None
	
	def _process_server_message(self, packet):
		if not packet:
			self.logger and self.logger.info("No packet to process.")
			return ""

		message = parse_attr_packet(packet)

		response = AttrPacket(
			seq = message.seq,
			cmd = defs.Device_Protocol.CMD_RSP,
			attr = message.attr,
			val = 0 
		)

		if not response:
			self.logger and self.logger.info("Failed to parse packet.")
			return ""

		if (message.cmd == defs.Device_Protocol.CMD_GET):
			response.val = self._message_get_handler(message.attr)

		elif (message.cmd == defs.Device_Protocol.CMD_SET):
			response.val = self._message_set_handler(message.attr, message.val)

		elif (message.cmd == defs.Device_Protocol.CMD_IDY):
			response.cmd = defs.Device_Protocol.CMD_IDY
			response.attr = self.metadata["type"]
			response.val = self.metadata["id"]

		else:
			self.logger and self.logger.info("Unknown message received: " + packet)
			return ""

		return format_attr_packet(response)

	def _main_loop(self):
		self._app_jobs()

		if not self.connected and not self._establish_connection():
			time.sleep(min(self.reconnect_delay, self.max_app_interval))
			return

		poll_result = self.poller.poll(min(self.poll_timeout, self.max_app_interval * 1000))

		socket_problem = select.POLLNVAL | select.POLLERR | select.POLLHUP

		for fd, event in poll_result:
			if event & socket_problem:
				self._close_connection()
				return
			elif event & select.POLLIN:
				message = self._socket_recv()
				if not message:
					return

				response = self._process_server_message(message)
				if response:
					self._socket_send(response)	

	def run(self):
		try:
			while True:
				self._main_loop()
		except KeyboardInterrupt:
			self._close_connection()
			self.logger and self.logger.info("Messaging framework stopped by user.")
			raise
		except:
			self.logger and self.logger.critical("Messaging framework crashed!", exc_info = True)
			# if emailer:
			# 	emailer.send_crash_report("Messaging framework crashed!", e)
