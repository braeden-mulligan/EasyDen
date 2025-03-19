import { ENTITY_TYPE_MAP, SERVER_ADDR } from "./defines"
import { add_notification, update_device_list } from "./store";

export const default_error_handler = function (error) {
	//TODO: implement this.
	add_notification(error)
}

export const request = async function(data = {}, error_handler = null) {
	return fetch(
		"http://" + SERVER_ADDR, 
		{
			method: "POST",
			headers: {
				"Content-type": "application/json",
			},
			body: JSON.stringify(data),
		}

	).then(async (response) => {
		response = await response.json();

		if (response.error) {
			error_handler ? error_handler(response.error) : default_error_handler(response.error);
		}

		return response;

	}).catch((error) => {
		console.log("Unhandled error: " + error);
	});
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