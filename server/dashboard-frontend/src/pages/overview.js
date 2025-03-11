import { request } from "../api";

export const OverviewPage = function() {
	const handleClick = async function () {
		let x  = await request({hello: "world"}, (error) => {
			console.log("Test error handler: " + JSON.stringify(error));
		})
		console.log(x)
	}

	return (
		<button onClick={handleClick}>Request</button>
	)
}