import { ENTITY_TYPE_MAP, SERVER_ADDR } from "./defines"
import { add_notification, update_device_list } from "./store";
import { get_cookie } from "./utils";

export const default_error_handler = function (error) {
	//TODO: implement this.
	add_notification(error)
}

export const request = async function(data = {}, error_handler = null, endpoint = "/data-conduit") {
	const root_url = (location.protocol || "https:") + "//" + SERVER_ADDR;

	let response = await fetch(
		root_url + endpoint,
		{
			method: "POST",
			headers: {
				"Content-type": "application/json",
				"X-CSRF-TOKEN": get_cookie("csrf_access_token"),
			},
			body: JSON.stringify(data),
		}
	);

	if (response.status == 401) {
		//TODO:
		// block page
		// spin after a moment

		const refresh = await fetch(
			root_url + "/auth",
			{
				method: "POST",
				headers: {
					"Content-type": "application/json",
					"X-CSRF-TOKEN": get_cookie("csrf_refresh_token"),
				},
				body: JSON.stringify({ action: "refresh" }),
			}
		);

		if (refresh.status == 200) {
			response = await request(data, error_handler, endpoint);
		} else {
			// sign out user
			// window.location.reload();
		}
	}

	if (response.status != 200) {
		console.log("Unexpected response:", response.status, response.statusText);
		return null;
	}

	const response_content = await response.json();

	if (response_content.error) {
		error_handler ? error_handler(response.error) : default_error_handler(response.error);
	}

	return response_content;
}

export const fetch_devices = async function(type, params, suppress_error = false) {
	const response = await request({
		entity: type || "device",
		directive: "fetch",
		parameters: params || {}
	}, suppress_error ? () => {} : null);

	if (response?.result) {
		update_device_list(response.result);
	}

	return response
}

export const send_command = async function(device, command_data) {
	const response = await request({
		entity: ENTITY_TYPE_MAP[device.type] || "device",
		directive: "command",
		parameters: {
			"device-id": device.id,
			"command": command_data
		}
	});

	if (response?.result) {
		update_device_list(response.result);
	}

	return response
}

export const add_schedule = async function(device, schedule_data) {
	const response = await request({
		entity: "schedule",
		directive: "create",
		parameters: {
			"device-id": device.id,
			"device-type": device.type,
			"schedule": schedule_data
		}
	})

	if (response?.result){
		fetch_devices(ENTITY_TYPE_MAP[device.type], {
			"device-id": device.id
		})
	}
}

export const remove_schedule = async function(device, schedule_id){
	const response = await request({
		entity: "schedule",
		directive: "delete",
		parameters: {
			"schedule-id": schedule_id,
		}
	})

	if (response?.result) {
		fetch_devices(ENTITY_TYPE_MAP[device.type], {
			"device-id": device.id
		})
	}
};