from flask import render_template
from dashboard import app

@app.route("/")
def index():
	return render_template("home.html", title="Dashboard")
#	return "Home Server"

@app.route("/thermostat")
def thermostat():
	return "Thermostat Status"

@app.route("/irrigator")
def irrigator():
	return "Garden Status"

@app.route("/smartplug")
def smartplug():
	return "Smartplug Not Available"
