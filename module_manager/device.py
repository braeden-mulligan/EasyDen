import config
from socket_util import socket_error
import json, select, socket, sys, time, os

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
	GENERIC_REG_ENABLE = 1
	GENERIC_REG_PING = 2
	GENERIC_REG_KEEPALIVE = 3
	GENERIC_REG_DATE = 4
	GENERIC_REG_TIME = 5
	GENERIC_REG_WEEKDAY = 6
	GENERIC_REG_SCHEDULE = 7
	GENERIC_REG_SCHEDULE_ENABLE = 8
	GENERIC_REG_SCHEDULE_COUNT = 9
	GENERIC_REG_APP_FREQUENCY = 20
	GENERIC_REG_POLL_FREQUENCY = 21
	GENERIC_REG_PUSH_ENABLE = 31
	GENERIC_REG_PUSH_FREQUENCY = 32
	GENERIC_REG_PUSH_BUFFERING = 33

	POWEROUTLET_REG_STATE = 101
	POWEROUTLET_REG_OUTLET_COUNT = 102

	THERMOSTAT_REG_TEMPERATURE = 201
	THERMOSTAT_REG_TARGET_TEMPERATURE = 202
	THERMOSTAT_REG_THRESHOLD_HIGH = 203
	THERMOSTAT_REG_THRESHOLD_LOW = 204
	THERMOSTAT_REG_HYSTERESIS = 205
	THERMOSTAT_REG_MIN_COOLDOWN = 206
	THERMOSTAT_REG_HUMIDITY = 207

	IRRIGATION_REG_MOISTURE = 301
	IRRIGATION_REG_TARGET_MOISTURE = 302
	IRRIGATION_REG_THRESHOLD_HIGH = 303
	IRRIGATION_REG_THRESHOLD_LOW = 304
	IRRIGATION_REG_HYSTERESIS = 305
	IRRIGATION_REG_MIN_COOLDOWN = 306
	IRRIGATION_REG_SWITCH_COUNTER = 307

	CMD_NUL = 0
	CMD_GET = 1
	CMD_SET = 2
	CMD_RSP = 3
	CMD_PSH = 4
	CMD_IDY = 5
	#CMD_DAT = 5

	def __init__(self, socket_connection = None, poll_obj = None):
		self.device_type = 0
		self.device_id = 0
		self.online_status = False 

#TODO: remove assigned debug value
		self.device_attrs = {} #(reg, val)

		self.msg_timeout = 2.0
		self.msg_retries = 1
		self.msg_seq = 1

		self.poll_obj = poll_obj
		self.soc_connection = None
		self.soc_fd = None
		self.soc_keepalive = config.DEVICE_KEEPALIVE
		self.soc_last_keepalive = time.time()
# List of triples (message_string, timeout, retry_count) 
		self.pending_response = []

		self.connect(socket_connection)
		return

	def get_json_obj(self):
		device_obj = {}
		device_obj["device_type"] = self.device_type
		device_obj["device_id"] = self.device_id
		device_obj["online_status"] = self.online_status
		device_obj["registers"] = self.device_attrs
		return device_obj

	def update_pending(self):
		print("UPDATE_PENDING")
		
		for entry in self.pending_response:
			message, timestamp, retries = entry
			print("check entry [" + message + "] @ " + str(time.time()) + ", retries " + str(retries) + ": [" + str(message) + "]. Timestamp: " + str(timestamp))
			if time.time() > timestamp + self.msg_timeout:
				print("Pending before: " + str(self.pending_response))
				self.pending_response.remove(entry)
				print("Pending after: " + str(self.pending_response))
				if retries > 0:
					print("Message [" + message + "] deilvery failed, retrying " + str(retries) + " more times...")
					self.device_send(0, 0, 0, retries - 1, message) 
				else:
					self.disconnect()
					print("Message [" + message + "] deilvery failed.")
		return 

#TODO: debug version
	def update_attributes(self, reg, val):
		self.device_attrs[reg] = val
		return

#TODO: improve parsing
	def parse_message(self, message_str):
		words = [int(w, 16) for w in message_str.split(',')]

		prev_msg_cmd = None
		prev_words = None
		for entry in self.pending_response:
			prev_words = [int(w, 16) for w in entry[0].split(',')]
			if prev_words[0] == words[0]:
				self.pending_response.remove(entry)
				prev_msg_cmd = prev_words[1]

		if words[1] == SH_Device.CMD_RSP and prev_msg_cmd == SH_Device.CMD_GET:
			self.update_attributes(words[2], words[3])
		elif words[1] == SH_Device.CMD_RSP and prev_msg_cmd == SH_Device.CMD_SET: 
			self.update_attributes(prev_words[2], prev_words[3])
			#confirm success or failure to inform web app?
#TODO 
			pass
		elif words[1] == SH_Device.CMD_IDY:
			self.device_type = words[2]
			self.device_id = words[3]
			return self.device_id

		return None

#TODO: introduce delays for ESP to process?
#TODO: use queue?
	def device_send(self, cmd, reg, val, retries = -1, raw_msg = None):
		r = retries 
		if r < 0:
			r = self.msg_retries
		if self.soc_connection is not None:
			m = raw_msg or "{:04X},{:02X},{:02X},{:08X}".format(self.msg_seq, cmd, reg, val)
			print("Device " + str(self.device_id) + " send: [" + m + "] retries = " + str(r))

			self.pending_response.append((m, time.time(), r))
			#try:
			#TODO: except close broken connections 
			if self.soc_connection:
				self.soc_connection.send(m.encode())

			if raw_msg is None:
#TODO: wrap msg_seq, limited to 16 bits
				self.msg_seq += 1
			return True 
		return False

	def device_recv(self):
		if self.soc_connection is not None:
			#try: except
			msg = self.soc_connection.recv(32).decode()
			print("Device " + str(self.device_id) + " recv: [" + msg + "]")

			self.soc_last_keepalive = time.time()

			return self.parse_message(msg)
		return None

	def disconnect(self):
		socket_error(self.soc_connection, select.POLLERR, self.poll_obj)
		self.online_status = False
		self.soc_connection = None
		self.soc_fd = None
		return

	def connect(self, soc_conn):
		self.soc_connection = soc_conn
		if soc_conn is not None:
			self.soc_fd = self.soc_connection.fileno()
			self.online_status = True
		return 

	def check_keepalive(self):
		for entry in self.pending_response:
			words = [int(w, 16) for w in entry[0].split(',')]
			if words[2] == SH_Device.GENERIC_REG_PING:
				# Already checking keepalive.
				return
		if self.online_status:
			if time.time() > self.soc_last_keepalive + config.DEVICE_KEEPALIVE:
				self.device_send(SH_Device.CMD_GET, SH_Device.GENERIC_REG_PING, 0, retries = 1)


