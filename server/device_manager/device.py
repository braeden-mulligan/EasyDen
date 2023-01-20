from device_manager import config
from device_manager import device_definitions as SH_defs
from device_manager import messaging_interchange as messaging
from device_manager import utilities as utils
import copy, datetime, json, socket, sys, time, os

class SH_Device:
	STATUS_OK = 0
	STATUS_UNRESPONSIVE = 1
	STATUS_ERROR = 2

	MAX_SEQUENCE_NUM = 32767
	MAX_TX_RETRIES = 1
	TX_TIMEOUT = 3.0
	TX_BUFFER_SIZE = 128

	def __init__(self, socket_connection = None):
		# Attributes returned on device query.
		self.device_type = 0
		self.device_id = 0
		self.device_attrs = {} #(reg, {value, queried_at, updated_at})
		self.name = "Default Name"
		self.online_status = False 
		self.fully_initialized = False

		# Attributes available for info query
		self.last_contact = None
		self.reconnect_count = -1 # For debugging

		self.msg_timeout = SH_Device.TX_TIMEOUT
		self.msg_retries = SH_Device.MAX_TX_RETRIES
		self.msg_seq = 1
		self.soc_connection = None
		self.soc_fd = None
		self.soc_heartbeat = config.DEVICE_KEEPALIVE
		self.soc_last_heartbeat = None
# pending response triple of (packet_string, timeout, retry_count) 
		self.pending_response = None
# pending send list of double of (packet_string, retry_count) 
		self.pending_transmission = []
		self.max_pending_messages = SH_Device.TX_BUFFER_SIZE
		self.no_response = 0

		self.connect(socket_connection)
		self.update_last_contact()
		return

	def update_last_contact(self):
		self.last_contact = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
		self.soc_last_heartbeat = time.monotonic()
		self.no_response = 0
		return

	def get_data(self):
		device_obj = {}
		device_obj["type"] = self.device_type
		device_obj["id"] = self.device_id
		device_obj["name"] = self.name
		device_obj["online"] = self.online_status
		device_obj["initialized"] = self.fully_initialized
		device_obj["registers"] = copy.deepcopy(self.device_attrs)
		return device_obj

	def update_pending(self):
		if self.pending_response:
			packet, timestamp, retries = self.pending_response 
			#print("waiting on message [" + packet + "] retries remaining: " + str(retries))

			if time.monotonic() > timestamp + self.msg_timeout:
				self.pending_response = None
				if retries > 0:
					print("Message [" + packet + "] deilvery failed, retrying " + str(retries) + " more times...")
					self.device_send(None, retries - 1, packet) 
				else:
					print("Message [" + packet + "] deilvery failed.")
					self.no_response += 1
					return SH_Device.STATUS_UNRESPONSIVE

		elif self.pending_transmission:
			p, r = self.pending_transmission.pop(0)
			if self.soc_connection:
				print("Transmitting: [" + str(p) + "] to device " + str(self.device_id) + ". " + str(r) + " retries available...")
				self.pending_response = (p, time.monotonic(), r)
				self.soc_connection.send(p.encode())

		return SH_Device.STATUS_OK

	def update_attributes(self, reg, val, query = False, update = False):
		if reg == SH_defs.register_id("GENERIC_REG_NULL"):
			return
		elif reg == SH_defs.register_id("GENERIC_REG_PING"):
			return
		else: 
			attribute = {
			  "value": val,
			  "queried_at": round(time.monotonic(), 5) if query else 0.0,
			  "updated_at": round(time.monotonic(), 5) if update else 0.0
			}

			self.device_attrs[reg] = self.device_attrs.get(reg, attribute)

			if query:
				self.device_attrs[reg]["queried_at"] = attribute["queried_at"]
			elif update:
				self.device_attrs[reg]["value"] = attribute["value"]
				self.device_attrs[reg]["updated_at"] = attribute["updated_at"]
				
		return

	def parse_packet(self, packet):
		try:
			words = [int(w, 16) for w in packet.split(',')]
		except Exception as e:
			utils.print_exception(e)
			return None

		if len(words) != 4:
			return None

		return words

	def process_message(self, packet):
		try:
			msg_seq, msg_cmd, msg_reg, msg_val = self.parse_packet(packet)
		except TypeError:
#TODO: log frequency of malformed packets?
			print("Failed to parse packet [" + str(packet) + "]!")
			return None
		
		sent_seq = sent_cmd = sent_reg = sent_val = None

		if self.pending_response:
			sent_seq, sent_cmd, sent_reg, sent_val = self.parse_packet(self.pending_response[0])
			if msg_seq == sent_seq:
				self.pending_response = None

		# Check this to avoid sending obselete duplicate requests.
		# TODO: Further investigate conditions this would occur... 
		#   pending response cleared after timeout -> duplicate request gets queued to send -> device responds before request is re-sent?
		elif self.pending_transmission:
			print("No pending_response, checking send queue.")
			for entry in self.pending_transmission:
				sent_seq, sent_cmd, sent_reg, sent_val = self.parse_packet(entry[0])
				if msg_seq == sent_seq:
					print("Found in send queue. Message awaiting transmission removed.")
					self.pending_transmission.remove(entry)

		else:
			print("process_message error. Received packet does not correspond to any pending messages.")
			return None

		if msg_cmd == SH_defs.CMD_RSP and sent_cmd == SH_defs.CMD_GET:
			self.update_attributes(msg_reg, msg_val, update = True)

		elif msg_cmd == SH_defs.CMD_RSP and sent_cmd == SH_defs.CMD_SET: 
			self.update_attributes(sent_reg, msg_val, update = True)

		elif msg_cmd == SH_defs.CMD_IDY:
			self.device_type = msg_reg
			self.device_id = msg_val
			return self.device_id

		return 0

	def device_recv(self):
		if self.soc_connection is not None:
			try:
				# This should always return bytes because we use i/o poll mechanism.
				msg = self.soc_connection.recv(32).decode()
			except Exception as e:
				utils.print_exception(e)
				return -1

			print("Received [" + msg + "] from device: " + str(self.device_id))

			self.update_last_contact()
			
			recv_result = self.process_message(msg)
			if recv_result is None:
				return -2
			return recv_result
		return 0

	def device_send(self, message, retries = -1, raw_packet = None):
		m = raw_packet or "{:04X},".format(self.msg_seq) + message

		if retries < 0:
			retries = self.msg_retries

			# Only update query timestamp if message is original, not a re-try
			_, cmd, reg, val = self.parse_packet(m)
			if cmd == SH_defs.CMD_GET or cmd == SH_defs.CMD_SET:
				self.update_attributes(reg, val, query = True)

		if self.soc_connection is None:
			return False

		if raw_packet is None:
			self.msg_seq += 1
			if self.msg_seq >= SH_Device.MAX_SEQUENCE_NUM:
				self.msg_seq = 1;

		print("\nSubmit: [" + m + "] (retries = " + str(retries) + ") to device " + str(self.device_id))

		if len(self.pending_transmission) >= self.max_pending_messages:
			print("Device send buffer full")
			return False
				
		# Tag device id for logging.
		self.pending_transmission.append((m, retries))
		print("Pending transmissions for device " + str(self.device_id) +": " + str(self.pending_transmission))

		return True 

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
			self.update_last_contact()
		return 

	def check_heartbeat(self):
		if self.pending_response:
			_, _, pending_reg, _ = self.parse_packet(self.pending_response[0])
			
			if pending_reg == SH_defs.register_id("GENERIC_REG_PING"):
				# Already waiting on a heartbeat check.
				return
		if self.online_status and (time.monotonic() > self.soc_last_heartbeat + config.DEVICE_KEEPALIVE):
			self.device_send(messaging.generic_ping())
			self.soc_last_heartbeat = time.monotonic()

	def initialization_task(self):
		if self.fully_initialized:
			return True
		if not self.device_id or self.pending_response:
			return False

		necessary_attributes = [
			SH_defs.register_id("GENERIC_REG_ENABLE")
		]

		if self.device_type == SH_defs.type_id("SH_TYPE_POWEROUTLET"):
			necessary_attributes.append(SH_defs.register_id("POWEROUTLET_REG_SOCKET_COUNT"))
			necessary_attributes.append(SH_defs.register_id("POWEROUTLET_REG_STATE"))

		elif self.device_type == SH_defs.type_id("SH_TYPE_THERMOSTAT"):
			necessary_attributes.append(SH_defs.register_id("THERMOSTAT_REG_TEMPERATURE"))
			necessary_attributes.append(SH_defs.register_id("THERMOSTAT_REG_TARGET_TEMPERATURE"))
			necessary_attributes.append(SH_defs.register_id("THERMOSTAT_REG_TEMPERATURE_CORRECTION"))
			necessary_attributes.append(SH_defs.register_id("THERMOSTAT_REG_THRESHOLD_HIGH"))
			necessary_attributes.append(SH_defs.register_id("THERMOSTAT_REG_THRESHOLD_LOW"))
			necessary_attributes.append(SH_defs.register_id("THERMOSTAT_REG_MAX_HEAT_TIME"))
			necessary_attributes.append(SH_defs.register_id("THERMOSTAT_REG_MIN_COOLDOWN_TIME"))
			necessary_attributes.append(SH_defs.register_id("THERMOSTAT_REG_HUMIDITY_SENSOR_COUNT"))

		elif self.device_type == SH_defs.type_id("SH_TYPE_IRRIGATION"):
			necessary_attributes.append(SH_defs.register_id("IRRIGATION_REG_SENSOR_COUNT"))
			necessary_attributes.append(SH_defs.register_id("IRRIGATION_REG_MOISTURE_0"))
			necessary_attributes.append(SH_defs.register_id("IRRIGATION_REG_MOISTURE_1"))
			necessary_attributes.append(SH_defs.register_id("IRRIGATION_REG_MOISTURE_2"))
			necessary_attributes.append(SH_defs.register_id("IRRIGATION_REG_SENSOR_RAW_0"))
			necessary_attributes.append(SH_defs.register_id("IRRIGATION_REG_SENSOR_RAW_1"))
			necessary_attributes.append(SH_defs.register_id("IRRIGATION_REG_SENSOR_RAW_2"))

		else:
			return self.fully_initialized

		self.fully_initialized = True
		for reg in necessary_attributes:
			if reg not in self.device_attrs:
				self.fully_initialized = False
				self.device_send(messaging.template.format(SH_defs.CMD_GET, reg, 0))
		return self.fully_initialized

