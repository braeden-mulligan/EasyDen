from . import config
import datetime, json, socket, sys, time, os

class SH_Device:
	SH_TYPE_RESERVED_1 = 0
	SH_TYPE_RESERVED_2 = 1
	SH_TYPE_RESERVED_3 = 2
	SH_TYPE_RESERVED_4 = 3
	SH_TYPE_RESERVED_5 = 4
	SH_TYPE_CAMERA = 5
	SH_TYPE_IRRIGATION = 6
	SH_TYPE_POWEROUTLET = 7
	SH_TYPE_THERMOSTAT = 8

	GENERIC_REG_NULL = 0
	GENERIC_REG_RESERVED_1 = 1
	GENERIC_REG_RESERVED_2 = 2
	GENERIC_REG_RESERVED_3 = 3
	GENERIC_REG_RESERVED_4 = 4
	GENERIC_REG_RESERVED_5 = 5
	GENERIC_REG_ENABLE = 6
	GENERIC_REG_PING = 7
	#GENERIC_REG_KEEPALIVE = 8
	GENERIC_REG_DATE = 9
	GENERIC_REG_TIME = 10
	GENERIC_REG_WEEKDAY = 11
	GENERIC_REG_SCHEDULE = 12
	GENERIC_REG_SCHEDULE_ENABLE = 13
	GENERIC_REG_SCHEDULE_COUNT = 14
	GENERIC_REG_APP_FREQUENCY = 20
	GENERIC_REG_POLL_FREQUENCY = 21
	GENERIC_REG_PUSH_ENABLE = 31
	GENERIC_REG_PUSH_FREQUENCY = 32
	GENERIC_REG_PUSH_BUFFERING = 33

	POWEROUTLET_REG_STATE = 101
	POWEROUTLET_REG_OUTLET_COUNT = 102

	THERMOSTAT_REG_TEMPERATURE = 101
	THERMOSTAT_REG_TARGET_TEMPERATURE = 102
	THERMOSTAT_REG_THRESHOLD_HIGH = 103
	THERMOSTAT_REG_THRESHOLD_LOW = 104
	THERMOSTAT_REG_HYSTERESIS = 105
	THERMOSTAT_REG_MIN_COOLDOWN = 106
	THERMOSTAT_REG_HUMIDITY = 107

	IRRIGATION_REG_MOISTURE = 101
	IRRIGATION_REG_TARGET_MOISTURE = 102
	IRRIGATION_REG_THRESHOLD_HIGH = 103
	IRRIGATION_REG_THRESHOLD_LOW = 104
	IRRIGATION_REG_HYSTERESIS = 105
	IRRIGATION_REG_MIN_COOLDOWN = 106
	IRRIGATION_REG_SWITCH_COUNTER = 107

	CMD_NUL = 0
	CMD_GET = 1
	CMD_SET = 2
	CMD_RSP = 3
	CMD_PSH = 4
	CMD_IDY = 5
	#CMD_DAT = 5

	STATUS_OK = 0
	STATUS_UNRESPONSIVE = 1
	STATUS_ERROR = 2

	def __init__(self, socket_connection = None):
		self.device_type = 0
		self.device_id = 0
		self.device_attrs = {} #(reg, val)
		self.name = ""

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

	def get_json_obj(self):
		device_obj = {}
		device_obj["device_type"] = self.device_type
		device_obj["device_id"] = self.device_id
		device_obj["online_status"] = self.online_status
		device_obj["last_contact"] = self.last_contact
		device_obj["registers"] = self.device_attrs
		return device_obj

	def update_pending(self):
		if self.pending_response:
			packet, timestamp, retries = self.pending_response 
			print("waiting on message [" + packet + "] retries remaining: " + str(retries))

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
			print("Transmitting: [" + str(p) + "] retries " + str(r))
			#try:
			#TODO: except close broken connections 
			if self.soc_connection:
				self.pending_response = (p, time.time(), r)
				self.soc_connection.send(p.encode())

		return SH_Device.STATUS_OK

	def update_attributes(self, reg, val):
		if reg == SH_Device.GENERIC_REG_NULL:
			return
		elif reg == SH_Device.GENERIC_REG_PING:
			return
		else: 
			self.device_attrs[reg] = val
		return

#TODO: improve parsing robustness
	def parse_message(self, packet_string):
		words = [int(w, 16) for w in packet_string.split(',')]

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
			if words[2] == SH_Device.GENERIC_REG_PING:
				# Already waiting on a heartbeat check.
				return
		if self.online_status:
			if time.time() > self.soc_last_heartbeat + config.DEVICE_KEEPALIVE:
				self.device_send("{:02X},{:02X},{:08X}".format(SH_Device.CMD_GET, SH_Device.GENERIC_REG_PING, 0), retries = 1)
				self.soc_last_heartbeat = time.time()


