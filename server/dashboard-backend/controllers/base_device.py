import sys
sys.path.append("..")

from common.defines import *
from common.utils import error_response
from common import server_config as config
from .. import server_interconnect as interconnect

import time

def fetch(request_params, device_data_processor):
	response = interconnect.fetch_devices(request_params)

	if response.get("result") is not None:
		response["result"] = device_data_processor(response["result"])
		return response

	if response.get("error") is None:
		return error_response()
	
	return response

# NOTE: Only supports one device at a time for now
def command(request_params, command_packet, device_data_processor):
	response = interconnect.send_device_command(command_packet, request_params)

	if response.get("error"):
		return response

	timeout = time.monotonic() + (request_params.get("timeout") or (config.TX_TIMEOUT * (config.MAX_TX_RETRIES  + 1) + 1.0))

	while time.monotonic() < timeout:
		time.sleep(0.15)
		devices = interconnect.fetch_devices(request_params).get("result")
		if not devices:
			continue 

		target_attribute = int(command_packet.split(",")[1], 16)

		last_query = devices[0]["attributes"].get(str(target_attribute), {}).get("queried_at")
		last_update = devices[0]["attributes"].get(str(target_attribute), {}).get("updated_at")

		if last_query is None or last_update is None:
			continue

		if last_update > last_query:
			return {
				"result": device_data_processor(devices)
			}

	return error_response(E_TIMEOUT, "Device response could not be confirmed.")

