import sys
sys.path.append("..")
from common import defines, utils
from common.log_handler import logger as log
from .controllers import poweroutlet
from .controllers import thermostat
from .controllers import schedules
from .server_interconnect import interconnect_transact

def handle_query(request):
	"""
	Request formats. Not all listed parameters are required; their presence depends 
	 on the specific entity and directive combination.

	{
		entity: "irrigation" | "poweroutlet" | "thermostat",
		directive: "fetch" | "command" | "update",
		parameters: {
			device-id: int | string,
			device-type: int | string,
			command: {
				attribute-id: int,
				attribute-value: any
			},
			timeout: number
			name: string
		}
	}

	{
		entity: "schedule" ,
		directive: "create" | "delete" | "edit",
		parameters: {
			schedule-id: int,
			device-id: int,
			device-type: int,
			schedule:{
				recurring: true,
				time:{
					hour: int,
					minute: int,
					days: string
			},
			"command":{
				"attribute-id": int,
				"attribute-value": any
			},
			pause: int
		}
    }
		
	{
		entity: "server",
		directive: "config-get" | "config-set",
		parameters: {
			device-id: string
			name: string
			log-level: string
			tx-queue-retention: int
			device-keepalive: int
		}
	}
	"""

	try: 
		if request.get("parameters") is None:
			request["parameters"] = {}

		log.debug(request)

		if request.get("debug-passthrough"):
			return interconnect_transact(request)

		match request.get("entity"):
			case "irrigation":
				return utils.error_response(defines.E_UNIMPLEMENTED)
			case "poweroutlet":
				return poweroutlet.handle_request(request)
			case "thermostat":
				return thermostat.handle_request(request)
			case "schedule":
				return schedules.handle_request(request)
			case "server":
				return utils.error_response(defines.E_UNIMPLEMENTED)
			case _:
				return utils.error_response(defines.E_INVALID_REQUEST, "Unknown entity specified.")

	except Exception as e:
		log.exception("Unhandled exception")
		return utils.error_response(defines.E_UNKNOWN, "Unhandled server error", e)
