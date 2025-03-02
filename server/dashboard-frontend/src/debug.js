import { request } from "./api";

export const Debug_Page = function() {
	function debug_form_submit(e) {
		e.preventDefault();

		const form = e.target;
		const formData = new FormData(form);
		const formJson = Object.fromEntries(formData.entries());

		formJson.parameters = JSON.parse(formJson.parameters);
		formJson.entity = "debug";

		console.log("form data:", formJson);

		request(formJson).then((response) => {
			console.log("response:", response);
		})
	}

	return (
	<div>
		<h1>Debug Page</h1>
		<form onSubmit={(e) => debug_form_submit(e)}>
			<input type="text" placeholder="category" name="category" />
			<input type="text" placeholder="directive" name="directive" />
			<textarea type="text" placeholder="parameters" name="parameters" />
			<button type="submit">Submit</button>
		</form>
	</div>
	);
}