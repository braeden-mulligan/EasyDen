from . import config
import datetime, json, socket, sys, time, os

class SH_Device:
	TYPE_MAP = config.build_definition_mapping("SH_TYPE_")
	REGISTER_MAP = config.build_definition_mapping("_REG_")

	CMD_NUL = 0
	CMD_GET = 1
	CMD_SET = 2
	CMD_RSP = 3
	CMD_PSH = 4
	CMD_IDY = 5
	#CMD_DAT = 6

	STATUS_OK = 0
	STATUS_UNRESPONSIVE = 1
	STATUS_ERROR = 2

	def type_id(type_name):
		for t in SH_Device.TYPE_MAP:
			if (type_name == t[0]):
				return t[1]
		return None

	def type_label(type_id):
		for t in SH_Device.TYPE_MAP:
			if type_id == t[1]:
				return t[0]
		return None

	def register_id(reg_name):
		for reg in SH_Device.REGISTER_MAP:
			if reg_name == reg[0]:
				return reg[1]
		return None
	
	# Because the register mapping is not one-to-one we need device type
	# Type can be passed as either string or int
	def register_label(reg_id, device_type):
		if isinstance(device_type, int):
			device_type = SH_Device.type_label(device_type)
		if not device_type:
			return None
		type_name = device_type.removeprefix("SH_TYPE_")

		for reg_label, reg_num in SH_Device.REGISTER_MAP:
			if reg_id == reg_num:
				if "GENERIC" in reg_label or type_name in reg_label:
					return reg_label
		return None

	def __init__(self, socket_connection = None):
		self.device_type = 0
		self.device_id = 0
		self.device_attrs = {} #(reg, val)
		self.name = "Default Name"

		self.msg_timeout = 3.0
		self.msg_retries = 1
		self.msg_seq = 1

		self.soc_connection = None
		self.soc_fd = None
		self.soc_heartbeat = config.DEVICE_KEEPALIVE
		self.soc_last_heartbeat = None
		self.online_status = False 
		self.last_contact = None
		self.reconnect_count = -1
		self.fully_initialized = False

# pending response triple of (packet_string, timeout, retry_count) 
		self.pending_response = None
# pending send list of double of (packet_string, retry_count) 
		self.pending_send = []
		self.max_pending_messages = 3
		self.no_response = 0

		self.connect(socket_connection)
		self.update_last_contact()
		return

	def update_last_contact(self):
		self.last_contact = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
		self.soc_last_heartbeat = time.time()
		self.no_response = 0
		return

	def get_obj_json(self):
		device_obj = {}
		device_obj["type"] = self.device_type
		device_obj["id"] = self.device_id
		device_obj["name"] = self.name
		device_obj["online"] = self.online_status
		device_obj["registers"] = self.device_attrs
		return device_obj

	def update_pending(self):
		if self.pending_response:
			packet, timestamp, retries = self.pending_response 
			#print("waiting on message [" + packet + "] retries remaining: " + str(retries))

			if time.time() > timestamp + self.msg_timeout:
				self.pending_response = None
				if retries > 0:
					print("Message [" + packet + "] deilvery failed, retrying " + str(retries) + " more times...")
					self.device_send(None, retries - 1, packet) 
				else:
					print("Message [" + packet + "] deilvery failed.")
					self.no_response += 1
					return SH_Device.STATUS_UNRESPONSIVE

		elif self.pending_send:
			p, r = self.pending_send.pop(0)
			print("Transmitting: [" + str(p) + "] retries " + str(r) + "...")
			#try:
			#TODO: except close broken connections 
			if self.soc_connection:
				self.pending_response = (p, time.time(), r)
				self.soc_connection.send(p.encode())

		return SH_Device.STATUS_OK

	def update_attributes(self, reg, val):
		if reg == SH_Device.register_id("GENERIC_REG_NULL"):
			return
		elif reg == SH_Device.register_id("GENERIC_REG_PING"):
			return
		else: 
			self.device_attrs[reg] = val
		return

#TODO: improve parsing robustness
	def parse_message(self, packet_string):
		print("DEVICE PARSEING " + packet_string)
		words = [int(w, 16) for w in packet_string.split(',')]
		print("WORDS " + str(words[0]) + " " + str(words[1]) + " " + str(words[2]) + " " + str(words[3]))

		prev_msg_cmd = None
		prev_words = None

		if self.pending_response:
			prev_words = [int(w, 16) for w in self.pending_response[0].split(',')]
			if prev_words[0] == words[0]:
				self.pending_response = None
				prev_msg_cmd = prev_words[1]

		# Check this to avoid sending diplicate messages.
		elif self.pending_send:
			print("No pending_response, checking send queue.")
			for entry in self.pending_send:
				prev_words = [int(w, 16) for w in entry[0].split(',')]
				if prev_words[0] == words[0]:
					print("Found in send queue. Waiting transmission removed.")
					self.pending_send.remove(entry)
					prev_msg_cmd = prev_words[1]

		else:
			print("parse_message() error. Recv does not correspond to anything pending.")
			return None

		if words[1] == SH_Device.CMD_RSP and prev_msg_cmd == SH_Device.CMD_GET:
			self.update_attributes(words[2], words[3])

		elif words[1] == SH_Device.CMD_RSP and prev_msg_cmd == SH_Device.CMD_SET: 
			self.update_attributes(prev_words[2], prev_words[3])
			#TODO: confirm success or failure to inform web app?

		elif words[1] == SH_Device.CMD_IDY:
			self.device_type = words[2]
			self.device_id = words[3]
			return self.device_id

		return None

	def device_send(self, message, retries = -1, raw_packet= None):
		r = retries 
		if r < 0:
			r = self.msg_retries

		if self.soc_connection is not None:
			m = raw_packet or "{:04X},".format(self.msg_seq) + message
			if raw_packet is None:
				self.msg_seq += 1
				if self.msg_seq >= 65535:
					self.msg_seq = 1;

			print("Device " + str(self.device_id) + " submit: [" + m + "] retries = " + str(r))

			if len(self.pending_send) >= self.max_pending_messages:
				print("Device send buffer full")
				return False
					
			self.pending_send.append((m, r))
			print("Pending send: " + str(self.pending_send))

			return True 
		return False

	def device_recv(self):
		if self.soc_connection is not None:
			#try: except
			msg = self.soc_connection.recv(32).decode()
			print("Device " + str(self.device_id) + " recv: [" + msg + "]")

			self.update_last_contact()

			return self.parse_message(msg)
		return None

	def disconnect(self):
		self.online_status = False
		self.soc_connection = None
		self.soc_fd = None
		return

	def connect(self, soc_conn):
		self.soc_connection = soc_conn
		if soc_conn is not None:
			self.soc_fd = self.soc_connection.fileno()
			self.online_status = True
			self.no_response = 0
			self.reconnect_count += 1
		return 

	def check_heartbeat(self):
		if self.pending_response:
			words = [int(w, 16) for w in self.pending_response[0].split(',')]
			if words[2] == SH_Device.register_id("GENERIC_REG_PING"):
				# Already waiting on a heartbeat check.
				return
		if self.online_status:
			if time.time() > self.soc_last_heartbeat + config.DEVICE_KEEPALIVE:
				self.device_send("{:02X},{:02X},{:08X}".format(SH_Device.CMD_GET, SH_Device.register_id("GENERIC_REG_PING"), 0), retries = 1)
				self.soc_last_heartbeat = time.time()

	def initialization_task(self):
		if self.fully_initialized or not self.device_id or self.pending_response:
			return self.fully_initialized

		necessary_attributes = []
		if self.device_type == SH_Device.type_id("SH_TYPE_POWEROUTLET"):
			necessary_attributes = [SH_Device.register_id("POWEROUTLET_REG_SOCKET_COUNT"), SH_Device.register_id("POWEROUTLET_REG_STATE")]
		elif self.device_type == SH_Device.type_id("SH_TYPE_THERMOSTAT"):
			pass
		else:
			return self.fully_initialized

		self.fully_initialized = True
		for reg in necessary_attributes:
			if reg not in self.device_attrs:
				self.fully_initialized = False
				self.device_send("{:02X},{:02X},{:08X}".format(SH_Device.CMD_GET, reg, 0), retries = 1)
		return self.fully_initialized

