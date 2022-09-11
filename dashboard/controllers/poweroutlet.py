from flask import request

from dashboard import server_interconnect as interconnect
from dashboard import utilities as utils

import device_manager.device_definitions as dm_defs
import device_manager.messaging_interchange as interchange

import json

def fetch(request):
	device_id = request.args.get("id")
	response_label, poweroutlets = interconnect.fetch_devices(device_id, dm_defs.type_id("SH_TYPE_POWEROUTLET"))

	if response_label != "JSON":
		return utils.compose_response(response_label, poweroutlets)

	valid_devices = []
	for p in poweroutlets:
		if not p["initialized"]:
			continue

		socket_count = interchange.reg_to_int(p["registers"], "POWEROUTLET_REG_SOCKET_COUNT")
		if socket_count is None:
			continue

		outlet_state_attr = utils.unpack_reg_attribute(p["registers"], "POWEROUTLET_REG_STATE")
		if not outlet_state_attr:
			continue

		utils.prune_device_data(p)

		outlet_state_attr["value"] = interchange.poweroutlet_read_state(outlet_state_attr["value"], socket_count)
		p["socket_states"] = outlet_state_attr

		valid_devices.append(p);

	return utils.compose_response(response_label, json.dumps(valid_devices))

def command(request):
	device_id = request.args.get("id")
	socket_vals = [int(val) for val in request.data.decode().split(',')]
	cmd = interchange.poweroutlet_set_state(socket_vals)
	print("Issue command: " + cmd);
	resp = interconnect.data_transaction(interconnect.device_command(device_id, cmd))
	return resp
