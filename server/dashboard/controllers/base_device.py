from flask import request, Response

from dashboard import server_interconnect as interconnect
from dashboard import utilities as utils

import device_manager.device_definitions as dm_defs

import json, time

def fetch(request, processor, type_label):
	device_id = request.args.get("id")

	response_label, devices = interconnect.fetch_devices(device_id, device_type = dm_defs.type_id(type_label))

	if response_label != "JSON":
		return utils.compose_response(response_label, devices)
	
	return Response(response = json.dumps(processor(devices)), mimetype = "application/json")

def command(request, packet, type_label):
	device_id = request.args.get("id")

	interconnect.data_transaction(interconnect.device_command(device_id, packet))

#TODO: Clean up...
	#if request.args.get("all") = true
	# submit best-effort cmd
	timeout = time.monotonic() + 5.0
	while time.monotonic() < timeout: #args.get("timeout")
		time.sleep(0.15)
		_, devices = interconnect.fetch_devices(device_id) 
		if not devices:
			continue 

		last_query = devices[0]["registers"].get(request.args.get("register"), {}).get("queried_at")
		last_update = devices[0]["registers"].get(request.args.get("register"), {}).get("updated_at")
		if last_query is None or last_update is None:
			continue

		if last_update > last_query:
			return Response(response = json.dumps(devices), mimetype = "application/json");

	return "{ \"error\": \"Device could not be reached.\" }"