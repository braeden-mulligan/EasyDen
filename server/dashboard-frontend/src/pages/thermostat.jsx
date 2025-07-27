import { DevicePanel } from "../layout/device-panel";

export const ThermostatPage = function() {
	return (<>
		<DevicePanel entity_types={"thermostat"} />
		<div>{"<Temperature history chart>"}</div>
	</>)
}