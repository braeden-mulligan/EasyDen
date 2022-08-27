from flask import request

from dashboard import server_interconnect as interconnect
from dashboard import utilities as utils

import device_manager.device_definitions as dm_defs
import device_manager.messaging as dm_messaging

import json

def fetch(request):
	device_id = request.args.get("id")
	thermostats = interconnect.fetch_devices(device_id, device_type = dm_defs.type_id("SH_TYPE_THERMOSTAT"))

	if thermostats is None:
		return "{result: \"ERROR\"}"

	valid_devices = []
	for t in thermostats:
		if not t["initialized"]:
			continue

		t["temperature"] = dm_messaging.reg_to_float(t["registers"], "THERMOSTAT_REG_TEMPERATURE")
		t["humidity"] = dm_messaging.reg_to_float(t["registers"], "THERMOSTAT_REG_HUMIDITY")

		utils.prune_device_obj(t)
		valid_devices.append(t)

	return json.dumps(valid_devices)

def command(request):
#TODO: Debugging for now
	device_id = request.args.get("id")
	interconnect.data_transaction(interconnect.device_command(device_id, thermostat_get_temperature()))
	interconnect.data_transaction(interconnect.device_command(device_id, thermostat_get_humidity()))
	return "success"
