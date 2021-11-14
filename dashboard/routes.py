from flask import redirect, render_template, request, url_for
from . import dashboard_app

from .server_interconnect import data_transaction
from module_manager.device import SH_Device
from module_manager.messaging import *

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


def debug_fetch_devices_helper():
	devices = []
	device_json_raw = data_transaction("fetch type " + str(SH_Device.SH_TYPE_POWEROUTLET))
	
	error = error_check(device_json_raw)
	if error:
		return error

	devices = json.loads(device_json_raw)
	return devices

@dashboard_app.route("/poweroutlet", methods=["GET", "POST"])
def poweroutlet():
	devices = debug_fetch_devices_helper()

#TODO: make general requests.
	d_regs = {}
	d_id = 0
	if devices:
		d_id = devices[0]["device_id"] or 0
		d_regs = devices[0]["registers"]

	state = 2
	if d_id and d_regs:
#TODO: Debug only
		print(d_regs[str(SH_Device.POWEROUTLET_REG_STATE)])
		if d_regs[str(SH_Device.POWEROUTLET_REG_STATE)] & 0x0001 == 1:
			state = 1
		elif d_regs[str(SH_Device.POWEROUTLET_REG_STATE)] & 0x0001 == 0:
			state = 0

	if request.method == "GET":
		if d_id and state == 2:
			data_transaction("command id " + str(d_id) + " " + poweroutlet_get_state())
			time.sleep(0.5)
			return redirect(url_for("poweroutlet"))
			#return render_template("poweroutlet.html", title="Smart Outlet", devices=[{d_id:state}])
		else:
			s_state = "UNKNOWN"
			if state == 1:
				s_state = "ON"
			elif state == 0:
				s_state = "OFF"
			#outlets = [{"Outlet ID: " + str(d_id): s_state}]
		return render_template("poweroutlet.html", title="Smart Outlet", devices=[{d_id:s_state}])

	if request.method == "POST":
		if d_id:
			state = not state
			data_transaction("command id " + str(d_id) + " " + poweroutlet_set_state([(0, state)]))

		time.sleep(0.5)
		#devices = debug_fetch_devices_helper()
		return redirect(url_for("poweroutlet"))
		#return render_template("poweroutlet.html", title="Smart Outlet", devices=[{d_id:state}])

@dashboard_app.route("/debug", methods=["GET", "POST"])
def debug():
	return "Debug page."
