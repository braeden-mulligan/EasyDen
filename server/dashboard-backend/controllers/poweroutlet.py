import common.device_protocol_helpers as device_protocol

from .. import server_interconnect as interconnect
from ..device_helpers import *

def poweroutlet_processor(poweroutlets):
	valid_devices = []

	for device in poweroutlets:
		if not device["initialized"]:
			continue

		device["attributes"] = {}
		device["attributes"]["enabled"] = unpack_attribute_to_int(device["attributes"], "GENERIC_ATTR_ENABLE")
		device["attributes"]["socket_count"] = unpack_attribute_to_int(device["attributes"], "POWEROUTLET_ATTR_SOCKET_COUNT")

		outlet_state = unpack_attribute_to_int(device["attributes"], "POWEROUTLET_ATTR_STATE")
		outlet_state["value"], _ = device_protocol.poweroutlet_read_state(outlet_state["value"], device["attributes"]["socket_count"]["value"])
		device["attributes"]["socket_states"] = outlet_state

		# def schedule_processor(register, value, device = device):
		# 	if register == utils.register_id("POWEROUTLET_REG_STATE"):
		# 		socket_state = interchange.reg_to_int({ str(register): { "value": value }}, reg_id = register)		
		# 		socket_values, socket_selection = interchange.poweroutlet_read_state(socket_state, device["attributes"]["socket_count"]["value"])
		# 		for i, entry in enumerate(socket_selection):
		# 			if not entry:
		# 				socket_values[i] = None
		# 		return ("socket_states", socket_values)

		# utils.reformat_schedules(device, schedule_processor)

		prune_device_data(device)

		valid_devices.append(device)

	return valid_devices

def fetch(request_data):
	device_id = request_data.get("id")
	device_type = request_data.get("type")
	include_meta_info = request_data.get("include-meta-info")

	response = interconnect.fetch_devices(device_id, device_type, include_meta_info)

	if response.result:
		response.result = poweroutlet_processor(response.result)
		return response

	if not response.error:
		return { 
			"error": {
				"code": "UNKNOWN",
			}
		}
	
	return response

def command(request_data):
	pass

def delegate_operation(request_data):
	operation = request_data.get("operation")
	match operation:
		case "get":
			return fetch(request_data)
		case "put":
			return command(request_data)
		case _:
			return {
				"error":  {
					"code": "INVALID_OPERATION",
					"details": ("Missing" if not operation else "Invalid") + " operation."
				}
			}

# def command(request):
# 	command_data = json.loads(request.data.decode())
# 	message = poweroutlet_build_command(command_data)

# 	if message:
# 		return base.command(request, command_data["register"], message, poweroutlet_processor, "SH_TYPE_POWEROUTLET")
	
# 	return base.error({ "error": None })

# def set_schedule(request):
# 	return base.set_schedule(request, poweroutlet_build_command, poweroutlet_processor, "SH_TYPE_POWEROUTLET")

# def poweroutlet_build_command(attribute):
# 	message = utils.build_command(attribute, [], [])

# 	if int(attribute["register"]) == utils.register_id("POWEROUTLET_REG_STATE"):
# 		message = interchange.poweroutlet_set_state(attribute["attribute_data"])

# 	return message
