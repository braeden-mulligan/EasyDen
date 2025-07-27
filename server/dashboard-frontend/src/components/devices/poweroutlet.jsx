import { useEffect, useState } from "react";
import { InfoPane, Schedules } from './shared'
import { send_command } from "../../api";
import PowerIcon from "@mui/icons-material/Power";
import OutletIcon from '@mui/icons-material/Outlet';
import { ToggleSwitch } from "../toggle-switch/toggle-switch";

const SocketSelector = function({ device, on_select, initial_state, disabled }) {
	const [target_states, set_target_states] = useState(initial_state || device.attributes.socket_states.value.map((val) => null));

	const set_socket_state = function(value, index) {
		const new_state = target_states.slice();
		new_state[index] = value;
		set_target_states(new_state);
		on_select({
			"attribute-id": device.attributes.socket_states.id,
			"attribute-value": new_state
		});
	}

	return (
		<div className="flex-row" style={{ justifyContent: "space-evenly", gap: "16px", padding: "0 16px"}}>
			{target_states.map((val, i) => (
				<div key={i} className="flex-column" style={{ gap: "16px", paddingBottom: "16px"}}>
					<OutletIcon sx={{ color: val == null ? "grey" : val ?  "darkgreen" : "darkred"}}
						onClick={() => {
							if (!initial_state) {
								target_states[i] == null ? 
								set_socket_state(false, i) :
								set_socket_state(null, i)
							} else {
								set_socket_state(!val, i);
							}
						}}
					/>
					<ToggleSwitch  value={val} onChange={(value) => set_socket_state(value, i)} disabled={disabled}/>
				</div>
			))}
		</div>
	)
}

const SocketRenderer = function({ schedule }) {
	switch(schedule.command.attribute_name) {
		case "socket_states":
			return (
				<div style={{ display: "flex", gap: "8px" }}>
					{schedule.command.value.map((val, i) => (
						<OutletIcon sx={{ color: val == null ? "grey" : val ?  "darkgreen" : "darkred"}}/>
					))}
				</div>
			)
	}
}

export const Poweroutlet = function({ device, limited }) {
	return (<>
		<InfoPane device={device} Icon={PowerIcon} limited={limited} />
		<SocketSelector
			device={device} 
			on_select={(new_command) => {
				send_command(device, new_command);
			}}
			initial_state={device.attributes.socket_states.value}
			disabled={!device.online}
		/>
		{!limited && <Schedules device={device} AttributeRenderer={SocketRenderer} AttributeSelector={SocketSelector} />}
	</>)
}
