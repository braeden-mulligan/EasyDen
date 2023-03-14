from device_manager import config
from device_manager import device_definitions as defs
from device_manager import messaging_interchange as messaging

#TODO fix this dirty style
from device_manager import device_nexus as nexus

import json, datetime, schedule, time

schedules = []

last_thermostat_query = time.time()
last_irrigation_query = time.time()

def keepalive(device_list):
	for d in device_list:
		if d.initialization_task():
			d.check_heartbeat()

#TODO: use new schedule job architecture for doing this.
def query_thermostats(device_list):
	global last_thermostat_query

	if time.time() < last_thermostat_query + (config.DEVICE_KEEPALIVE  * 0.95):
		return

	thermostats = [d for d in device_list if d.device_type == defs.type_id("SH_TYPE_THERMOSTAT")]
	for t in thermostats:
		t.device_send(messaging.thermostat_get_temperature())
#TODO: if device has humidity sensor
		#t.device_send(messaging.thermostat_get_humidity())

	last_thermostat_query = time.time()

def query_irrigation(device_list):
	global last_irrigation_query
	
	if time.time() < last_irrigation_query + 5.0:
		return

	irrigators = [d for d in device_list if d.device_type == defs.type_id("SH_TYPE_IRRIGATION")]
	for device in irrigators:
		for i in range(3):
			device.device_send(messaging.irrigation_get_moisture(i))
			device.device_send(messaging.irrigation_get_moisture_raw(i))
			device.device_send(messaging.irrigation_get_sensor_raw_max(i))
			device.device_send(messaging.irrigation_get_sensor_raw_min(i))
			device.device_send(messaging.irrigation_get_sensor_recorded_max(i))
			device.device_send(messaging.irrigation_get_sensor_recorded_min(i))

	last_irrigation_query = time.time()

class Device_Schedule:
	def __init__(self, device_id, data):
		self.device_id = device_id
		self.data = data
		self.job = []

	def __eq__(self, other):
		if type(other) is not type(self):
			return False
		if other.device_id != self.device_id:
			return False
		if other.data != self.data:
			return False
		return True

def send_command(device_id, command):
	for d in nexus.device_list:
		if device_id == d.device_id:
			d.device_send(command)
	return

def fetch_schedules(device_id):
	existing_schedules = []
	for s in schedules:
		if s.device_id == device_id:
			existing_schedules.append(s.data)
	return existing_schedules

#{"action": "create", "recurring": true, "time": {"hour": "3", "minute": "14"}, "command": "02,66,42840000"}
def submit_schedule(device_id, data):
	global schedules

	print("Appending " + data + " for device " + str(device_id))
	data = json.loads(data)

	action = data["action"]
	del data["action"]

	new_schedule = Device_Schedule(device_id, data)
	
	for s in schedules:
		if new_schedule == s:
			if action == "delete":
				for j in s.job:
					schedule.cancel_job(j)
				schedules.remove(s)
				return True
			else:
				print("Cannot add duplicate schedule")
				return False
	print("NEW SCHEDULE ADDED!")

	time_expression = "{:02d}".format(int(data["time"]["hour"])) + ":" + "{:02d}".format(int(data["time"]["minute"]))
	new_schedule.job.append(schedule.every().day.at(time_expression).do(send_command, device_id, data["command"]))
	schedules.append(new_schedule)

	return True

def run_tasks(device_list):
	keepalive(device_list)
	query_thermostats(device_list)
	query_irrigation(device_list)

	schedule.run_pending()
	return