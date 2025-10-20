import subprocess, json, os
from common.utils import error_response, load_json_file
from common.defines import E_REQUEST_FAILED

API_KEYS_PATH = os.path.dirname(os.path.realpath(__file__)) + "/../../../secrets.json"

api_keys = load_json_file(API_KEYS_PATH).get("api_keys", {})

COINGECKO_API_KEY = api_keys.get("coingecko")
TIINGO_API_KEY = api_keys.get("tiingo")

def fetch():
	if not COINGECKO_API_KEY or not TIINGO_API_KEY:
		return error_response(E_REQUEST_FAILED, "API key(s) not found.")

	bitcoin_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=cad&ids=bitcoin&{COINGECKO_API_KEY}"
	sp500_url = f"https://api.tiingo.com/tiingo/daily/spy/prices?token={TIINGO_API_KEY}"

	bitcoin_response = subprocess.run(["curl", bitcoin_url, "--max-time", "10"], capture_output = True, text = True)
	sp500_response = subprocess.run(["curl", sp500_url, "--max-time", "10"], capture_output = True, text = True)

	if bitcoin_response.returncode == 0:
		bitcoin_data = json.loads(bitcoin_response.stdout)
		if isinstance(bitcoin_data, list) and len(bitcoin_data) > 0:
			bitcoin_data = bitcoin_data[0]

	if sp500_response.returncode == 0:
		sp500_data = json.loads(sp500_response.stdout) 
		if isinstance(sp500_data, list) and len(sp500_data) > 0:
			sp500_data = sp500_data[0]

		return {
			"bitcoin-price": bitcoin_data.get("current_price"),
			"bitcoin-image-url": bitcoin_data.get("image"),
			"sp500-price": sp500_data.get("close") if sp500_data else None
		}

	error_details = {}

	if bitcoin_response.returncode != 0:
		error_details["bitcoin"] = bitcoin_response.stderr
	if sp500_response.returncode != 0:
		error_details["sp500"] = sp500_response.stderr

	return error_response(E_REQUEST_FAILED, error_details)

