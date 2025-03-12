import { useEffect } from "react";
import { useGlobalStore } from "../store";
import { start_device_polling } from "../utils";

export const OverviewPage = function() {
	const devices = useGlobalStore((state) => state.devices)

	useEffect(() => {
		return start_device_polling(["thermostat", "poweroutlet"]);
	}, [])

	return (
		<ul>
			{devices.map((device) => <li key={device.id}>{JSON.stringify(device)}</li>)}
		</ul>
	)
}