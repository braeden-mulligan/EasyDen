from device_manager import config
from device_manager import device_definitions as SH_defs
from device_manager import messaging_interchange as messaging

import datetime, time

def keepalive(device_list):
	for d in device_list:
		if d.initialization_task():
			d.check_heartbeat()

last_thermostat_query = time.time()
def query_thermostats(device_list):
	global last_thermostat_query

	if time.time() < last_thermostat_query + (config.DEVICE_KEEPALIVE  * 0.95):
		return

	thermostats = [d for d in device_list if d.device_type == SH_defs.type_id("SH_TYPE_THERMOSTAT")]
	for t in thermostats:
		t.device_send(messaging.thermostat_get_temperature())
		t.device_send(messaging.thermostat_get_humidity())

	last_thermostat_query = time.time()
