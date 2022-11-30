from flask import request 

from dashboard import utilities as utils
from dashboard.controllers import base_device as base

import device_manager.messaging_interchange as interchange

import json

FLOAT_REGISTER_VALUES = [
	utils.register_id("THERMOSTAT_REG_TARGET_TEMPERATURE"),
	utils.register_id("THERMOSTAT_REG_THRESHOLD_HIGH"),
	utils.register_id("THERMOSTAT_REG_THRESHOLD_LOW"),
	utils.register_id("THERMOSTAT_REG_TEMPERATURE_CORRECTION")
]

INTEGER_REGISTER_VALUES = [
	utils.register_id("GENERIC_REG_ENABLE"),
	utils.register_id("THERMOSTAT_REG_MAX_HEAT_TIME"),
	utils.register_id("THERMOSTAT_REG_MIN_COOLDOWN_TIME")
]

def thermostat_processor(thermostats):
	valid_devices = []
	for t in thermostats:
		if not t["initialized"]:
			continue

		t["attributes"] = {}

		t["attributes"]["enabled"] = utils.unpack_attribute(t["registers"], "GENERIC_REG_ENABLE")
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

def build_command(request_data):
	register = int(request_data["register"])

	if register in FLOAT_REGISTER_VALUES:
		value = float(request_data["data"])
		return interchange.command_from_float(register, value)
	elif register in INTEGER_REGISTER_VALUES:
		value = int(request_data["data"])
		return interchange.command_from_int(register, value)

	return None

def command(request):
	message = None
	register = int(request.args.get("register"))

	#TODO Fix this with front-end
	value = request.data.decode()
	attribute_data = {"register": register, "data": value}
	message = build_command(attribute_data)

	if message:
		return base.command(request, message, thermostat_processor, "SH_TYPE_THERMOSTAT")
	
	return base.error({ "error": None })


def set_schedule(request):
	schedule_data = json.loads(request.data.decode())
	message = build_command(schedule_data)
	
	del schedule_data["register"]
	del schedule_data["data"]

	schedule_data["command"] = message

	return base.set_schedule(request, json.dumps(schedule_data), thermostat_processor, "SH_TYPE_THERMOSTAT")