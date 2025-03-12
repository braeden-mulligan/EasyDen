import { request } from "../api";

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
		</div>
	);
}