import { useEffect } from "react";
import { useGlobalStore } from "../store";
import { ENTITY_TYPE_MAP, DEVICE_POLL_PERIOD_MS } from "../defines";
import { fetch_devices } from "../api";
import { Poweroutlet } from "../components/poweroutlet";
import { Thermostat } from "../components/thermostat";

export const DevicePanel = function({ entity_types, brief }) {
	if (typeof entity_types === "string") entity_types = [entity_types];

	const devices = useGlobalStore((state) => state.devices)
	 .filter((device) => entity_types.some((entity) => ENTITY_TYPE_MAP[device.type] == entity));

	useEffect(() => {
		for (const type of entity_types) {
			fetch_devices(type, undefined, true);
		}

		const poll_timer = setInterval(async () => {
			for (const type of entity_types) {
				fetch_devices(type, undefined, true);
			}
		}, DEVICE_POLL_PERIOD_MS);

		return () => clearInterval(poll_timer);
	}, [])

	const select_device_component = function(device) {
		switch (ENTITY_TYPE_MAP[device.type]) {
			case "thermostat":
				return <Thermostat device={device} brief={brief}/>
			case "poweroutlet":
				return <Poweroutlet device={device} brief={brief}/>
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