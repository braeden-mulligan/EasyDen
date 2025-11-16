import common.device_protocol_helpers as device_protocol

from common.defines import *
from common.utils import error_response
from common import device_definitions as device_defs
from . import base_device as base
from .base_device import repack_int_attribute, build_command, prune_device_data, repack_schedule

def poweroutlet_processor(poweroutlets):
	valid_devices = []

	for device in poweroutlets:
		if not device["initialized"]:
			continue

		translated_attributes = {}
		translated_attributes["enabled"] = repack_int_attribute("GENERIC_ATTR_ENABLE", device["attributes"])
		translated_attributes["socket_count"] = repack_int_attribute("POWEROUTLET_ATTR_SOCKET_COUNT", device["attributes"])

		outlet_state = repack_int_attribute("POWEROUTLET_ATTR_STATE", device["attributes"])
		outlet_state["value"], _ = device_protocol.poweroutlet_read_state(outlet_state["value"], translated_attributes["socket_count"]["value"])
		translated_attributes["socket_states"] = outlet_state

		prune_device_data(device)
		device["attributes"] = translated_attributes

		if device.get("schedules"):
			poweroulet_repack_schedules(device)

		valid_devices.append(device)

	return valid_devices

def poweroutlet_build_command(command_data):
	command_packet = build_command(command_data, [], [])

	if int(command_data["attribute-id"]) == device_defs.attribute_id("POWEROUTLET_ATTR_STATE"):
		command_packet = device_protocol.poweroutlet_set_state(command_data["attribute-value"])

	return command_packet

def command(request_params):
	command_data = request_params.get("command")

	try:
		command_packet = poweroutlet_build_command(command_data)
	except Exception as e:
		return error_response(E_REQUEST_FAILED, "Failed to build poweroutlet command.", e)

	return base.command(request_params, command_packet, poweroutlet_processor)

def poweroulet_repack_schedules(device):
	def schedule_processor(attr, value):
		if attr == device_defs.attribute_id("POWEROUTLET_ATTR_STATE"):
			socket_count = device["attributes"]["socket_count"]["value"]
			socket_values, socket_selection = device_protocol.poweroutlet_read_state(value, socket_count)

			for i, entry in enumerate(socket_selection):
				if not entry:
					socket_values[i] = None

			return ("socket_states", socket_values)

	for schedule in device["schedules"]:
		repack_schedule(schedule, schedule_processor)

def handle_request(request):
	directive = request.get("directive")
	request_params = request.get("parameters") 

	request_params["device-type"] = device_defs.device_type_id("DEVICE_TYPE_POWEROUTLET")

	match directive:
		case "fetch":
			return base.fetch(request_params, poweroutlet_processor)
		case "command":
			return command(request_params)
		case _:
			return error_response(E_INVALID_REQUEST, ("Missing" if not directive else "Invalid") + " directive.")
