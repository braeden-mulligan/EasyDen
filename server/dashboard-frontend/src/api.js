import { SERVER_ADDR } from "./defines"
import { add_notification } from "./store";

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
	})
}