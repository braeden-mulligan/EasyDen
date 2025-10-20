import subprocess, json, os
from common.utils import error_response, load_json_file
from common.defines import E_REQUEST_FAILED

API_KEYS_PATH = os.path.dirname(os.path.realpath(__file__)) + "/../../../secrets.json"

api_keys = load_json_file(API_KEYS_PATH).get("api_keys", {})

OPEN_WEATHER_API_KEY = api_keys.get("open_weather")
DEFAULT_LAT = 49.24375
DEFAULT_LON = -122.85050

def fetch(lat, lon):
	if lat is None or lon is None:
		lat = DEFAULT_LAT
		lon = DEFAULT_LON

	if not OPEN_WEATHER_API_KEY:
		return error_response(E_REQUEST_FAILED, "OpenWeather API key not found.")

	weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPEN_WEATHER_API_KEY}&units=metric"
	forcast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPEN_WEATHER_API_KEY}&units=metric"

	weather = subprocess.run(["curl", weather_url, "--max-time", "10"], capture_output = True, text = True)
	forecast = subprocess.run(["curl", forcast_url, "--max-time", "10"], capture_output = True, text = True)

	if weather.returncode == 0 and forecast.returncode == 0:
		return {
			"current": json.loads(weather.stdout),
			"forecast": json.loads(forecast.stdout)
		}

	error_details = {}

	if weather.returncode != 0:
		error_details["weather"] = weather.stderr
	if forecast.returncode != 0:
		error_details["forecast"] = forecast.stderr

	return error_response(E_REQUEST_FAILED, error_details)

