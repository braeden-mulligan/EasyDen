import { useState } from "react";
import DeviceUnknownIcon from "@mui/icons-material/DeviceUnknown";
import SettingsIcon from '@mui/icons-material/Settings';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import { ToggleSwitch } from "../toggle-switch/toggle-switch";
import { add_schedule, remove_schedule, send_command } from "../../api";
import { capitalize } from "../../utils";
import { theme } from "../../styles/theme";
import { Popover } from '../popover/popover';
import { COMMON_COMMANDS } from "../../defines";

const styles = {
	schedules_list: {
		margin: "0px 8px 4px",
		maxHeight: "268px",
		overflow: "auto",
		border: theme.border_thin,
	},
	shedules_list_css: `
		.schedules-list >:nth-child(even) {
			background-color: #dbdbdb;
		
		}
	`
}

export const InfoPane = function({ device, Icon, Settings, status, limited }) {
	const [current_status, set_current_status] = useState(device.attributes.enabled.value);
	const [settings_popover_open, set_settings_popover_open] = useState(false);

	const toggle_status = async function(value) {
		const response = await send_command(device, {
			"attribute-id": device.attributes.enabled.id,
			"attribute-value": +value
		});

		if (response?.result) {
			set_current_status(response.result[0].attributes.enabled.value);
		}
	}

	const SharedSettings = function() {
		return (
			<>
				<p>{`Device ID: ${device.id}`}</p>
				<button onClick={() => send_command(device, COMMON_COMMANDS.Blink)}>
					Click to Identify
				</button>
			</>
		);
	}

	return (<>
		<div className="flex-row" style={{
			height: "48px",
			justifyContent: "space-between",
			padding: "4px 8px"
		}}>
			{<Icon fontSize="large"/> || <DeviceUnknownIcon fontSize="large" />}
			<p>{device.name}</p>
			<Popover is_open={settings_popover_open} set_is_open={set_settings_popover_open}
				reference_element={
					<SettingsIcon fontSize="large"
						style={{
							marginRight: "4px",
							marginTop: "8px",
						}}
					 />
				}
				style={{ 
					...theme.light.card,
					padding: "8px 16px",
					margin: "4px",
				}}
			>
				<div>
					<SharedSettings />
					{Settings && <Settings /> }
				</div>
			</Popover>
		</div>
		<hr/>
		<div className="flex-row" style={{
			height: "40px",
			width: "100%",
			justifyContent: "space-between"
		}}>
			<div style={{ flex: 1 }}/>
			<div className="flex-row">
				{device.online ? 
					<p style={{ color: "green"}}>Online</p> :
					<p style={{ color: "red" }}>Offline</p> 
				}
				<p>&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;</p>
				<p>{status ? status : device.attributes.enabled.value ? "Enabled" : "Disabled" }</p>
			</div>
			<div className="flex-row" style={{
				flex: 1,
				justifyContent: "flex-end",
			}}>
				<ToggleSwitch style={{ paddingRight: "12px" }} value={current_status} onChange={toggle_status} disabled={limited}/>
			</div>
		</div>
		<hr/>
	</>);
}

/**
 * Schedules
 * 
 * Example arguments:
 * 
 * AttributeRenderer: function(schedule) {
 *		switch (schedule.command.attribute_name) {
 *			case "target_temperature": 
 *				return (<Element>{schedule.command.value}</Element>)
 *			case "other_operating_param":
 *				...
 * }
 * 
 * AttributeSelector: function(device, on_select) {
 * 		return (<Element 
 * 			onChange={(e) => {
 *		 		on_select({
 *					"attribute-id": device.attributes.<attribute-name>.id,
 *					"attribute-value": e.target.value
 *		 		});
 *			}
 * 		/>)
 *	}
 */
export const Schedules = function({ device, AttributeRenderer, AttributeSelector }) {
	const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
	const blank_schedule = {
		command: {},
		time: {},
		recurring: true,
		pause: 0
	};
	const schedules = [];
	const [selected_days, set_selected_days] = useState(days.map(() => false));
	const [new_schedule, set_new_schedule] = useState(blank_schedule);
	const [popover_open, set_popover_open] = useState(false);

	function handle_day_change(day_index, value) {
		function days_to_string(selected_days) {
			return days.filter((_, i) => selected_days[i]).map(day => day.toLowerCase()).join(",");
		}

		const new_days = selected_days.slice(); 
		new_days[day_index] = value;

		const new_schedule_time = {...new_schedule.time};
		new_schedule_time.days = days_to_string(new_days);
		set_new_schedule((prev) => ({...prev, time: new_schedule_time}));
 		set_selected_days(new_days);
	}

	for (const schedule of device.schedules) {
		const days = schedule.time.days.split(",");

		schedules.push(
			<div className="flex-row"
				key={schedule.id}
				style={{
					padding: "6px 8px",
				}}
			>
				<div>
					<AttributeRenderer schedule={schedule}/>
					<p style={{ margin: "2px"}}>
						{`@ ${schedule.time.hour}:${schedule.time.minute} `}
						{`${schedule.recurring ?
							"every: " + days.map((day) => capitalize(day)).join(", ") :
							"once this " + capitalize(days[0])}`}
					</p>
				</div>
				<div className="flex-row" style={{
					flex: 1,
					justifyContent: "flex-end",
				}}>
					<RemoveIcon
						sx={{color:"#771c13", border: "1px solid #771c13", borderRadius: "4px", backgroundColor: theme.light.card.backgroundColor }}
						onClick={() => remove_schedule(device, schedule.id)}
					/>
					</div>
			</div>
		)
	}

	return (
		<div>
			<hr/>
			<div className="flex-row" style={{
				height: "40px",
				justifyContent: "space-between"
			}}>
				<div style={{ flex: 1 }}/>
				<h4 style={{
					display:"flex",
					justifyContent:"center",
				}}>Schedules</h4>
				<div className="flex-row" style={{
					flex: 1,
					justifyContent: "flex-end",
				}}>
					<Popover is_open={popover_open} set_is_open={set_popover_open}
						reference_element={
							<AddIcon 
								sx={{ border: "1px solid black", borderRadius: "4px", marginRight: "16px" }}
							/>
						}
						style={{ 
							...theme.light.card,
							padding: "8px 16px",
						}}
					>
						<AttributeSelector
							device={device}
							on_select ={(new_command) => {
								set_new_schedule((prev) => ({...prev, command: new_command }))
							}
						}/>
							<input type={"time"} 
								value={new_schedule.time.hour && new_schedule.time.minute ?
									`${new_schedule.time.hour}:${new_schedule.time.minute}` :
									""
								}
								onChange={(e) => {
									const new_schedule_time = {...new_schedule.time};
									const [hour, minute] = e.target.value.split(":");
									new_schedule_time.hour = hour;
									new_schedule_time.minute = minute;
									set_new_schedule((prev)=> ({...prev, time: new_schedule_time}));
							}}/>
							{days.map((day, i) => (
								<div key={day}>
									<input type={"checkbox"} id={day} 
										checked={selected_days[i]}
										onChange={(e) => handle_day_change(i, e.target.checked)}/>
									<label>{day}</label>
								</div>
							))}
							<div>
								<input type={"checkbox"} id={"Recurring"} onChange={(e) => set_new_schedule((prev) => ({...prev, recurring: !e.target.checked}))}/>
								<label>One-time</label>
							</div>
						<button
							onClick={() => {
								add_schedule(device, new_schedule);
								set_popover_open(false);
								set_new_schedule(blank_schedule);
								set_selected_days(days.map(() => false));
							}}
						>
							Add
						</button>
					</Popover>
				</div>
			</div>
			<div className="schedules-list" style={styles.schedules_list}>
				{schedules}
			</div>
			<style>{styles.shedules_list_css}</style>
		</div>
	)
}
