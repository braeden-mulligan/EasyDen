import { jwtDecode } from "jwt-decode";

export const equal = function(obj_1, obj_2) {
	function is_object(obj) {
  		return obj != null && typeof obj === 'object';
	}

	const keys_1 = Object.keys(obj_1);
	const keys_2 = Object.keys(obj_2);
	if (keys_1.length !== keys_2.length) return false;

	for (const key of keys_1) {
		const val_1 = obj_1[key];
		const val_2 = obj_2[key];
		const are_objects = is_object(val_1) && is_object(val_2);

		if (are_objects && !equal(val_1, val_2) || !are_objects && val_1 !== val_2) {
			return false;
		}
	}

	return true;
}

export function capitalize(input) {
    if (typeof input === "string") {
        return input.charAt(0).toUpperCase() + input.slice(1);
    } else if (Array.isArray(input)) {
        return input.map(word => word.charAt(0).toUpperCase() + word.slice(1));
    } 

	throw new TypeError("Input must be a string or an array of strings");
}

export const get_cookie = function(name) {
	const cookies = document.cookie.split("; ");
	const cookie = cookies.find(cookie => cookie.startsWith(name + "="))

	if (cookie) {
		return (cookie.split("=")[1]);
	}

	return null;
}

export const set_cookie = function(name, value, days = 365) {
	let expires = "";
	if (days) {
		const date = new Date();
		date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
		expires = "; expires=" + date.toUTCString();
	}
	document.cookie = name + "=" + value + expires + "; path=/";
}

export const store_jwt_expiry = function(access_token, refresh_token = null) {
	const access_expiry = jwtDecode(access_token).exp * 1000; 
	set_cookie("access_token_expiry", access_expiry.toString());

	if (refresh_token) {
		const refresh_expiry = jwtDecode(refresh_token).exp * 1000;
		set_cookie("refresh_token_expiry", refresh_expiry.toString());
	}
}

export const logout = function() {
	set_cookie("access_token_expiry", "0");
	set_cookie("refresh_token_expiry", "0");
	window.location.reload();
}
