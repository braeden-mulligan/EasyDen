from flask import redirect, render_template, request, url_for

from dashboard import dashboard_app

import debug as dev
import server_interconnect as interconnect 

import controllers.thermostat as thermostat
import controllers.poweroutlet as poweroutlet
import controllers.irrigation as irrigation

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

@dashboard_app.route("/debug/message", methods=["GET", "POST"])
def debug():
	print(str(request.get_data()))
	if request.method == "GET":
		return render_template("debug.html")
	elif request.method == "POST":
		debug_text = request.form["debug-input"]
		response = interconnect.data_transaction(debug_text)
		return render_template("debug.html", response = response)

@dashboard_app.route("/debug/thermostat/refresh", methods=["GET"])
def debug_thermostat_fetch():
	return dev.thermostat_fetch()

# @dashboard_app.route("/debug/thermostat/command", methods=["PUT"])
# def debug_thermostat_fetch():
#	return dev.thermostat_command()

@dashboard_app.route("/debug/poweroutlet/refresh", methods=["GET"])
def debug_poweroutlet_fetch():
	return dev.poweroutlet_fetch()

# @dashboard_app.route("/debug/thermostat/command", methods=["PUT"])
# def debug_thermostat_fetch():
# 	return dev.poweroutlet_command()


@dashboard_app.route("/device/irrigation", methods=["GET"])
def irrigation_dash():
	return render_template("irrigation.html", title="Irrigation")

@dashboard_app.route("/device/irrigation/refresh", methods=["GET"])
def irrigation_fetch():
	return irrigation.fetch(request)

@dashboard_app.route("/device/irrigation/command", methods=["PUT"])
def irrigation_command():
	return irrigation.command(request)

@dashboard_app.route("/device/irrigation/schedule", methods=["POST"])
def irrigation_schedule():
	return irrigation.set_schedule(request)


@dashboard_app.route("/device/thermostat", methods=["GET"])
def thermostat_dash():
	return render_template("thermostat.html", title="Thermostat")

@dashboard_app.route("/device/thermostat/refresh", methods=["GET"])
def thermostat_fetch():
	return thermostat.fetch(request)

@dashboard_app.route("/device/thermostat/command", methods=["PUT"])
def thermostat_command():
	return thermostat.command(request)

@dashboard_app.route("/device/thermostat/schedule", methods=["POST"])
def thermostat_schedule():
	return thermostat.set_schedule(request)


@dashboard_app.route("/device/poweroutlet", methods=["GET"])
def poweroutlet_dash():
	return render_template("poweroutlet.html", title="Outlets")

@dashboard_app.route("/device/poweroutlet/refresh", methods=["GET"])
def poweroutlet_fetch():
	return poweroutlet.fetch(request)

@dashboard_app.route("/device/poweroutlet/command", methods=["PUT"])
def poweroutlet_command():
	return poweroutlet.command(request)

@dashboard_app.route("/device/poweroutlet/schedule", methods=["POST"])
def poweroutlet_schedule():
	return poweroutlet.set_schedule(request)