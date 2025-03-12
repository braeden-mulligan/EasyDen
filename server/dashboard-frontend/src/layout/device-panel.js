import { useEffect } from "react";
import { useGlobalStore } from "../store";
import { start_device_polling } from "../utils";
import { DEVICE_TYPE_MAP } from "../defines";
import { Poweroutlet, Thermostat } from "../components/devices";

export const DevicePanel = function({ device_types }) {
	if (typeof device_types === "string") device_types = [device_types];

	const devices = useGlobalStore((state) => state.devices)
	 .filter((device) => device_types.some((type) => DEVICE_TYPE_MAP[device.type] == type));

	useEffect(() => {
		return start_device_polling(device_types);
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