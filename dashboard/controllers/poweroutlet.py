from flask import request

from dashboard import server_interconnect as interconnect
from dashboard import utilities as utils

import device_manager.device_definitions as dm_defs
import device_manager.messaging as dm_messaging

import json

def fetch(request):
	device_id = request.args.get("id")
	poweroutlets = interconnect.fetch_devices(device_id, dm_defs.type_id("SH_TYPE_POWEROUTLET"))

	if poweroutlets is None:
		return "{\"result\": \"ERROR\"}"

	valid_devices = []
	for p in poweroutlets:
		if not p["initialized"]:
			continue

		socket_count = dm_messaging.reg_to_int(p["registers"], "POWEROUTLET_REG_SOCKET_COUNT")
		if not socket_count:
			socket_count = 0
			continue

		outlet_state = dm_messaging.reg_to_int(p["registers"], "POWEROUTLET_REG_STATE")
		if not outlet_state:
			outlet_state = 0
			continue

		utils.prune_device_obj(p)

		p["socket_states"] = dm_messaging.poweroutlet_read_state(outlet_state, socket_count)
		valid_devices.append(p);

	return json.dumps(valid_devices)

def command(request):
#TODO: Debugging for now
	device_id = request.args.get("id")
	socket_vals = [int(val) for val in request.data.decode().split(',')]
	cmd = dm_messaging.poweroutlet_set_state(socket_vals)
	print("Issue command: " + cmd);
	resp = interconnect.data_transaction(interconnect.device_command(device_id, cmd))
	return resp
