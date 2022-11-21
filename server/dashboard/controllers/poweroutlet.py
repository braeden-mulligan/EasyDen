from flask import request

from dashboard import utilities as utils
from dashboard.controllers import base_device as base

import device_manager.messaging_interchange as interchange

def poweroutlet_processor(poweroutlets):
	valid_devices = []
	for p in poweroutlets:
		if not p["initialized"]:
			continue

		p["attributes"] = {}

		socket_count = interchange.reg_to_int(p["registers"], "POWEROUTLET_REG_SOCKET_COUNT")
		if socket_count is None:
			continue

		outlet_state_attr = utils.unpack_attribute(p["registers"], "POWEROUTLET_REG_STATE")
		if not outlet_state_attr:
			continue

		outlet_state_attr["value"] = interchange.poweroutlet_read_state(outlet_state_attr["value"], socket_count)
		p["attributes"]["socket_states"] = outlet_state_attr

		utils.prune_device_data(p)
		valid_devices.append(p);

	return valid_devices

def fetch(request):
	return base.fetch(request, poweroutlet_processor, "SH_TYPE_POWEROUTLET")

def command(request):
	message = None
	register = int(request.args.get("register"))

	if register == utils.register_id("GENERIC_REG_ENABLE"):
		interchange.command_from_int(int(request.data.decode()))
	elif register == utils.register_id("POWEROUTLET_REG_STATE"):
		socket_vals = [int(val) for val in request.data.decode().split(',')]
		message = interchange.poweroutlet_set_state(socket_vals)
	else:
		return "{ \"error\": null }"

	return base.command(request, message, "SH_TYPE_POWEROUTLET")
