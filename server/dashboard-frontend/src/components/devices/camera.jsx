import { useEffect, useRef, useState } from 'react';
import { InfoPane, Schedules } from './shared'
import { send_command } from "../../api";
import CameraIcon from "@mui/icons-material/Videocam";
import { ToggleSwitch } from "../toggle-switch/toggle-switch";

const CAMERA_STATUS = {
	0: "Inactive",
	1: "Motion detect idle",
	2: "Motion detect awaiting startup",
	4: "Motion detect recording",
	8: "Motion detect shutting down"
}

export const Camera = function({ device, limited }) {
	const [toggle_disabled, set_toggle_disabled] = useState(false);

	const toggle_motion_detection = function() {
		set_toggle_disabled(true)
		send_command(device, {
			"attribute-id": device.attributes.motion_detect_enabled.id,
			"attribute-value": !device.attributes.motion_detect_enabled.value
		}).then((response) => console.log(response)).finally(() => set_toggle_disabled(false))
	}

	const status = CAMERA_STATUS[device.attributes.status?.value] || "Status unknown";

	return (<>
		<InfoPane device={device} Icon={CameraIcon} limited={limited}/>
		<div className="flex-row" style={{ justifyContent: "space-between", padding: "16px"}}>
			<p>{status}</p>
			<ToggleSwitch  value={device.attributes.motion_detect_enabled.value} onChange={toggle_motion_detection} disabled={toggle_disabled}/>
		</div>
		{/* {!limited && <Schedules device={device} AttributeRenderer={} AttributeSelector={}/>} */}
	</>)
}


