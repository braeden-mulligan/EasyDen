import sys
sys.path.append("..")
from common.log_handler import logger as log
# from .controllers import base_device as base
from .controllers import poweroutlet
# from .controllers import thermostat

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
				"attribute": string,
				"value": object
			},
			"config": "string",
			"schedule": bool
			"data": object,
		}
	}
	"""

	log.debug(request)

	entity = request.get("entity")
	match entity:
		case "irrigation":
			pass
		case "poweroutlet":
			return  poweroutlet.delegate_operation(request)
		case "thermostat":
			pass
			# return thermostat.fetch()
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
