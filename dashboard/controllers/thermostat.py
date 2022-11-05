from flask import request

from dashboard import server_interconnect as interconnect
from dashboard import utilities as utils

import device_manager.device_definitions as dm_defs
import device_manager.messaging_interchange as interchange

import json

def fetch(request):
	device_id = request.args.get("id")
	response_label, thermostats = interconnect.fetch_devices(device_id, device_type = dm_defs.type_id("SH_TYPE_THERMOSTAT"))

	if response_label != "JSON":
		return utils.compose_response(response_label, thermostats)

	valid_devices = []
	for t in thermostats:
		if not t["initialized"]:
			continue

		t["attributes"] = {}

		t["attributes"]["enabled"] = utils.unpack_attribute(t["registers"], "GENERIC_REG_ENABLE")
		print(t["attributes"])
		t["attributes"]["temperature"] = utils.unpack_attribute_to_float(t["registers"], "THERMOSTAT_REG_TEMPERATURE")
		t["attributes"]["target_temperature"] = utils.unpack_attribute_to_float(t["registers"], "THERMOSTAT_REG_TARGET_TEMPERATURE")
		t["attributes"]["humidity"] = utils.unpack_attribute_to_float(t["registers"], "THERMOSTAT_REG_HUMIDITY")
		t["attributes"]["threshold_high"] = utils.unpack_attribute_to_float(t["registers"], "THERMOSTAT_REG_THRESHOLD_HIGH")
		t["attributes"]["threshold_low"] = utils.unpack_attribute_to_float(t["registers"], "THERMOSTAT_REG_THRESHOLD_LOW")
		t["attributes"]["temperature_correction"] = utils.unpack_attribute_to_float(t["registers"], "THERMOSTAT_REG_TEMPERATURE_CORRECTION")
		t["attributes"]["max_heat_time"] = utils.unpack_attribute(t["registers"], "THERMOSTAT_REG_MAX_HEAT_TIME")
		t["attributes"]["min_cooldown_time"] = utils.unpack_attribute(t["registers"], "THERMOSTAT_REG_MIN_COOLDOWN_TIME")

		utils.prune_device_data(t)
		valid_devices.append(t)

	return utils.compose_response(response_label, json.dumps(valid_devices))

def command(request):
	device_id = request.args.get("id")
	value = float(request.data.decode())
	interconnect.data_transaction(interconnect.device_command(device_id, interchange.thermostat_set_temperature(value)))
	return "success"
