from flask import Flask, request, Response, send_from_directory
from flask_cors import CORS
from pathlib import Path

import importlib

REACT_APP_PATH = str(Path(__file__).parent) + "/dashboard-frontend/build"

dashboard_app = Flask(__name__, static_folder=REACT_APP_PATH, static_url_path="/")
CORS(dashboard_app, origins=["http://localhost:*", "https://localhost:*"])

@dashboard_app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "GET":
		response = send_from_directory(dashboard_app.static_folder, "index.html")
		return response

	return Response(response = "{\"hello\": \"world\"}", mimetype = "application/json")


if __name__ == "__main__":
	dashboard_app.run(host="0.0.0.0", port=80)