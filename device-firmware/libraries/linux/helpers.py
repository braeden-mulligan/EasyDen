import json, os, sys

base_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(base_path + "/../..")

from common.utils import load_json_file

def store_settings(new_settings):
	all_settings = load_json_file("settings.json")
	all_settings.update(new_settings)

	settings_file = base_path + "/../../files/json/settings.json"

	with open(settings_file, 'w') as file:
		file.write(json.dumps(all_settings, indent = '\t'))