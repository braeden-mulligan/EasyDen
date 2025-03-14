from common.defines import *
from common.utils import error_response
from common import device_definitions as device_defs
from .thermostat import thermostat_build_command
from .poweroutlet import poweroutlet_build_command
from ..server_interconnect import interconnect_transact

def create_schedule(request_params):
	"""
		params.schedule: {
			"recurring": bool,
			"time": {
				"hour": int,
				"minute": int,
				"days": string - eg. "mon,thu,sat"
			},
			command:{
				"attribute-id",
				"attribute-value"
			},
			"pause": int
		}
	"""
	device_id = request_params.get("device-id")
	device_type = request_params.get("device-type")
	schedule_data = request_params.get("schedule")

	formatted_command = None

	if device_type == device_defs.device_type_id("DEVICE_TYPE_THERMOSTAT"):
		formatted_command = thermostat_build_command(schedule_data.get("command"))
	
	if device_type == device_defs.device_type_id("DEVICE_TYPE_POWEROUTLET"):
		formatted_command = poweroutlet_build_command(schedule_data.get("command"))

	schedule_data["command"] = formatted_command

	return interconnect_transact({
		"entity": "schedule",
		"directive": "create",
		"parameters": {
			"device-id": device_id,
			"schedule": schedule_data
		}
	})


def delete_schedule(request_params):
	return interconnect_transact({
		"entity": "schedule",
		"directive": "delete",
		"parameters": request_params
	})


def handle_request(request):
	directive = request.get("directive")
	request_params = request.get("parameters") 

	match directive:
		case "create":
			return create_schedule(request_params)
		case "delete":
			return delete_schedule(request_params)
		case _:
			return error_response(E_INVALID_REQUEST, ("Missing" if not directive else "Invalid") + " directive.")