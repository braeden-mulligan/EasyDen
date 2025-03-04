from common import device_definitions as device_defs
from ..device_helpers import *
from . import base_device as base

FLOAT_ATTRIBUTE_VALUES = [
	device_defs.attribute_id("THERMOSTAT_ATTR_TARGET_TEMPERATURE"),
	device_defs.attribute_id("THERMOSTAT_ATTR_THRESHOLD_HIGH"),
	device_defs.attribute_id("THERMOSTAT_ATTR_THRESHOLD_LOW"),
	device_defs.attribute_id("THERMOSTAT_ATTR_TEMPERATURE_CORRECTION")
]

INTEGER_ATTRIBUTE_VALUES = [
	device_defs.attribute_id("THERMOSTAT_ATTR_MAX_HEAT_TIME"),
	device_defs.attribute_id("THERMOSTAT_ATTR_MIN_COOLDOWN_TIME")
]

def thermostat_processor(thermostats):
	valid_devices = []
	for device in thermostats:
		if not device["initialized"]:
			continue

		translated_attributes = {}

		translated_attributes["enabled"] = repack_int_attribute("GENERIC_ATTR_ENABLE", device["attributes"])
		translated_attributes["temperature"] = repack_float_attribute("THERMOSTAT_ATTR_TEMPERATURE", device["attributes"])
		translated_attributes["target_temperature"] = repack_float_attribute("THERMOSTAT_ATTR_TARGET_TEMPERATURE", device["attributes"])
		translated_attributes["humidity"] = repack_float_attribute("THERMOSTAT_ATTR_HUMIDITY", device["attributes"])
		translated_attributes["threshold_high"] = repack_float_attribute("THERMOSTAT_ATTR_THRESHOLD_HIGH", device["attributes"])
		translated_attributes["threshold_low"] = repack_float_attribute("THERMOSTAT_ATTR_THRESHOLD_LOW", device["attributes"])
		translated_attributes["temperature_correction"] = repack_float_attribute("THERMOSTAT_ATTR_TEMPERATURE_CORRECTION", device["attributes"])
		translated_attributes["max_heat_time"] = repack_int_attribute("THERMOSTAT_ATTR_MAX_HEAT_TIME", device["attributes"])
		translated_attributes["min_cooldown_time"] = repack_int_attribute("THERMOSTAT_ATTR_MIN_COOLDOWN_TIME", device["attributes"])

		# def schedule_processor(register, value, device = device):
		# 	if register == device_defs.attribute_id("THERMOSTAT_ATTR_TARGET_TEMPERATURE"):
		# 		target_temperature = interchange.reg_to_float({ str(register): { "value": value }}, reg_id = register)
		# 		return ("target_temperature", target_temperature)

		# device_defs.reformat_schedules(device, schedule_processor)

		prune_device_data(device)
		device["attributes"] = translated_attributes

		valid_devices.append(device)

	return valid_devices

def command(request_data):
	command_data = request_data.get("command")

	try:
		command_packet = build_command(command_data, INTEGER_ATTRIBUTE_VALUES, FLOAT_ATTRIBUTE_VALUES)
	except Exception as e:
		return {
			"error": {
				"code": "INVALID_OPERATION",
				"details": "Failed to build thermostat command: " + str(e)
			}
		}

	return base.command(request_data, command_packet, thermostat_processor)

# def set_schedule(request):
# 	return base.set_schedule(request, thermostat_build_command, thermostat_processor, "SH_TYPE_THERMOSTAT")

def handle_request(request):
	directive = request.get("directive")
	request_data = request.get("parameters")

	match directive:
		case "fetch":
			return base.fetch(request_data, thermostat_processor)
		case "command":
			return command(request_data)
		case _:
			return {
				"error":  {
					"code": "INVALID_OPERATION",
					"details": ("Missing" if not directive else "Invalid") + " directive."
				}
			}