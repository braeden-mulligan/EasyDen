import { SERVER_ADDR } from "./defines"

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
			const default_error_handler = function () {
				//TODO: implement this.
			}
			error_handler ? error_handler(response.error) : default_error_handler(response.error);
		}

		return response;

	}).catch((error) => {
		console.log("Unhandled error: " + error);
	})
}