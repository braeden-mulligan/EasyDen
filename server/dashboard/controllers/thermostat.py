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
	for device in thermostats:
		if not device["initialized"]:
			continue

		device["attributes"] = {}

		device["attributes"]["enabled"] = utils.unpack_attribute(device["registers"], "GENERIC_REG_ENABLE")
		device["attributes"]["temperature"] = utils.unpack_attribute_to_float(device["registers"], "THERMOSTAT_REG_TEMPERATURE")
		device["attributes"]["target_temperature"] = utils.unpack_attribute_to_float(device["registers"], "THERMOSTAT_REG_TARGET_TEMPERATURE")
		device["attributes"]["humidity"] = utils.unpack_attribute_to_float(device["registers"], "THERMOSTAT_REG_HUMIDITY")
		device["attributes"]["threshold_high"] = utils.unpack_attribute_to_float(device["registers"], "THERMOSTAT_REG_THRESHOLD_HIGH")
		device["attributes"]["threshold_low"] = utils.unpack_attribute_to_float(device["registers"], "THERMOSTAT_REG_THRESHOLD_LOW")
		device["attributes"]["temperature_correction"] = utils.unpack_attribute_to_float(device["registers"], "THERMOSTAT_REG_TEMPERATURE_CORRECTION")
		device["attributes"]["max_heat_time"] = utils.unpack_attribute(device["registers"], "THERMOSTAT_REG_MAX_HEAT_TIME")
		device["attributes"]["min_cooldown_time"] = utils.unpack_attribute(device["registers"], "THERMOSTAT_REG_MIN_COOLDOWN_TIME")

		for i, schedule in enumerate(device["schedules"]):
			tag = schedule
			_, register, value = tag["command"].split(',')
			register = int(register, 16)

			if register == utils.register_id("THERMOSTAT_REG_TARGET_TEMPERATURE"):
				target_temperature = interchange.reg_to_float({ str(register): { "value": value }}, reg_id = register)
			else:
				continue

			device["schedules"][i] = { "attribute": "target_temperature", "value": target_temperature, "id_tag": tag }

		utils.prune_device_data(device)
		valid_devices.append(device)

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
	command_data = json.loads(request.data.decode())
	message = build_command(command_data)

	if message:
		return base.command(request, command_data["register"], message, thermostat_processor, "SH_TYPE_THERMOSTAT")
	
	return base.error({ "error": None })


def set_schedule(request):
	schedule_data = json.loads(request.data.decode())
	
	if schedule_data["action"] == "create":
		message = build_command(schedule_data)
		del schedule_data["register"]
		del schedule_data["data"]

		schedule_data["command"] = message
	elif schedule_data["action"] == "delete":
		pass

	return base.set_schedule(request, json.dumps(schedule_data), thermostat_processor, "SH_TYPE_THERMOSTAT")