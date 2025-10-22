import { request } from "../api";
import { SERVER_ADDR } from "../defines";

export const DebugPage = function() {
	function debug_form_submit(e) {
		e.preventDefault();

		const form = e.target;
		const formData = new FormData(form);
		const formJson = Object.fromEntries(formData.entries());

		formJson.parameters = JSON.parse(formJson.parameters);

		request(formJson).then((response) => {
			console.log("Debug response:", response);
		})
	}

	function login(e) {
		e.preventDefault();

		const form = e.target;
		const formData = new FormData(form);
		const formJson = Object.fromEntries(formData.entries());

		// formJson.parameters = JSON.parse(formJson.parameters);

		console.log("Login form data:", formJson);
		const request_data = {
			action: "login",
			username: formJson.username,
			password: formJson.password

		}
		console.log("Requesting auth with:", request_data);

		request(request_data, null, "/auth")

		// request(formJson).then((response) => {
		// 	console.log("Debug response:", response);
		// })
	}

	function token_refresh(e) {
		e.preventDefault();
		console.log("Refreshing token");
		const request_data = {
			action: "refresh",
		}
		request(request_data, null, "/auth", true).then((response) => {
			console.log("Token refresh response:", response);
		})
	}

	return (
		<div>
			<form onSubmit={(e) => debug_form_submit(e)}>
				<label>Device Manager debug passthrough</label>
				<input type="checkbox" name="debug-passthrough" />
				<br />
				<input type="text" placeholder="entity" name="entity" />
				<input type="text" placeholder="directive" name="directive" />
				<textarea type="text" placeholder="parameters" name="parameters" />
				<button type="submit">Submit</button>
			</form>

			<form onSubmit={(e) => login(e)}>
				<input type="text" placeholder="username" name="username" />
				<input type="password" placeholder="password" name="password" />
				<button type="submit">Submit</button>
			</form>

			<form onSubmit={(e) => token_refresh(e)}>
				<button type="submit">Refresh Token</button>
			</form>
		</div>
	);
}