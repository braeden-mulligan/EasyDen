from flask import redirect, render_template, request, url_for
from . import dashboard_app

from . import server_interconnect as si
from module_manager.device import SH_Device
from module_manager.messaging import *

import time

@dashboard_app.route("/poweroutlet", methods=["GET", "POST"])
def poweroutlet():
	si_response = si.data_transaction("fetch type " + str(SH_Device.SH_TYPE_POWEROUTLET))
	label, response = si.parse_response(si_response)

	devices = []
	if label == si.RESPONSE_JSON:
		devices = response
	else:
		return render_template("error.html", message = si.compose_error_log(label, si_response))

#TODO: make general requests.
# If multiple devices, make sure data_transaction timeout = 0.0
	need_refresh = False
	
	for d in devices:
		if str(SH_Device.POWEROUTLET_REG_STATE) not in d["registers"]:
			si.data_transaction(si.build_command(poweroutlet_get_state(), SH_Device.SH_TYPE_POWEROUTLET))
			need_refresh = True

	if request.method == "GET":
		if need_refresh:
			time.sleep(0.5)
			return redirect(url_for("poweroutlet"))
		else:
			return render_template("poweroutlet.html", title="Smart Outlet", devices = devices)

	if request.method == "POST":
		time.sleep(0.5)
		return redirect(url_for("poweroutlet"))

