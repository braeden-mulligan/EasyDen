import { DevicePanel } from "../layout/device-panel";

export const OverviewPage = function() {
	return (<>
		<DevicePanel entity_types={["thermostat", "poweroutlet"]} brief={true}/>
		<div>{"<market data>"}</div>
		<div>{"<weather forecast>"}</div>
	</>)
}