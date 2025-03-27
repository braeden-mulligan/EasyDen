import { useEffect, useRef, useState } from 'react';
import { InfoPane, Schedules } from './shared'
import { send_command } from "../../api";
import { Popover } from '../popover/popover';
import DeviceThermostatIcon from "@mui/icons-material/DeviceThermostat";
import TuneIcon from '@mui/icons-material/Tune';
import { theme } from '../../styles/theme';

const SetpointSelector = function({ device, on_select }) {
	const [target_temperature, set_target_temperature] = useState(device.attributes.target_temperature.value);

	useEffect(() => {
		on_select({
			"attribute-id": device.attributes.target_temperature.id,
			"attribute-value": device.attributes.target_temperature.value
		});
	}, []);

	return(
		<div>
			<p style={{ padding: "0", margin: "0" }}>Select set-point</p>
			<input type="range" min="10" max="30" step="0.25" 
				style={{ writingMode: "vertical-lr", direction: "rtl"}} 
				value={target_temperature}
				onChange={(e) => {
					set_target_temperature(e.target.value)
					on_select({
						"attribute-id": device.attributes.target_temperature.id,
						"attribute-value": e.target.value
					});
				}}
			/>
			<p>{ target_temperature }</p>
		</div>
	)
}

const SetpointRenderer = function({ schedule }) {
	switch(schedule.command.attribute_name) {
		case "target_temperature":
			return (
				<p style={{ padding: "0", margin: "0" }}>
					{`Change set-point to: ${schedule.command.value} °C`}
				</p>
			)
	}
}

export const Thermostat = function({ device, limited }) {
	const target_temperature_command = useRef();
	const [popover_open, set_popover_open] = useState(false);

	const status = (() => {
		switch(device.attributes.status?.value) {
			case 0:
				return "Disabled";
			case 1:
				return "Idle";
			case 2: 
				return "Heating 🔥";
			case 3:
				return "Forced idle";
		}

		return "Status unknown";
	})();

	useEffect(() => {
		if (!device.online) {
			set_popover_open(false);
		}
	}, [device.online]);

	return (<>
		<InfoPane device={device} Icon={DeviceThermostatIcon} status={status} limited={limited}/>
		<div className="flex-column" style={{ justifyContent: "center" }}>
			<h2>{device.attributes.temperature.value.toFixed(1) + " °C"}</h2>
			<div className="flex-row" style={{ width: "100%",  justifyContent: "space-between"}}>
				<div style={{ flex: 1, paddingLeft: "16px" }}/>
				<p>{`Set-point: ${device.attributes.target_temperature.value} °C`}</p>
				<div className="flex-row" style={{
					flex: 1,
					justifyContent: "flex-end",
					paddingRight: "16px"
				}}>
					<Popover is_open={popover_open} set_is_open={!device.online ? () => {} : set_popover_open} reference_element={
						<TuneIcon sx={{ border: "1px solid black", borderRadius: "4px", ...(!device.online && {backgroundColor: "lightgrey"})}}/>
					}
						style={{
							...theme.light.card,
							padding: "8px 16px",
						}}
					>
						<SetpointSelector
							device={device}
							on_select={(command) => target_temperature_command.current = command}
						/>
						<button onClick={() => {
								send_command(device, target_temperature_command.current);
								set_popover_open(false);
						}}> 
							Confirm
						</button>
					</Popover>
				</div>
			</div>
		</div>
		{/* <MutableAttribute description="Target Temperature" attribute={device.attributes.target_temperature} set_attribute={set_attribute}/> */}
		{/* <Mutable_Attribute description="Temperature correction" attribute={ attributes.temperature_correction } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Threshold high" attribute={ attributes.threshold_high } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Threshold low" attribute={ attributes.threshold_low } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Max heat time" attribute={ attributes.max_heat_time } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Min cooldown time" attribute={ attributes.min_cooldown_time } update_attribute={ update_attribute } />
		<p>{JSON.stringify(device)}</p> */}
		{!limited && <Schedules device={device} AttributeRenderer={SetpointRenderer} AttributeSelector={SetpointSelector}/>}
	</>)
}


