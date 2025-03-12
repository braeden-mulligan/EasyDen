export const Poweroutlet = function({ device }) {
	return (<>
		<p>POWEROUTLET</p>
		<p>{JSON.stringify(device)}</p>
	</>)
}

export const Thermostat = function({ device }) {
	return (<>
		<p>THERMOSTAT</p>
		<p>{JSON.stringify(device)}</p>
	</>)
}
