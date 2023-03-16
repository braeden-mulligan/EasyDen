from flask import request, Response

from device_manager import config as dm_config
from dashboard import server_interconnect as interconnect
from dashboard import utilities as utils

import json, time

def fetch(request, processor, type_label):
	device_id = request.args.get("id")

	response_label, devices = interconnect.fetch_devices(device_id, device_type_label = type_label)

	if response_label != "JSON":
		return utils.compose_response(response_label, devices)
	
	return Response(response = json.dumps(processor(devices)), mimetype = "application/json")

def command(request, target_register, packet, processor, type_label):
	device_id = request.args.get("id")

	interconnect.data_transaction(interconnect.device_command(device_id, packet))

#TODO: Clean up...
	#if request.args.get("all") == true
	# submit best-effort cmd
	# else
	timeout = time.monotonic() + (request.args.get("timeout") or (dm_config.DEVICE_TX_TIMEOUT * (dm_config.DEVICE_MAX_TX_RETRIES  + 1) + 1.0))
	while time.monotonic() < timeout:
		time.sleep(0.15)
		_, devices = interconnect.fetch_devices(device_id) 
		if not devices:
			continue 

		last_query = devices[0]["registers"].get(str(target_register), {}).get("queried_at")
		last_update = devices[0]["registers"].get(str(target_register), {}).get("updated_at")
		if last_query is None or last_update is None:
			continue

		if last_update > last_query:
			return Response(response = json.dumps(processor(devices)), mimetype = "application/json")

	return error("Device could not be reached")

def set_schedule(request, data, command_builder, processor, type_label):		
	if data["action"] == "create":
		data["command"] = command_builder(data)

	data.pop("register", None)
	data.pop("attribute_data", None)

	schedule_data = json.dumps(data)
	print("Setting schedule:", schedule_data)

	device_id = request.args.get("id")
	interconnect.data_transaction(interconnect.device_schedule(device_id, schedule_data))
	response_label, devices = interconnect.fetch_devices(device_id, device_type_label = type_label)
	
	return Response(response = json.dumps(processor(devices)), mimetype = "application/json")

def error(message):
	data = {"error": message}
	return Response(response = json.dumps(data), mimetype = "application/json")
