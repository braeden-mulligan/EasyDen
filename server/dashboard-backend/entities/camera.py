from common.defines import *
from common.utils import error_response, int32_to_float
from common import device_definitions as device_defs
from . import base_device as base
from .base_device import repack_float_attribute, repack_int_attribute, build_command, prune_device_data, repack_schedule

#define CAMERA_ATTR_NOTIFICATIONS_GLOBAL 0x80
#define CAMERA_ATTR_NOTIFY_MOTION_START 0x81
#define CAMERA_ATTR_NOTIFY_FILE_READY 0x82
#define CAMERA_ATTR_NOTIFY_INCLUDE_ATTACHMENT 0x83
#define CAMERA_ATTR_CAMERA_STATE 0x84
#define CAMERA_ATTR_MOTION_DETECT_ENABLED 0x85
#define CAMERA_ATTR_IDLE_RETURN_DELAY 0x87
#define CAMERA_ATTR_MIN_IDLE_TIME 0x88
#define CAMERA_ATTR_CAPTURE_STILL 0x89
#define CAMERA_ATTR_MAX_RECORDING_TIME 0x8A
#define CAMERA_ATTR_MOTION_SENSITIVITY 0x8B
FLOAT_ATTRIBUTE_VALUES = [
]

INTEGER_ATTRIBUTE_VALUES = [
	device_defs.attribute_id("CAMERA_ATTR_CAMERA_STATE"),
	device_defs.attribute_id("CAMERA_ATTR_MOTION_DETECT_ENABLED")
]

def camera_processor(cameras):
	valid_devices = []
	for device in cameras:
		if not device["initialized"]:
			continue

		translated_attributes = {}
		translated_attributes["enabled"] = repack_int_attribute("GENERIC_ATTR_ENABLE", device["attributes"])
		translated_attributes["status"] = repack_int_attribute("CAMERA_ATTR_CAMERA_STATE", device["attributes"])
		translated_attributes["motion_detect_enabled"] = repack_int_attribute("CAMERA_ATTR_MOTION_DETECT_ENABLED", device["attributes"])

		prune_device_data(device)
		device["attributes"] = translated_attributes

		if device.get("schedules"):
			camera_repack_schedules(device)

		valid_devices.append(device)

	return valid_devices

def camera_build_command(command_data):
	return build_command(command_data, INTEGER_ATTRIBUTE_VALUES, FLOAT_ATTRIBUTE_VALUES)

def command(request_params):
	command_data = request_params.get("command")

	try:
		command_packet = camera_build_command(command_data)
	except Exception as e:
		return error_response(E_REQUEST_FAILED, "Failed to build thermostat command.", e)

	return base.command(request_params, command_packet, camera_processor)

def camera_repack_schedules(device):
	pass

def handle_request(request):
	directive = request.get("directive")
	request_params = request.get("parameters")

	request_params["device-type"] = device_defs.device_type_id("DEVICE_TYPE_CAMERA")

	match directive:
		case "fetch":
			return base.fetch(request_params, camera_processor)
		case "command":
			return command(request_params)
		case _:
			return error_response(E_INVALID_REQUEST, ("Missing" if not directive else "Invalid") + " directive.")
