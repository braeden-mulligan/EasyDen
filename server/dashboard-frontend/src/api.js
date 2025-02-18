import { SERVER_ADDR } from "./defines"

export const request = async function(data = {}) {
	console.log("Requesting from" + SERVER_ADDR)

	return fetch(
		"http://" + SERVER_ADDR, 
		{
			method: "POST",
			headers: {
				"Content-type": "application/json",
			},
			body: JSON.stringify(data),
		}
	).then((response) => {
		return response.json();
	}).catch((error) => {
		console.log("Error: " + error);
	})
}