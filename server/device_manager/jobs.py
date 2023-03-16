from device_manager import config
from device_manager import device_definitions as defs
from device_manager import messaging_interchange as messaging

import copy, json, datetime, schedule, time

#TODO Replace with DB ids
last_used_id = 0
def generate_id():
	global last_used_id
	last_used_id += 1
	return last_used_id

# data format: {"recurring": <bool>, "time": {"hour": <int>, "minute": <int>, "days": <string (eg. "mon,thu,sat")>}, "command": <string>, "pause": <int>}
class Device_Command_Schedule:
	def __init__(self, device, data):
		self.schedule_id = generate_id()
		self.device = device
		self.recurring = data["recurring"]
		self.time = data["time"]
		self.command = data["command"]
		self.pause = data["pause"]
		self.job = []

	def get_data(self):
		return {
			"id": self.schedule_id,
			"recurring": self.recurring,
			"time": self.time,
			"command": self.command,
			"pause": self.pause
		}

	def process_task(self):
		if self.pause < 0:
			return
		elif self.pause == 0:
			self.device.device_send(self.command)
		else:
			self.pause -= 1
			return

		if self.recurring == False:
			self.cancel_schedule()

	def cancel_schedule(self):
		for sub_job in self.job:
			schedule.cancel_job(sub_job)
		self.job = None

	def __eq__(self, other):
		if type(other) is not type(self):
			return False
		if other.device.device_id != self.device.device_id:
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
		else:
			return False

		return True


class Nexus_Jobs:
	def __init__(self, device_list):
		self.thermostat_query_interval = config.DEVICE_KEEPALIVE * 0.95
		self.irrigation_query_interval = 10.0

		self.last_thermostat_query = time.monotonic()
		self.last_irrigation_query = time.monotonic()
		self.schedules = []

		self.device_list = device_list

	def run_tasks(self):
		self.query_thermostats()
		self.query_irrigation()
		self.keepalive()
		schedule.run_pending()
		#Scrub expired one-time scheduled events from list
		self.schedules[:] = [schedule for schedule in self.schedules if schedule.job is not None]

	def fetch_schedules(self, device_id):
		return [s.get_data() for s in self.schedules if s.device.device_id == device_id]

	#{("id": <int>,) "action": "create"|"delete"|"edit", "recurring": <bool>, "time": {"hour": "3", "minute": "14", "days": "tue,thu,sun"}, "command": "02,66,42840000", "pause": <int>}
	def submit_schedule(self, device_id, data):
		print("Submitting schedule " + data + " for device " + str(device_id))
		data = json.loads(data)

		action = data["action"]
		del data["action"]

		device = None
		for entry in self.device_list:
			if entry.device_id == device_id:
				device = entry
				break
		
		if action == "delete":
			for s in self.schedules:
				if s.schedule_id == int(data["id"]):
					s.cancel_schedule()
					self.schedules.remove(s)
					print("Successfully removed schedule")
					return True
			print("Failed to find schedule")

		elif action == "create":
			new_schedule = Device_Command_Schedule(device, data)

			for s in self.schedules:
				if new_schedule == s:
					print("Cannot add duplicate event (overlapping schedule)")
					return False

			time_expression = "{:02d}".format(int(data["time"]["hour"])) + ":" + "{:02d}".format(int(data["time"]["minute"]))
			if not data["time"]["days"]:
				new_schedule.job.append(schedule.every().day.at(time_expression).do(new_schedule.process_task))
			else:
				days = data["time"]["days"].split(",")

				if "mon" in days:
					new_schedule.job.append(schedule.every().monday.at(time_expression).do(new_schedule.process_task))
				if "tue" in days:
					new_schedule.job.append(schedule.every().tuesday.at(time_expression).do(new_schedule.process_task))
				if "wed" in days:
					new_schedule.job.append(schedule.every().wednesday.at(time_expression).do(new_schedule.process_task))
				if "thu" in days:
					new_schedule.job.append(schedule.every().thursday.at(time_expression).do(new_schedule.process_task))
				if "fri" in days:
					new_schedule.job.append(schedule.every().friday.at(time_expression).do(new_schedule.process_task))
				if "sat" in days:
					new_schedule.job.append(schedule.every().saturday.at(time_expression).do(new_schedule.process_task))
				if "sun" in days:
					new_schedule.job.append(schedule.every().sunday.at(time_expression).do(new_schedule.process_task))

			self.schedules.append(new_schedule)
			print("New schedule added!")
			return True

		elif action == "edit":
			for s in self.schedules:
				if s.schedule_id == data["id"]:
					s.pause = data["pause"]
					print("Edited schedule " + str(s.schedule_id))
					return True
			print("Failed to find schedule")

		return False

	def query_thermostats(self):
		if time.monotonic() < self.last_thermostat_query + self.thermostat_query_interval:
			return

		thermostats = [d for d in self.device_list if d.device_type == defs.type_id("SH_TYPE_THERMOSTAT")]
		for device in thermostats:
			device.device_send(messaging.thermostat_get_temperature())
			#TODO: if device has humidity sensor
			#device.device_send(messaging.thermostat_get_humidity())

		self.last_thermostat_query = time.monotonic()

	def query_irrigation(self):	
		if time.monotonic() < self.last_irrigation_query + self.last_irrigation_query:
			return

		irrigators = [d for d in self.device_list if d.device_type == defs.type_id("SH_TYPE_IRRIGATION")]
		for device in irrigators:
			for i in range(3):
				device.device_send(messaging.irrigation_get_moisture(i))
				device.device_send(messaging.irrigation_get_moisture_raw(i))
				device.device_send(messaging.irrigation_get_sensor_raw_max(i))
				device.device_send(messaging.irrigation_get_sensor_raw_min(i))
				device.device_send(messaging.irrigation_get_sensor_recorded_max(i))
				device.device_send(messaging.irrigation_get_sensor_recorded_min(i))

		self.last_irrigation_query = time.monotonic()

	def keepalive(self):
		for device in self.device_list:
			if device.initialization_task():
				device.check_heartbeat()
