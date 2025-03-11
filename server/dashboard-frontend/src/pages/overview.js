import { default_error_handler, request } from "../api";

export const OverviewPage = function() {
	const handleClick = async function () {
		let x  = await request({hello: "world"}, (error) => {
			default_error_handler(error)
			console.log("Test custom error handler: " + JSON.stringify(error));
		})
	}

	return (
		<button onClick={handleClick}>Request</button>
	)
}