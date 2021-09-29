from flask import render_template
from dashboard import app

import socket

SERVER_INTERCONNECT = "/tmp/sh_server_ic"
# Temporary solution.
def data_query():
	soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	soc.connect(SERVER_INERCONNECT)
#do send,
#wait for response
	soc.shutdown(socket.SHUT_RDWR)
	soc.close()

@app.route("/")
def index():
	return render_template("home.html", title="Dashboard")
#	return "Home Server"

@app.route("/thermostat")
def thermostat():
	return "Thermostat not yet available."

@app.route("/irrigator")
def irrigator():
	return "Irrigation not yet available"

@app.route("/powersocket")
def smartplug():
	return "Return"
