import sys
sys.path.append("..")
from common import defines, utils
from common.log_handler import logger as log
from .controllers import poweroutlet
from .controllers import thermostat
from .server_interconnect import interconnect_transact

def handle_query(request):
	"""
	request format:
	{
		"entity": "irrigation" | "poweroutlet" | "thermostat" | "schedule" | "config",
		"directive": "fetch" | "command" | "submit" | "update" | "delete",
		"parameters": {
			"id": int | string,
			"type": int | string,
			"name": string,
			"command": {
				"attribute_id": int,
				"value": object
			},
			"config": "string",
			"schedule": object,
			"data": object,
			"timeout": number
		}
	}
	"""

	if request.get("parameters") is None:
		request["parameters"] = {}

	log.debug(request)

	if request.get("debug-passthrough"):
		return interconnect_transact(request)

	match request.get("entity"):
		case "irrigation":
			pass
		case "poweroutlet":
			return poweroutlet.handle_request(request)
		case "thermostat":
			return thermostat.handle_request(request)
		case "schedule":
			pass
		case "server":
			pass
		case _:
			return utils.error_response(defines.E_INVALID_REQUEST, "Unknown entity specified.")
	
	return utils.error_response()
