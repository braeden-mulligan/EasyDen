import sys
sys.path.append("..")

from common import server_config as config

from .. import server_interconnect as interconnect
# from dashboard import utilities as utils

import time

def fetch_device(request, processor):
	# device_id = request.get("id")
	devices = interconnect.fetch_devices(meta_info = True)

	return processor(devices)

def command(request, packet, processor):
	device_id = request.get("id")

	interconnect.send_device_command(device_id, packet)

#TODO: Clean up...
	#if request.args.get("all") == true
	# submit best-effort cmd
	# else
	timeout = time.monotonic() + (request.args.get("timeout") or (config.TX_TIMEOUT * (config.MAX_TX_RETRIES  + 1) + 1.0))
	while time.monotonic() < timeout:
		time.sleep(0.15)
		devices = interconnect.fetch_devices(device_id).get("result")
		if not devices:
			continue 

	#TODO: get target from packet
		last_query = devices[0]["attributes"].get(str(target_register), {}).get("queried_at")
		last_update = devices[0]["attributes"].get(str(target_register), {}).get("updated_at")
		if last_query is None or last_update is None:
			continue

		if last_update > last_query:
			return processor(devices)

	return {
		"error": {
			"code": "TIMEOUT",
			"details": "Device could not be reached."
		}
	}

# def set_schedule(request, command_builder, processor, type_label):
# 	data = json.loads(request.data.decode())

# 	if data["action"] == "create":
# 		data["command"] = command_builder(data)

# 	data.pop("register", None)
# 	data.pop("attribute_data", None)

# 	schedule_data = json.dumps(data)
# 	print("Setting schedule:", schedule_data)

# 	device_id = request.args.get("id")
# 	interconnect.data_transaction(interconnect.device_schedule(device_id, schedule_data))
# 	response_label, devices = interconnect.fetch_devices(device_id, device_type_label = type_label)
	
# 	return Response(response = json.dumps(processor(devices)), mimetype = "application/json")

# def error(message):
# 	data = {"error": message}
# 	return Response(response = json.dumps(data), mimetype = "application/json")
