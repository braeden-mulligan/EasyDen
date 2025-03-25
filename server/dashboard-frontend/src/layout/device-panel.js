import { useEffect } from "react";
import { useGlobalStore } from "../store";
import { ENTITY_TYPE_MAP, DEVICE_POLL_PERIOD_MS } from "../defines";
import { fetch_devices } from "../api";
import { Poweroutlet } from "../components/devices/poweroutlet";
import { Thermostat } from "../components/devices/thermostat";
import { theme } from "../styles/theme";

const styles = {
	device_card: {
		backgroundColor: theme.light.card_color,
		border: theme.border_thin,
		borderRadius: "8px"
	},
	device_card_css: `
		.device-card {
			width: 280px;
			max-width: 360px;
		}

		@media (orientation: portrait) and (max-width: 608px) {
			.device-card {
				width: 100%;
			}
		}
	`,
	panel_container: {
		// display: "grid",
		// gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
		display: "flex",
		flexDirection: "row",
		flexWrap: "wrap",
		gap: "1rem"
	},
}

const DeviceCard = function({ device, limited }) {
	const select_device_component = function() {
		switch (ENTITY_TYPE_MAP[device.type]) {
			case "thermostat":
				return <Thermostat device={device} limited={limited}/>
			case "poweroutlet":
				return <Poweroutlet device={device} limited={limited}/>
			default:
				return (<>
					<p>UNKNOWN DEVICE</p>
					<p>{JSON.stringify(device)}</p>
				</>)
		}
	}

	return (<>
		<div className="device-card" style={styles.device_card}>
			{select_device_component()}
		</div>
		<style>{styles.device_card_css}</style>
	</>)
}

export const DevicePanel = function({ entity_types, limited}) {
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

	return (
		<div style={styles.panel_container}>
			{devices.map((device) =><DeviceCard key={device.id} device={device} limited={limited}/>)}
		</div>
	)
}