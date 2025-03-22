from common.defines import *
from common.utils import error_response, int32_to_float
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

		# TODO: Make this not so ad hoc
		translated_attributes["status"] = {
			"id": 200,
			"value": device["attributes"].get("200", {}).get("value", 69)
		}

		prune_device_data(device)
		device["attributes"] = translated_attributes

		if device.get("schedules"):
			thermostat_repack_schedules(device)

		valid_devices.append(device)

	return valid_devices

def thermostat_build_command(command_data):
	return build_command(command_data, INTEGER_ATTRIBUTE_VALUES, FLOAT_ATTRIBUTE_VALUES)

def command(request_params):
	command_data = request_params.get("command")

	try:
		command_packet = thermostat_build_command(command_data)
	except Exception as e:
		return error_response(E_REQUEST_FAILED, "Failed to build thermostat command.", e)

	return base.command(request_params, command_packet, thermostat_processor)

def thermostat_repack_schedules(device):
	def schedule_processor(attr, value):
		if attr == device_defs.attribute_id("THERMOSTAT_ATTR_TARGET_TEMPERATURE"):
			return ("target_temperature", int32_to_float(value))

	for schedule in device["schedules"]:
		repack_schedule(schedule, schedule_processor)

def handle_request(request):
	directive = request.get("directive")
	request_params = request.get("parameters")

	request_params["device-type"] = device_defs.device_type_id("DEVICE_TYPE_THERMOSTAT")

	match directive:
		case "fetch":
			return base.fetch(request_params, thermostat_processor)
		case "command":
			return command(request_params)
		case _:
			return error_response(E_INVALID_REQUEST, ("Missing" if not directive else "Invalid") + " directive.")
