from common import defines, utils
from ..services import weather, market

def handle_request(request):
	directive = request.get("directive")
	request_params = request.get("parameters") 

	match directive:
		case "fetch":
			if "weather" in request_params.get("service", ""):
				return weather.fetch(request_params.get("latitude"), request_params.get("longitude"))
			elif "market" in request_params.get("service", ""):
				return market.fetch()
	
			return utils.error_response(defines.E_INVALID_REQUEST, "Invalid service specified in fetch directive.")

		case "config-get":
			return utils.error_response(defines.E_UNIMPLEMENTED)

		case "config-set":
			return utils.error_response(defines.E_UNIMPLEMENTED)

		case _:
			return utils.error_response(defines.E_INVALID_REQUEST, ("Missing" if not directive else "Invalid") + " directive.")
