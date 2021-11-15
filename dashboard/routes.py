from flask import redirect, render_template, request, url_for
from . import dashboard_app

from .server_interconnect import data_transaction
from module_manager.device import SH_Device
from module_manager.messaging import *

import os
 
# Circumvent browser caching 
def timestamped_url_for(endpoint, **values):
	if endpoint == 'static':
		file_name = values.get('filename', None)
		if file_name:
			file_path = os.path.join(dashboard_app.root_path, endpoint, file_name)
			values['v'] = int(os.stat(file_path).st_mtime)
	return url_for(endpoint, **values)

@dashboard_app.context_processor
def override_url_for():
    return dict(url_for=timestamped_url_for)

@dashboard_app.route("/")
def index():
	return render_template("home.html", title="Dashboard")

@dashboard_app.route("/error")
def error():
	return render_template("error.html")

@dashboard_app.route("/debug", methods=["GET", "POST"])
def debug():
	return "Debug page."

@dashboard_app.route("/irrigator")
def irrigator():
	return "Irrigation not yet available"

