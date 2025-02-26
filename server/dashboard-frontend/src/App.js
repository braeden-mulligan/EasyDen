import { request } from "./api";

function App() {

const handleClick = async function () {
	let x  = await request({hello: "world"});
	console.log(x)
}


return (
	<>
		<h1>EasyDen Smart Home System</h1>
		<button onClick={handleClick}>Request</button>
	</>
);
}

export default App;
