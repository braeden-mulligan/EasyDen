from flask import redirect, render_template, request, url_for
from . import dashboard_app

from .server_interconnect import data_transaction
from module_manager.device import SH_Device
from module_manager.messaging import *

@dashboard_app.route("/thermostat")
def thermostat():
	return str(SH_Device.SH_TYPE_THERMOSTAT)
	#return "Thermostat not yet available."

