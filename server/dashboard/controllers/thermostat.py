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

		def schedule_processor(register, value, device = device):
			if register == utils.register_id("THERMOSTAT_REG_TARGET_TEMPERATURE"):
				target_temperature = interchange.reg_to_float({ str(register): { "value": value }}, reg_id = register)
				return ("target_temperature", target_temperature)

		utils.reformat_schedules(device, schedule_processor)
		utils.prune_device_data(device)

		valid_devices.append(device)

	return valid_devices

def fetch(request):
	return base.fetch(request, thermostat_processor, "SH_TYPE_THERMOSTAT")

def command(request):
	command_data = json.loads(request.data.decode())
	message = utils.build_command(command_data, INTEGER_REGISTER_VALUES, FLOAT_REGISTER_VALUES)

	if message:
		return base.command(request, command_data["register"], message, thermostat_processor, "SH_TYPE_THERMOSTAT")
	
	return base.error({ "error": None })

def set_schedule(request):
	data = json.loads(request.data.decode())
	return base.set_schedule(request, data, thermostat_build_command, thermostat_processor, "SH_TYPE_THERMOSTAT")

def thermostat_build_command(data):
	return utils.build_command(data, INTEGER_REGISTER_VALUES, FLOAT_REGISTER_VALUES)