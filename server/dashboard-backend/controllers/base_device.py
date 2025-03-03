import sys
sys.path.append("..")

from common import server_config as config
from .. import server_interconnect as interconnect

import time

def fetch(request_data, device_data_processor):
	device_id = request_data.get("id")
	device_type = request_data.get("type")
	include_meta_info = request_data.get("include-meta-info")

	response = interconnect.fetch_devices(device_id, device_type, include_meta_info)

	if response["result"]:
		response["result"] = device_data_processor(response["result"])
		return response

	if not response["error"]:
		return { 
			"error": {
				"code": "UNKNOWN",
			}
		}
	
	return response

def command(request_data, command_packet, device_data_processor):
	device_id = request_data.get("id")

	response = interconnect.send_device_command(device_id, command_packet)

	if response.get("error"):
		return response

	timeout = time.monotonic() + (request_data.get("timeout") or (config.TX_TIMEOUT * (config.MAX_TX_RETRIES  + 1) + 1.0))

	while time.monotonic() < timeout:
		time.sleep(0.15)
		devices = interconnect.fetch_devices(device_id).get("result")
		if not devices:
			continue 

		target_attribute = int(command_packet.split(",")[1], 16)

		last_query = devices[0]["attributes"].get(str(target_attribute), {}).get("queried_at")
		last_update = devices[0]["attributes"].get(str(target_attribute), {}).get("updated_at")

		if last_query is None or last_update is None:
			continue

		if last_update > last_query:
			return device_data_processor(devices)

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
