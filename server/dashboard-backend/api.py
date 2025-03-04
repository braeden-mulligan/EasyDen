import sys
sys.path.append("..")
from common.log_handler import logger as log
from .controllers import poweroutlet
from .controllers import thermostat
from .server_interconnect import interconnect_transact

def handle_query(request):
	"""
	request format:
	{
		"entity": "irrigation" | "poweroutlet" | "thermostat" | "schedule" | "config",
		"directive": "fetch" | "command" | "put" | "update" | "delete",
		"parameters": {
			"id": string,
			"type": string,
			"name": string,
			"command": {
				"attribute_id": int,
				"value": object
			},
			"config": "string",
			"schedule": 
			"data": object,
			"timeout": number
		}
	}
	"""

	log.debug(request)

	if request.get("debug-passthrough"):
		return interconnect_transact(request)

	match request.get("entity"):
		case "irrigation":
			pass
		case "poweroutlet":
			return  poweroutlet.handle_request(request)
		case "thermostat":
			return thermostat.handle_request(request)
		case "schedule":
			pass
		case "server":
			pass
		case _:
			return {
				"error": {
					"code": "INVALID_REQUEST",
					"details": "Unknown entity specified."
				}
			}
	
	return {
		"error": {
			"code": "UNKNOWN",
			"details": "Unknown error occurred."
		}
	}
