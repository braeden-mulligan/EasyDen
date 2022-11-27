from flask import request 

from dashboard import utilities as utils
from dashboard.controllers import base_device as base

import device_manager.messaging_interchange as interchange

def thermostat_processor(thermostats):
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

	return valid_devices

def fetch(request):
	return base.fetch(request, thermostat_processor, "SH_TYPE_THERMOSTAT")

def command(request):
	float_register_values = [
	  utils.register_id("THERMOSTAT_REG_TARGET_TEMPERATURE"),
	  utils.register_id("THERMOSTAT_REG_THRESHOLD_HIGH"),
	  utils.register_id("THERMOSTAT_REG_THRESHOLD_LOW"),
	  utils.register_id("THERMOSTAT_REG_TEMPERATURE_CORRECTION")
	]

	integer_register_values = [
	  utils.register_id("GENERIC_REG_ENABLE"),
	  utils.register_id("THERMOSTAT_REG_MAX_HEAT_TIME"),
	  utils.register_id("THERMOSTAT_REG_MIN_COOLDOWN_TIME")
	]

	message = None
	register = int(request.args.get("register"))

	if register in float_register_values:
		value = float(request.data.decode())
		message = interchange.command_from_float(register, value)
	elif register in integer_register_values:
		value = int(request.data.decode())
		message = interchange.command_from_int(register, value)
	else:
		return base.error({ "error": None })

	return base.command(request, message, thermostat_processor, "SH_TYPE_THERMOSTAT")

