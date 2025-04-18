import sys
sys.path.append("..")
from common import server_config as config
from common import device_definitions as defs
from common.log_handler import logger as log
from common import device_protocol_helpers as device_protocol
from common.defines import *
from common.utils import error_response
from database import operations as db

import json, schedule, time

#TODO: Refactor jobs and schedules

class Device_Command_Schedule:
	"""
	data: {
		"recurring": bool,
		"time": {
			"hour": int,
			"minute": int,
			"days": string - eg. "mon,thu,sat"
		},
		"command": string - device message eg. "02,66,42840000",
		"pause": int
	}
	"""
	def __init__(self, device, data, schedule_id = None):
		self.id = schedule_id
		self.device = device
		self.recurring = data["recurring"]
		self.time = data["time"]
		self.command = data["command"]
		self.pause = data["pause"]
		self.job = []

	def __eq__(self, other):
		if type(other) is not type(self):
			return False
		if other.device.id != self.device.id:
			return False
		if other.command != self.command:
			return False
		if other.time["hour"] == self.time["hour"] and other.time["minute"] == self.time["minute"]:
			if not self.time["days"] or not other.time["days"]:
				return True
			
			for day in self.time["days"].split(","):
				if day in other.time["days"].split(","):
					return True
		return False

	def get_data(self):
		return {
			"id": self.id,
			"recurring": self.recurring,
			"time": self.time,
			"command": self.command,
			"pause": self.pause
		}

	def cancel_schedule(self):
		for sub_job in self.job:
			schedule.cancel_job(sub_job)
		self.job = None

	def process_task(self):
		if self.pause < 0:
			return
		elif self.pause == 0:
			self.device.device_send(self.command)
			if self.recurring == False:
				self.cancel_schedule()
		else:
			self.pause -= 1
			return

	def enqueue_job(self):
		time_expression = "{:02d}".format(int(self.time["hour"])) + ":" + "{:02d}".format(int(self.time["minute"]))
		if not self.time["days"]:
			self.job.append(schedule.every().day.at(time_expression).do(self.process_task))
		else:
			days = self.time["days"].split(",")

			if "mon" in days:
				self.job.append(schedule.every().monday.at(time_expression).do(self.process_task))
			if "tue" in days:
				self.job.append(schedule.every().tuesday.at(time_expression).do(self.process_task))
			if "wed" in days:
				self.job.append(schedule.every().wednesday.at(time_expression).do(self.process_task))
			if "thu" in days:
				self.job.append(schedule.every().thursday.at(time_expression).do(self.process_task))
			if "fri" in days:
				self.job.append(schedule.every().friday.at(time_expression).do(self.process_task))
			if "sat" in days:
				self.job.append(schedule.every().saturday.at(time_expression).do(self.process_task))
			if "sun" in days:
				self.job.append(schedule.every().sunday.at(time_expression).do(self.process_task))

class Nexus_Jobs:
	def __init__(self, device_list):
		self.thermostat_query_interval = config.DEVICE_KEEPALIVE * 0.95
		# self.irrigation_query_interval = 10.0
		# self.temperature_record_interval = 600.0

		self.last_thermostat_query = time.monotonic()
		self.last_irrigation_query = time.monotonic()
		self.device_list = device_list
		self.schedules = []
		self.thermostat_data = []
		self.log_temperature_flag = False
		self.last_temperature_record = time.monotonic()

		def schedule_entry_loader(db_row):
			device = next((d for d in device_list if d.id == db_row[2]), None)
			if device:
				self.schedules.append(Device_Command_Schedule(device, json.loads(db_row[1]), db_row[0]))

		db.load_schedules(device_list, schedule_entry_loader)

		for sched in self.schedules:
			sched.enqueue_job()

	def run_tasks(self):
		self.query_thermostats()
		# self.log_temperature()
		# self.query_irrigation()
		self.keepalive()
		schedule.run_pending()

		#Scrub expired one-time scheduled events from list
		for s in self.schedules:
			if s.job is None:
				db.remove_schedule(s.id)
		self.schedules[:] = [schedule for schedule in self.schedules if schedule.job is not None]

	def fetch_schedules(self, device_id):
		return [s.get_data() for s in self.schedules if s.device.id == device_id]

	def create_schedule(self, device_id, data):
		"""
		data: Device_Command_Schedule init data
		"""

		log.debug("Submitting schedule " + str(data) + " for device " + str(device_id))

		device = None
		for entry in self.device_list:
			if entry.id == device_id:
				device = entry
				break

		if device is None:
			return error_response(E_REQUEST_FAILED, "Device not found")
		
		try:
			new_schedule = Device_Command_Schedule(device, data)

			for s in self.schedules:
				if new_schedule == s:
					error_details = "Cannot add duplicate event (overlapping schedule)"
					log.info(error_details)
					return error_response(E_REQUEST_FAILED, error_details)

			new_schedule.id = db.add_schedule(new_schedule)
			new_schedule.enqueue_job()
			self.schedules.append(new_schedule)

			log.debug("New schedule added!")

			return {
				"result": "success",
				"schedule-id": new_schedule.id
			}

		except KeyError:
			error_details = "Could not create schedule. Bad argument provided."
			log.warning(error_details)
			return error_response(E_INVALID_REQUEST, error_details)

		except Exception as e:
			error_details = "Failed to create schedule."
			log.exception(error_details)
			return error_response(E_UNKNOWN, error_details, e)


	def delete_schedule(self, schedule_id):
		try:
			for s in self.schedules:
				if s.id == schedule_id:
					s.cancel_schedule()
					self.schedules.remove(s)
					db.remove_schedule(s.id)
					log.debug("Successfully removed schedule")
					return {
						"result": "success"
					}

			error_details = "Failed to find schedule"
			log.debug(error_details)
			return error_response(E_REQUEST_FAILED, error_details)

		except Exception as e:
			return error_response(E_UNKNOWN, "Failed to delete schedule", e)

	def query_thermostats(self):
		if time.monotonic() < self.last_thermostat_query + self.thermostat_query_interval:
			return

		thermostats = [d for d in self.device_list if d.type == defs.device_type_id("DEVICE_TYPE_THERMOSTAT")]
		for device in thermostats:
			device.device_send(device_protocol.thermostat_get_temperature())
			device.device_send(device_protocol.thermostat_get_status())
			#TODO: if device has humidity sensor
			#device.device_send(messaging.thermostat_get_humidity())

		self.last_thermostat_query = time.monotonic()
		# self.log_temperature_flag = True

	def log_temperature(self):
		log_delay = 10.0
		if self.thermostat_query_interval <= log_delay:
			raise Exception("Temperature data will not be logged!")

		if time.monotonic() < self.last_thermostat_query + log_delay:
			return

		if self.log_temperature_flag == False:
			return

		thermostats = [d.get_data() for d in self.device_list if d.type == defs.device_type_id("DEVICE_TYPE_THERMOSTAT")]
		for device in thermostats:
			if not device["initialized"]:
				continue

			# utils.hexify_attribute_values(device["attributes"])
			entry = (
			  device["id"],
			  device_protocol.reg_to_float(device["attributes"], reg_label = "THERMOSTAT_ATTR_TEMPERATURE"),
			  device_protocol.reg_to_float(device["attributes"], reg_label = "THERMOSTAT_ATTR_TARGET_TEMPERATURE"),
			  device_protocol.reg_to_int(device["attributes"], reg_label = "GENERIC_ATTR_ENABLE"),
			  device["online"],
			  int(time.time())
			)
			self.thermostat_data.append(entry)

		self.log_temperature_flag = False

		if time.monotonic() < self.last_temperature_record + self.temperature_record_interval:
			return

		db.store_thermostat_data(self.thermostat_data)
		self.thermostat_data = []
		self.last_temperature_record = time.monotonic()

	def query_irrigation(self):	
		if time.monotonic() < self.last_irrigation_query + self.irrigation_query_interval:
			return

		irrigators = [d for d in self.device_list if d.type == defs.device_type_id("DEVICE_TYPE_IRRIGATION")]
		for device in irrigators:
			for i in range(defs.IRRIGATION_MAX_SENSOR_COUNT):
				device.device_send(device_protocol.irrigation_get_moisture(i))
				device.device_send(device_protocol.irrigation_get_moisture_raw(i))
				device.device_send(device_protocol.irrigation_get_sensor_raw_max(i))
				device.device_send(device_protocol.irrigation_get_sensor_raw_min(i))
				device.device_send(device_protocol.irrigation_get_sensor_recorded_max(i))
				device.device_send(device_protocol.irrigation_get_sensor_recorded_min(i))

		self.last_irrigation_query = time.monotonic()

	def keepalive(self):
		for device in self.device_list:
			if device.initialization_task():
				device.check_heartbeat()
