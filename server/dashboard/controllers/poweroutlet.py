from flask import request

from dashboard import utilities as utils
from dashboard.controllers import base_device as base

import device_manager.messaging_interchange as interchange

import json

def poweroutlet_processor(poweroutlets):
	valid_devices = []
	for device in poweroutlets:
		if not device["initialized"]:
			continue

		device["attributes"] = {}

		device["attributes"]["enabled"] = utils.unpack_attribute(device["registers"], "GENERIC_REG_ENABLE")
		device["attributes"]["socket_count"] = utils.unpack_attribute(device["registers"], "POWEROUTLET_REG_SOCKET_COUNT")

		outlet_state_attr = utils.unpack_attribute(device["registers"], "POWEROUTLET_REG_STATE")
		outlet_state_attr["value"] = interchange.poweroutlet_read_state(outlet_state_attr["value"], device["attributes"]["socket_count"]["value"])
		
		device["attributes"]["socket_states"] = outlet_state_attr

		def schedule_processor(register, value, device = device):
			if register == utils.register_id("POWEROUTLET_REG_STATE"):
				socket_state = interchange.reg_to_int({ str(register): { "value": value }}, reg_id = register)		
				socket_values = interchange.poweroutlet_read_state(socket_state, device["attributes"]["socket_count"]["value"])
				return ("socket_states", socket_values)

		utils.reformat_schedules(device, schedule_processor)
		utils.prune_device_data(device)

		valid_devices.append(device)

	return valid_devices

def fetch(request):
	return base.fetch(request, poweroutlet_processor, "SH_TYPE_POWEROUTLET")

def command(request):
	command_data = json.loads(request.data.decode())
	message = poweroutlet_build_command(command_data)

	if message:
		return base.command(request, command_data["register"], message, poweroutlet_processor, "SH_TYPE_POWEROUTLET")
	
	return base.error({ "error": None })

def set_schedule(request):
	return base.set_schedule(request, poweroutlet_build_command, poweroutlet_processor, "SH_TYPE_POWEROUTLET")

def poweroutlet_build_command(attribute):
	message = utils.build_command(attribute, [], [])

	if int(attribute["register"]) == utils.register_id("POWEROUTLET_REG_STATE"):
		socket_vals = [int(val) for val in attribute["attribute_data"]]
		message = interchange.poweroutlet_set_state(socket_vals)

	return message
