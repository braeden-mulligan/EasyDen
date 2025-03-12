import sys
sys.path.append("..")
from common import server_config as config
from common import device_definitions as defs
from common.log_handler import logger as log

from common import device_protocol_helpers as device_protocol
import copy, datetime, sys, time

def parse_packet(packet):
	try:
		words = [int(w, 16) for w in packet.split(',')]
	except Exception as e:
		log.warning("Failed to parse packet <" + packet + ">", exc_info = True)
		return None

	if len(words) != 4:
		log.warning("Unexpected packed length: <" + packet + ">", exc_info = True)
		return None

	return words

class Pending_Message:	
	def __init__(self, packet, timestamp, retries):
		self.packet = packet
		self.timestamp = timestamp
		self.retries = retries

	def __eq__(self, other):
		if other.packet == self.packet:
			return True
		return False

	def duplicate(self, other):
		_, cmd_1, reg_1, val_1 = parse_packet(self.packet)
		_, cmd_2, reg_2, val_2 = parse_packet(other.packet)
		if cmd_1 == cmd_2 and reg_1 == reg_2 and val_1 == val_2:
			return True
		return False
		
class SmartHome_Device:
	STATUS_OK = 0
	STATUS_UNRESPONSIVE = 1
	STATUS_ERROR = 2

	ERROR_NO_SOCKET = -1
	ERROR_QUEUE_FULL = -2

	MAX_SEQUENCE_NUM = 32767
	TX_BUFFER_SIZE = 128

	def __init__(self, socket_connection = None):
		# Attributes returned on device query.
		self.type = 0
		self.id = 0
		self.attributes = {} #(reg, {value, queried_at, updated_at})
		self.name = "Default Name"
		self.online_status = False 
		self.fully_initialized = False

		# Attributes available for info query
		self.last_contact = None
		self.reconnect_count = -1 # For debugging

		self.msg_timeout = config.TX_TIMEOUT
		self.msg_retries = config.MAX_TX_RETRIES
		self.soc_heartbeat = config.DEVICE_KEEPALIVE

		# Configs
		self.soc_connection = None
		self.soc_fd = None
		self.soc_last_heartbeat = None
		self.max_pending_messages = SmartHome_Device.TX_BUFFER_SIZE
		self.msg_queue_retention_time = config.TX_QUEUE_RETENTION_TIME

		self.msg_seq = 1
		self.pending_response = None
		self.pending_transmissions = []
		self.consecutive_nack = 0

		self.connect(socket_connection)
		self.update_last_contact()
		return

	def get_data(self):
		return {
			"type": self.type,
			"id": self.id,
			"name": self.name,
			"online": self.online_status,
			"initialized": self.fully_initialized,
			"attributes": copy.deepcopy(self.attributes)
		}

	def disconnect(self):
		self.online_status = False
		self.soc_connection = None
		self.soc_fd = None
		self.pending_response = None
		for m in self.pending_transmissions:
			m.timestamp = time.monotonic()
		return

	def connect(self, soc_conn):
		self.soc_connection = soc_conn
		if soc_conn is not None:
			self.soc_fd = self.soc_connection.fileno()
			self.online_status = True
			self.consecutive_nack = 0
			self.reconnect_count += 1
			self.update_last_contact()
		return 

	def update_pending(self):
		def transmit_packet():
			self.pending_response.timestamp = time.monotonic()
			self.soc_connection.send(self.pending_response.packet.encode())

		if self.pending_response:
			if time.monotonic() > self.pending_response.timestamp + self.msg_timeout:
				if self.pending_response.retries > 0:
					log.info("Message <" + self.pending_response.packet + "> deilvery failed, retrying " + str(self.pending_response.retries) + " more times...")
					self.pending_response.retries -= 1
					try:
						transmit_packet()
					except ConnectionResetError:
						self.pending_transmissions.pop(0)
						return SmartHome_Device.STATUS_ERROR
				else:
					log.info("Message <" + self.pending_response.packet + "> deilvery failed.")
					self.consecutive_nack += 1
					self.pending_transmissions.insert(0, self.pending_response)
					self.pending_response = None
					return SmartHome_Device.STATUS_UNRESPONSIVE

		elif self.pending_transmissions:
			next_message = self.pending_transmissions[0]

			if self.soc_connection:
				log.debug("Transmitting: <" + str(next_message.packet) + "> to device " + str(self.id) + ". " + str(next_message.retries) + " retries available...")
				self.pending_response = next_message
				try:
					transmit_packet()
				except ConnectionResetError:
					self.pending_transmissions.pop(0)
					return SmartHome_Device.STATUS_ERROR
				self.pending_transmissions.pop(0)
			elif self.msg_queue_retention_time >= 0.0:
				self.pending_transmissions = [m for m in self.pending_transmissions if (m.timestamp + self.msg_queue_retention_time > time.monotonic())]

		return SmartHome_Device.STATUS_OK	

	def check_heartbeat(self):
		if self.pending_response:
			_, _, pending_reg, _ = parse_packet(self.pending_response.packet)
			
			if pending_reg == defs.attribute_id("GENERIC_ATTR_PING"):
				# Already waiting on a heartbeat check.
				return
		
		if self.online_status and (time.monotonic() > self.soc_last_heartbeat + config.DEVICE_KEEPALIVE):
			self.device_send(device_protocol.generic_ping())
			self.soc_last_heartbeat = time.monotonic()

	def device_recv(self):
		if self.soc_connection is not None:
			try:
				# This should always return bytes because we use i/o poll mechanism.
				msg = self.soc_connection.recv(32).decode()
			except Exception as e:
				log.warning("Socket recv failed.", exc_info = True)
				return -1

			log.debug("Received <" + msg + "> from device: " + str(self.id))

			self.update_last_contact()

			recv_result = self.process_message(msg)
			if recv_result is None:
				return -2
			return recv_result
		return 0

	def device_send(self, message):
		m = "{:04X},".format(self.msg_seq) + message

		_, cmd, reg, val = parse_packet(m)
		if cmd == defs.Device_Protocol.CMD_GET or cmd == defs.Device_Protocol.CMD_SET:
			self.update_attributes(reg, val, query = True)

		#TODO: Throw into queue and wait for (re)connection?
		if self.soc_connection is None:
			return SmartHome_Device.ERROR_NO_SOCKET

		current_seq = self.msg_seq
		self.msg_seq += 1
		if self.msg_seq >= SmartHome_Device.MAX_SEQUENCE_NUM:
			self.msg_seq = 1

		log.debug("Enqueue: <" + m + "> to device " + str(self.id))

		if len(self.pending_transmissions) >= self.max_pending_messages:
			log.warning("Device send buffer full")
			return SmartHome_Device.ERROR_QUEUE_FULL
		
		submitted_message = Pending_Message(m, time.monotonic(), self.msg_retries)

		for entry in self.pending_transmissions:
			if submitted_message.duplicate(entry):
				return current_seq

		self.pending_transmissions.append(submitted_message)

		return current_seq 

	# Private

	def update_last_contact(self):
		self.last_contact = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
		self.soc_last_heartbeat = time.monotonic()
		self.consecutive_nack = 0
		return

	def update_attributes(self, reg, val, query = False, update = False):
		if reg == defs.attribute_id("GENERIC_ATTR_NULL"):
			return
		elif reg == defs.attribute_id("GENERIC_ATTR_PING"):
			return
		else: 
			attribute = {
			  "value": val,
			  "queried_at": round(time.monotonic(), 5) if query else 0.0,
			  "updated_at": round(time.monotonic(), 5) if update else 0.0
			}

			self.attributes[reg] = self.attributes.get(reg, attribute)

			if query:
				self.attributes[reg]["queried_at"] = attribute["queried_at"]
			elif update:
				self.attributes[reg]["value"] = attribute["value"]
				self.attributes[reg]["updated_at"] = attribute["updated_at"]

	def process_message(self, packet):
		try:
			msg_seq, msg_cmd, msg_reg, msg_val = parse_packet(packet)
		except TypeError:
			log.warning("Failed to parse packet <" + str(packet) + ">!")
			return None

		sent_seq = sent_cmd = sent_reg = sent_val = None

		if self.pending_response:
			sent_seq, sent_cmd, sent_reg, sent_val = parse_packet(self.pending_response.packet)
			if msg_seq == sent_seq:
				self.pending_response = None

#TODO: Might not be possible to hit this block anymore.
		elif self.pending_transmissions:
			raise Exception("Unreachable block reached!")
			print("No pending_response, checking send queue.")
			for entry in self.pending_transmissions:
				sent_seq, sent_cmd, sent_reg, sent_val = parse_packet(entry.packet)
				if msg_seq == sent_seq:
					print("Found in send queue. Message awaiting transmission removed.")
					self.pending_transmissions.remove(entry)

		else:
# This can occur when device transmits a response but a retry is sent before the first response comes back.
# The first response is processed and then a duplicate response then comes because of the retry. Shouldn't be a problem.
# Conjecture: frequency of this is a function of timeout and retry count, tuning needed?
			log.warning("process_message error. Received packet does not correspond to any pending messages.")
			return None

		if msg_cmd == defs.Device_Protocol.CMD_RSP and sent_cmd == defs.Device_Protocol.CMD_GET:
			self.update_attributes(msg_reg, msg_val, update = True)

		elif msg_cmd == defs.Device_Protocol.CMD_RSP and sent_cmd == defs.Device_Protocol.CMD_SET: 
			self.update_attributes(sent_reg, msg_val, update = True)

		elif msg_cmd == defs.Device_Protocol.CMD_IDY:
			self.type = msg_reg
			self.id = msg_val
			return self.id

		return 0

	def initialization_task(self):
		if self.fully_initialized:
			return True
		if not self.id or self.pending_response:
			return False

		necessary_attributes = [
			defs.attribute_id("GENERIC_ATTR_ENABLE")
		]

		if self.type == defs.device_type_id("DEVICE_TYPE_POWEROUTLET"):
			necessary_attributes.append(defs.attribute_id("POWEROUTLET_ATTR_SOCKET_COUNT"))
			necessary_attributes.append(defs.attribute_id("POWEROUTLET_ATTR_STATE"))

		elif self.type == defs.device_type_id("DEVICE_TYPE_THERMOSTAT"):
			necessary_attributes.append(defs.attribute_id("THERMOSTAT_ATTR_TEMPERATURE"))
			necessary_attributes.append(defs.attribute_id("THERMOSTAT_ATTR_TARGET_TEMPERATURE"))
			necessary_attributes.append(defs.attribute_id("THERMOSTAT_ATTR_TEMPERATURE_CORRECTION"))
			necessary_attributes.append(defs.attribute_id("THERMOSTAT_ATTR_THRESHOLD_HIGH"))
			necessary_attributes.append(defs.attribute_id("THERMOSTAT_ATTR_THRESHOLD_LOW"))
			necessary_attributes.append(defs.attribute_id("THERMOSTAT_ATTR_MAX_HEAT_TIME"))
			necessary_attributes.append(defs.attribute_id("THERMOSTAT_ATTR_MIN_COOLDOWN_TIME"))
			necessary_attributes.append(defs.attribute_id("THERMOSTAT_ATTR_HUMIDITY_SENSOR_COUNT"))

		elif self.type == defs.device_type_id("DEVICE_TYPE_IRRIGATION"):
			necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_SENSOR_COUNT"))
			necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_PLANT_ENABLE"))
			necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_MOISTURE_CHANGE_HYSTERESIS_TIME"))
			necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_MOISTURE_CHANGE_HYSTERESIS_AMOUNT"))
			necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_CALIBRATION_MODE"))
			
			for i in range(defs.IRRIGATION_MAX_SENSOR_COUNT):
				necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_MOISTURE_" + str(i)))
				necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_MOISTURE_LOW_" + str(i)))
				necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_MOISTURE_LOW_DELAY_" + str(i)))
				necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_SENSOR_RAW_" + str(i)))
				necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_SENSOR_RAW_MAX_" + str(i)))
				necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_SENSOR_RAW_MIN_" + str(i)))
				necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_SENSOR_RECORDED_MAX_" + str(i)))
				necessary_attributes.append(defs.attribute_id("IRRIGATION_ATTR_SENSOR_RECORDED_MIN_" + str(i)))

		else:
			return self.fully_initialized

		self.fully_initialized = True
		for reg in necessary_attributes:
			attribute = self.attributes.get(reg, None)
			if attribute is None or attribute["updated_at"] < attribute["queried_at"]:
				self.fully_initialized = False
				self.device_send(device_protocol.template.format(defs.Device_Protocol.CMD_GET, reg, 0))

		return self.fully_initialized
