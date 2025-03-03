import sys
sys.path.append("..")
from common.log_handler import logger as log
from .controllers import poweroutlet
from .controllers import thermostat
from .server_interconnect import message_transaction

def handle_query(request):
	"""
	{
		"entity": "irrigation" | "poweroutlet" | "thermostat" | "server" | "debug",
		"operation": "get" | "put" | "update" | "delete",
		"parameters": {
			"all": bool,
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
		case "debug":
			return message_transaction(request)
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
