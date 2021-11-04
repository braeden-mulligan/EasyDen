from flask import render_template, request
from . import dashboard_app

from module_manager.device import SH_Device

import json, socket, time

SERVER_INTERCONNECT = "/tmp/sh_server_ic"
# Temporary solution.

def data_request(msg):
	soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	soc.connect(SERVER_INTERCONNECT)
	soc.settimeout(1.0)

	soc.send(msg.encode())

	resp = ""
	try:
		resp = soc.recv(65536).decode()
		print("Server got: " + resp)
	except Exception as e:
		print(e)

	soc.shutdown(socket.SHUT_RDWR)
	soc.close()
	return resp

@dashboard_app.route("/")
def index():
	return render_template("home.html", title="Dashboard")
#	return "Home Server"

@dashboard_app.route("/thermostat")
def thermostat():
	return str(SH_Device.GENERIC_REG_NULL)
	#return "Thermostat not yet available."

@dashboard_app.route("/irrigator")
def irrigator():
	return "Irrigation not yet available"

@dashboard_app.route("/poweroutlet", methods=["GET", "POST"])
def poweroutlet():
	devices = []

	devices = json.loads(data_request("fetch"))

#TODO: make general requests.
	d_id = 0
	if devices:
		d_id = devices[0]["device_id"]

	if request.method == "GET":
		data_request("debug get " + str(d_id))
		devices = json.loads(data_request("fetch"))
		return render_template("poweroutlet.html", title="Smart Outlet", devices=devices)

	if request.method == "POST":
		if devices:
			regs = devices[0]["registers"]
			if regs["101"] == 65280: 
				value = 1
			else:
				value = 0
			data_request("debug set " + str(d_id) + " " + str(value))

		time.sleep(0.5)
		devices = json.loads(data_request("fetch"))
		return render_template("poweroutlet.html", title="Smart Outlet", devices=devices)

@dashboard_app.route("/debug", methods=["GET", "POST"])
def debug():
	return "Debug page."
