from flask import redirect, render_template, request, url_for
from . import dashboard_app

from . import server_interconnect as si 
from module_manager.device import SH_Device
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
		
@dashboard_app.route("/device/refresh", methods=["GET"])
def device_refresh():
#TODO: Could do more data validation
	category = request.args.get("category", "")
	query = "fetch " + category

	if category == "type" or category == "id":
		device_selector = request.args.get("selector")
		if not device_selector:
#TODO more comprehensive error handling.
			return render_template("error.html", message = "Invalid query")
		else:
			query += " " + device_selector
	elif category == "all":
		pass
	else:
		return render_template("error.html", message = "Invalid query")

	si_response = si.data_transaction(query)
	label, response = si.parse_response(si_response)

	devices = []
	if label == si.RESPONSE_JSON:
		devices = response
	else:
		return render_template("error.html", message = si.compose_error_log(label, si_response))
	return json.dumps(devices)

@dashboard_app.route("/device/command", methods=["POST"])
def device_command():
	return "success"

@dashboard_app.route("/device/irrigator")
def irrigator():
	return "Irrigation not yet available"

@dashboard_app.route("/device/thermostat")
def thermostat():
	return str(SH_Device.SH_TYPE_THERMOSTAT)
	#return "Thermostat not yet available."

@dashboard_app.route("/device/poweroutlet", methods=["GET"])
def poweroutlet():
	return render_template("poweroutlet.html", title="Smart Outlet")

