import { WeatherWidget } from "../components/services/weather-widget";
import { DevicePanel } from "../layout/device-panel";

export const OverviewPage = function() {
	return (<>
		<WeatherWidget />
		<DevicePanel entity_types={["thermostat", "poweroutlet"]} limited={true}/>
		<div>{"<market data>"}</div>
	</>)
}