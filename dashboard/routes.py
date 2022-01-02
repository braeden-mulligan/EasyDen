from flask import redirect, render_template, request, url_for
from . import dashboard_app

import module_manager.device_definitions as SH_defs
from . import server_interconnect as si 
from module_manager.messaging import *

import json, os 
 
# Circumvent browser caching 
def timestamped_url_for(endpoint, **values):
	if endpoint == 'static':
		file_name = values.get('filename', None)
		if file_name:
			file_path = os.path.join(dashboard_app.root_path, endpoint, file_name)
			values["ver"] = int(os.stat(file_path).st_mtime)
	return url_for(endpoint, **values)

@dashboard_app.context_processor
def override_url_for():
    return dict(url_for=timestamped_url_for)

@dashboard_app.route("/")
def index():
	return render_template("home.html", title = "Dashboard")

@dashboard_app.route("/error")
def error():
	return render_template("error.html")

@dashboard_app.route("/device/debug", methods=["GET", "POST"])
def debug():
	print(str(request.get_data()))
	if request.method == "GET":
		return render_template("debug.html")
	elif request.method == "POST":
		debug_text = request.form["debug-input"]
		response = si.data_transaction(debug_text)
		return render_template("debug.html", response = response)


def device_fetch(device_id = None, device_type = None):
	query = "fetch "
	if device_id:
		query += "id " + str(device_id)
	elif device_type:
		query += "type " + str(device_type)
	else:
		query += "all"

	si_response = si.data_transaction(query)
	label, response = si.parse_response(si_response)

	devices = []
	if label == si.RESPONSE_JSON:
		devices = response
	else:
		devices = None

	return devices

def prune_device_obj(device):
	del device["type"]
	del device["initialized"]
	del device["registers"]
	return

@dashboard_app.route("/device/irrigator")
def irrigator():
	return "Irrigation not yet available"

@dashboard_app.route("/device/thermostat")
def thermostat():
	return render_template("thermostat.html", title="Thermostat")

@dashboard_app.route("/device/thermostat/refresh", methods=["GET"])
def thermostat_fetch():
	device_id = request.args.get("id")
	thermostats = device_fetch(device_id, device_type = SH_defs.type_id("SH_TYPE_THERMOSTAT"))

	if thermostats is None:
		return "{\"result\": \"ERROR\"}"

	valid_devices = []
	for t in thermostats:
		if not t["initialized"]:
			continue

		t["temperature"] = reg_to_float(t["registers"], "THERMOSTAT_REG_TEMPERATURE")
		t["humidity"] = reg_to_float(t["registers"], "THERMOSTAT_REG_HUMIDITY")

		prune_device_obj(t)
		valid_devices.append(t)

	return json.dumps(valid_devices)

@dashboard_app.route("/device/thermostat/command", methods=["POST"])
def thermostat_command():
#TODO: Debugging for now
	device_id = request.args.get("id")
	si.data_transaction(si.device_command(device_id, thermostat_get_temperature()))
	si.data_transaction(si.device_command(device_id, thermostat_get_humidity()))
	return "success"
# --- ---


# --- Power ouetlet section ---
@dashboard_app.route("/device/poweroutlet", methods=["GET"])
def poweroutlet():
	return render_template("poweroutlet.html", title="Outlets")

@dashboard_app.route("/device/poweroutlet/refresh", methods=["GET"])
def poweroutlet_fetch():
	device_id = request.args.get("id")
	poweroutlets = device_fetch(device_id, SH_defs.type_id("SH_TYPE_POWEROUTLET"))

	if poweroutlets is None:
		return "{\"result\": \"ERROR\"}"

	valid_devices = []
	for p in poweroutlets:
		if not p["initialized"]:
			continue

		socket_count = reg_to_int(p["registers"], "POWEROUTLET_REG_SOCKET_COUNT")
		if not socket_count:
			socket_count = 0
			continue

		outlet_state = reg_to_int(p["registers"], "POWEROUTLET_REG_STATE")
		if not outlet_state:
			outlet_state = 0
			continue

		prune_device_obj(p)

		p["socket_states"] = poweroutlet_read_state(outlet_state, socket_count)
		valid_devices.append(p);

	return json.dumps(valid_devices)

@dashboard_app.route("/device/poweroutlet/command", methods=["POST"])
def poweroutlet_command():
#TODO: Debugging for now
	device_id = request.args.get("id")
	socket_vals = [int(val) for val in request.data.decode().split(',')]
	cmd = poweroutlet_set_state(socket_vals)
	print("Issue command: " + cmd);
	si.data_transaction(si.device_command(device_id, cmd))
	return "success"
# --- ---

