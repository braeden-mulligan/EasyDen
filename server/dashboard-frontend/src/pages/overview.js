import { DevicePanel } from "../layout/device-panel";

export const OverviewPage = function() {
	return <DevicePanel device_types={["thermostat", "poweroutlet"]}/>
}