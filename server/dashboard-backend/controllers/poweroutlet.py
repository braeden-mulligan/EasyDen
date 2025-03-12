import common.device_protocol_helpers as device_protocol

from common.defines import *
from common.utils import error_response
from common import device_definitions as device_defs
from ..device_helpers import *
from . import base_device as base

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

		# def schedule_processor(register, value, device = device):
		# 	if register == utils.register_id("POWEROUTLET_REG_STATE"):
		# 		socket_state = interchange.reg_to_int({ str(register): { "value": value }}, reg_id = register)		
		# 		socket_values, socket_selection = interchange.poweroutlet_read_state(socket_state, device["attributes"]["socket_count"]["value"])
		# 		for i, entry in enumerate(socket_selection):
		# 			if not entry:
		# 				socket_values[i] = None
		# 		return ("socket_states", socket_values)

		# utils.reformat_schedules(device, schedule_processor)

		prune_device_data(device)
		device["attributes"] = translated_attributes

		valid_devices.append(device)

	return valid_devices

def poweroutlet_build_command(command_data):
	command_packet = build_command(command_data, [], [])

	if int(command_data["attribute_id"]) == device_defs.attribute_id("POWEROUTLET_ATTR_STATE"):
		command_packet = device_protocol.poweroutlet_set_state(command_data["value"])

	return command_packet

def command(request_params):
	command_data = request_params.get("command")

	try:
		command_packet = poweroutlet_build_command(command_data)
	except Exception as e:
		return error_response(E_REQUEST_FAILED, "Failed to build poweroutlet command.", e)

	return base.command(request_params, command_packet, poweroutlet_processor)

# def set_schedule(request):
	# return base.set_schedule(request, poweroutlet_build_command, poweroutlet_processor, "SH_TYPE_POWEROUTLET")

def handle_request(request):
	directive = request.get("directive")
	request_params = request.get("parameters") 

	request_params["type"] = device_defs.device_type_id("DEVICE_TYPE_POWEROUTLET")

	match directive:
		case "fetch":
			return base.fetch(request_params, poweroutlet_processor)
		case "command":
			return command(request_params)
		case _:
			return error_response(E_INVALID_REQUEST, ("Missing" if not directive else "Invalid") + " directive.")
