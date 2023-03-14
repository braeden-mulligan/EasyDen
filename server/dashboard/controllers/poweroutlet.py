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



#TODO: Generify with thermostat
		for i, schedule in enumerate(device["schedules"]):
			tag = schedule
			_, register, value = tag["command"].split(',')
			register = int(register, 16)

			if register == utils.register_id("POWEROUTLET_REG_STATE"):
				socket_state = interchange.reg_to_int({ str(register): { "value": value }}, reg_id = register)		
				socket_values = interchange.poweroutlet_read_state(socket_state, device["attributes"]["socket_count"]["value"])
			else:
				continue

			device["schedules"][i] = { "attribute": "socket_states", "value": socket_values, "id_tag": tag }



		utils.prune_device_data(device)
		valid_devices.append(device);

	return valid_devices

def fetch(request):
	return base.fetch(request, poweroutlet_processor, "SH_TYPE_POWEROUTLET")

def command(request):
	message = None
	command_data = json.loads(request.data.decode())
	register = int(command_data["register"])

	if register == utils.register_id("GENERIC_REG_ENABLE"):
		message = interchange.build_command_from_int(register, int(command_data["data"]))
	elif register == utils.register_id("POWEROUTLET_REG_STATE"):
		socket_vals = [int(val) for val in command_data["data"]]
		message = interchange.poweroutlet_set_state(socket_vals)
	else:
		return base.error({ "error": None })

	return base.command(request, register, message, poweroutlet_processor, "SH_TYPE_POWEROUTLET")

def set_schedule(request):
	schedule_data = json.loads(request.data.decode())
		
	if schedule_data["action"] == "create":
		socket_vals = [int(val) for val in schedule_data["data"]]
		message = interchange.poweroutlet_set_state(socket_vals)
		del schedule_data["register"]
		del schedule_data["data"]

		schedule_data["command"] = message
		print(schedule_data)
	elif schedule_data["action"] == "delete":
		pass

	return base.set_schedule(request, json.dumps(schedule_data), poweroutlet_processor, "SH_TYPE_POWEROUTLET")