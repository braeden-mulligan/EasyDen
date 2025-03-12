import { useEffect } from "react";
import { useGlobalStore } from "../store";
import { DEVICE_TYPE_MAP, DEVICE_POLL_PERIOD_MS } from "../defines";
import { fetch_devices } from "../api";
import { Poweroutlet, Thermostat } from "../components/devices";

export const DevicePanel = function({ device_types }) {
	if (typeof device_types === "string") device_types = [device_types];

	const devices = useGlobalStore((state) => state.devices)
	 .filter((device) => device_types.some((type) => DEVICE_TYPE_MAP[device.type] == type));

	useEffect(() => {
		for (const type of device_types) {
			fetch_devices(type, undefined, true);
		}

		const poll_timer = setInterval(async () => {
			for (const type of device_types) {
				fetch_devices(type, undefined, true);
			}
		}, DEVICE_POLL_PERIOD_MS);

		return () => clearInterval(poll_timer);
	}, [])

	const select_device_component = function(device) {
		switch (DEVICE_TYPE_MAP[device.type]) {
			case "thermostat":
				return <Thermostat device={device}/>
			case "poweroutlet":
				return <Poweroutlet device={device}/>
			default:
				return (<>
					<p>UNKNOWN DEVICE</p>
					<p>{JSON.stringify(device)}</p>
				</>)
		}
	}

	return (
		<ul>
			{devices.map((device) => <li key={device.id}>{select_device_component(device)}</li>)}
		</ul>
	)
}