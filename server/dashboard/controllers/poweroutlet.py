from flask import request

from dashboard import utilities as utils
from dashboard.controllers import base_device as base

import device_manager.messaging_interchange as interchange

import json

def poweroutlet_processor(poweroutlets):
	valid_devices = []
	for p in poweroutlets:
		if not p["initialized"]:
			continue

		p["attributes"] = {}

		p["attributes"]["enabled"] = utils.unpack_attribute(p["registers"], "GENERIC_REG_ENABLE")
		p["attributes"]["socket_count"] = utils.unpack_attribute(p["registers"], "POWEROUTLET_REG_SOCKET_COUNT")

		outlet_state_attr = utils.unpack_attribute(p["registers"], "POWEROUTLET_REG_STATE")
		outlet_state_attr["value"] = interchange.poweroutlet_read_state(outlet_state_attr["value"], p["attributes"]["socket_count"]["value"])
		
		p["attributes"]["socket_states"] = outlet_state_attr



#TODO: Generify with thermostat
		for i, schedule in enumerate(p["schedules"]):
			tag = schedule
			_, register, value = tag["command"].split(',')
			register = int(register, 16)

			if register == utils.register_id("POWEROUTLET_REG_STATE"):
				socket_state = interchange.reg_to_int({ str(register): { "value": value }}, reg_id = register)		
				socket_values = interchange.poweroutlet_read_state(socket_state, p["attributes"]["socket_count"]["value"])
			else:
				continue

			p["schedules"][i] = { "attribute": "socket_states", "value": socket_values, "id_tag": tag }



		utils.prune_device_data(p)
		valid_devices.append(p);

	return valid_devices

def fetch(request):
	return base.fetch(request, poweroutlet_processor, "SH_TYPE_POWEROUTLET")

def command(request):
	message = None
	command_data = json.loads(request.data.decode())
	register = int(command_data["register"])

	if register == utils.register_id("GENERIC_REG_ENABLE"):
		message = interchange.command_from_int(register, int(command_data["data"]))
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