from flask import render_template, request, url_for
from . import dashboard_app

from .server_interconnect import data_transaction
from module_manager.device import SH_Device

import json, time

def error_check(transaction_result):
	if "ERROR" in transaction_result:
		#do stuff?
		return render_template("error.html", message=transaction_result)
		#return transaction_result
	return None

@dashboard_app.route("/error")
def error():
	return render_template("error.html")

@dashboard_app.route("/")
def index():
	return render_template("home.html", title="Dashboard")

@dashboard_app.route("/thermostat")
def thermostat():
	return str(SH_Device.SH_TYPE_THERMOSTAT)
	#return "Thermostat not yet available."

@dashboard_app.route("/irrigator")
def irrigator():
	return "Irrigation not yet available"

@dashboard_app.route("/poweroutlet", methods=["GET", "POST"])
def poweroutlet():
	devices = []
	device_json_raw = data_transaction("fetch")
	
	error = error_check(device_json_raw)
	if error:
		return error

	return device_json_raw
	devices = json.loads(device_json_raw)

	power_outlets = []

	for d in devices:
		if d["device_type"] == str(SH_Device.SH_TYPE_POWEROUTLET):
			pass

#TODO: make general requests.
#TODO: Debug only
	p_regs = {}
	if power_outlets:
		p_id = power_outlets[0]["device_id"]
		p_regs = power_outlets[0]["registers"]

	state = 0
	if p_id:
		if p_regs[str(SH_Device.POWEROUTLET_REG_STATE)] == 65535:
			state = 1
		elif p_regs[str(SH_Device.POWEROUTLET_REG_STATE)] == 65280:
			state = 0
		else:
			state = 2

	if request.method == "GET":
		if p_id and state == 2:
			data_transaction("debug get " + str(p_id))
			time.sleep(0.5)
			return render_template("poweroutlet.html", title="Smart Outlet", devices=[{p_id:state}])
		else:
			s_state = "UNKNOWN"
			if state == 1:
				s_state = "ON"
			elif state == 0:
				s_state = "OFF"

			outlets = [{"Outlet ID: " + str(p_id): s_state}]
			return render_template("poweroutlet.html", title="Smart Outlet", devices=[{p_id:state}])

	if request.method == "POST":
		if p_id:
			data_transaction("debug set " + str(p_id) + " " + str(state))

		time.sleep(0.5)
		devices = json.loads(data_transaction("fetch"))
		return render_template("poweroutlet.html", title="Smart Outlet", devices=power_outlets)

@dashboard_app.route("/debug", methods=["GET", "POST"])
def debug():
	return "Debug page."
