import { MarketWidget } from "../components/services/market-widget";
import { WeatherWidget } from "../components/services/weather-widget";
import { DevicePanel } from "../layout/device-panel";

export const OverviewPage = function() {
	return (<>
		<WeatherWidget />
		<MarketWidget />
		<DevicePanel entity_types={["thermostat", "poweroutlet", "camera"]} limited={true}/>
	</>)
}