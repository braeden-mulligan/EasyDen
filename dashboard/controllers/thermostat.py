from flask import request

from dashboard import server_interconnect as interconnect
from dashboard import utilities as utils

import device_manager.device_definitions as dm_defs
import device_manager.messaging_interchange as interchange

import json

def unpack_with_float(registers, reg_label):
	attr = utils.unpack_reg_attribute(registers, reg_label)
	attr["value"] = interchange.reg_to_float(registers, reg_label)
	return attr

def fetch(request):
	device_id = request.args.get("id")
	response_label, thermostats = interconnect.fetch_devices(device_id, device_type = dm_defs.type_id("SH_TYPE_THERMOSTAT"))

	if response_label != "JSON":
		return utils.compose_response(response_label, poweroutlets)

	valid_devices = []
	for t in thermostats:
		if not t["initialized"]:
			continue

		t["attributes"] = {}

		t["attributes"]["temperature"] = unpack_with_float(t["registers"], "THERMOSTAT_REG_TEMPERATURE")
		t["attributes"]["target_temperature"] = unpack_with_float(t["registers"], "THERMOSTAT_REG_TARGET_TEMPERATURE")
		t["attributes"]["humidity"] = unpack_with_float(t["registers"], "THERMOSTAT_REG_HUMIDITY")
		t["attributes"]["threshold_high"] = unpack_with_float(t["registers"], "THERMOSTAT_REG_THRESHOLD_HIGH")
		t["attributes"]["threshold_low"] = unpack_with_float(t["registers"], "THERMOSTAT_REG_THRESHOLD_LOW")

		utils.prune_device_data(t)
		valid_devices.append(t)

	return utils.compose_response(response_label, json.dumps(valid_devices))

def command(request):
#TODO: Debugging for now, device manager should periodically check this
	device_id = request.args.get("id")
	value = float(request.data.decode())
	#interconnect.data_transaction(interconnect.device_command(device_id, interchange.thermostat_get_temperature()))
	#interconnect.data_transaction(interconnect.device_command(device_id, interchange.thermostat_get_humidity()))
	interconnect.data_transaction(interconnect.device_command(device_id, interchange.thermostat_set_temperature(value)))
	return "success"
