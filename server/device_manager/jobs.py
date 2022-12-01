from device_manager import config
from device_manager import device_definitions as SH_defs
from device_manager import messaging_interchange as messaging

#TODO fix this dirty style
from device_manager import device_nexus as nexus

import json, datetime, schedule, time

schedules = []

last_thermostat_query = time.time()

def keepalive(device_list):
	for d in device_list:
		if d.initialization_task():
			d.check_heartbeat()

#TODO: use new schedule job architecture for doing this.
def query_thermostats(device_list):
	global last_thermostat_query

	if time.time() < last_thermostat_query + (config.DEVICE_KEEPALIVE  * 0.95):
		return

	thermostats = [d for d in device_list if d.device_type == SH_defs.type_id("SH_TYPE_THERMOSTAT")]
	for t in thermostats:
		t.device_send(messaging.thermostat_get_temperature())
#TODO: if device has humidity sensor
		#t.device_send(messaging.thermostat_get_humidity())

	last_thermostat_query = time.time()

class Device_Schedule:
	def __init__(self, device_type, data, device_id):
		self.data = data
		self.device_type = device_type
		self.device_id = device_id
		self.job = None

	def __eq__(self, other):
		if type(other) is not type(self):
			return False
		if other.data != self.data:
			return False
		if other.device_type != self.device_type:
			return False
		if other.device_id != self.device_id:
			return False
		return True

def send_command(command, device_type, device_id):
	for d in nexus.device_list:
		if device_id is None and d.device_type == device_type:
			d.device_send(command)
		elif device_id and device_id == d.device_id:
			d.device_send(command)
	return

def fetch_schedules(device_id, device_type):
	existing_schedules = []
	for s in schedules:
		if s.device_id is None or s.device_id == device_id:
			existing_schedules.append(s.data)
	return existing_schedules

def submit_schedule(device_type, data, device_id = None):
	global schedules

	print("Appending " + data + " for device_type " + SH_defs.type_label(device_type) + " id " + str(device_id))
	data = json.loads(data)

	action = data["action"]
	del data["action"]

	new_schedule = Device_Schedule(device_type, data, device_id)
	
	for s in schedules:
		if new_schedule == s:
			if action == "delete":
				schedule.cancel_job(s.job)
				schedules.remove(s)
				return True
			else:
				#TODO: Handle if new schedule for type + id is already covered by same data for entire type group
				print("Cannot add duplicate schedule")
				return False
	print("NEW SCHEDULE ADDED!")

#TODO: proper cron format.
	time_expression = "{:02d}".format(int(data["time"]["hour"])) + ":" + "{:02d}".format(int(data["time"]["minute"]))
	new_schedule.job = schedule.every().day.at(time_expression).do(send_command, data["command"], device_type, device_id)
	schedules.append(new_schedule)

	return True

#{"action":"create","recurring":true,"time":{"hour":"23","minute":"2"},"command":"02,66,41B00000"}

def run_tasks(device_list):
	keepalive(device_list)
	query_thermostats(device_list)

	schedule.run_pending()
	return