from flask import Flask, request, Response, send_from_directory
from flask_cors import CORS
from pathlib import Path

import importlib, json
auth_module = importlib.import_module("dashboard-backend.auth")
data_api = importlib.import_module("dashboard-backend.api")
stream_module = importlib.import_module("dashboard-backend.stream")

REACT_APP_PATH = str(Path(__file__).parent) + "/dashboard-frontend/build"

dashboard_app = Flask(__name__, static_folder=REACT_APP_PATH, static_url_path="/")
auth_module.init_auth(dashboard_app)

CORS(dashboard_app, origins=["http://localhost*", "https://localhost*", "http://192.168.1.*", "https://192.168.1.*"], supports_credentials = True)

@dashboard_app.route("/", methods=["GET"])
@dashboard_app.errorhandler(404)
def index(error = ""):
	return send_from_directory(dashboard_app.static_folder, "index.html")

@dashboard_app.route("/auth", methods=["POST"])
def auth():
	return auth_module.handle_query(request.json)
	
@dashboard_app.route("/data-conduit", methods=["POST"])
@auth_module.jwt_required()
def data_conduit():
	return Response(json.dumps(data_api.handle_query(request.json)), mimetype = "application/json")

@dashboard_app.route("/stream/mjpeg")
@auth_module.jwt_required()
def stream_mjpeg():
	return stream_module.stream_mjpeg()

@dashboard_app.route("/stream/status")
@auth_module.jwt_required()
def stream_status():
    return stream_module.status()

if __name__ == "__main__":
	dashboard_app.run(host="0.0.0.0", port=443, ssl_context="adhoc", threaded=True)
