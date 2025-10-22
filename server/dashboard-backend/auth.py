import os, json
from flask import Response, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, set_access_cookies, set_refresh_cookies, get_jwt_identity, unset_jwt_cookies
from database.operations import fetch_user
from common.utils import load_json_file, error_response
from common.defines import E_INVALID_REQUEST

SECRETS_PATH = os.path.dirname(os.path.realpath(__file__)) + "/../../secrets.json"

bcrypt = None
jwt = None

def init_auth(app):
	global bcrypt
	global jwt

	bcrypt = Bcrypt(app)
	jwt = JWTManager(app)

	secrets_json = load_json_file(SECRETS_PATH).get("user_auth", {})

	if not secrets_json.get("secret_key") or not secrets_json.get("jwt_secret_key"):
		raise ValueError("secret_key and jwt_secret_key not found")
	
	app.config["SECRET_KEY"] = secrets_json.get("secret_key")
	app.config["JWT_SECRET_KEY"] = secrets_json.get("jwt_secret_key")
	app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
	app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 300
	app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 600
	# app.config["JWT_COOKIE_CSRF_PROTECT"] = True
	# app.config["JWT_COOKIE_SECURE"] = True
	# app.config["JWT_COOKIE_SAMESITE"] = "Lax"

def login(username, password):
	if not username or not password:
		return Response(json.dumps(error_response(E_INVALID_REQUEST, "Missing username or password.")), mimetype = "application/json")

	user = fetch_user(username)
	print("USER", user)

	if not user or not bcrypt.check_password_hash(user["password_hash"], password):
		return Response(json.dumps(error_response(E_INVALID_REQUEST, "Username and password mismatch.")), mimetype = "application/json")

	access_token = create_access_token(identity = user["username"])
	refresh_token = create_refresh_token(identity = user["username"])

	response = Response(json.dumps({
		"result": "success",
		"user": {
			"id": user["id"],
			"username": user["username"],
			"email": user["email"]
		},
		"tokens": {
			"access": access_token
		}
	}), mimetype = "application/json")

	set_access_cookies(response, access_token)
	set_refresh_cookies(response, refresh_token)
	
	return response
	
@jwt_required(refresh = True)
def token_refresh():
	pass
	current_user = get_jwt_identity()
	access_token = create_access_token(identity = current_user)

	response = Response(json.dumps({
		"result": "success",
		"tokens": {
			"access": access_token
		}
	}), mimetype = "application/json")

	set_access_cookies(response, access_token)

	return response

def handle_query(data):
	action = data.get("action")

	if action == "login":
		return login(data.get("username"), data.get("password"))

	if action == "refresh":
		return token_refresh()

	return Response(json.dumps(error_response(E_INVALID_REQUEST, "Unknown action.")), mimetype = "application/json")
	