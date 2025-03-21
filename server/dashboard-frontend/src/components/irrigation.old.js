// function Plant_Status({ attributes }){
// 	return (
// 		<div>
// 			<b>Plant { attributes.id }</b>
// 			<p>Current moisture: { attributes.moisture.value?.toFixed(1) + " %" }  ({ attributes.sensor_raw?.value })</p>
// 			<p>Target moisture: { attributes.target_moisture.value?.toFixed(1) + " %" }</p>
// 			<p>Moisture low threshold: { attributes.moisture_low.value?.toFixed(1) + " %" }</p>
// 			<p>Watering delay after moisture low { attributes.moisture_low_delay.value + " s" }</p>
// 			<p>Raw sensor value limits (configured) - Max: { attributes.sensor_raw_max.value }, Min: { attributes.sensor_raw_min.value }</p>
// 			<p>Raw sensor value limits (recorded) - Max: { attributes.sensor_recorded_max.value }, Min: { attributes.sensor_recorded_min.value }</p>
// 		</div>
// 	);
// }

// function Irrigation_Attributes({ attributes, update_attribute }) {
// 	function render_plant_status(obj) {
// 		return (
// 		<li key={ obj.id }>
// 			<Plant_Status attributes={ obj } />
// 		</li>
// 		)
// 	}

// 	let plant_statuses = [];
// 	for (let i = 0; i < attributes.sensor_count?.value; ++i) {
// 		// error check indicies
// 		plant_statuses.push({
// 			id: i,
// 			moisture: attributes.moisture[i],
// 			target_moisture: attributes.target_moisture[i],
// 			moisture_low: attributes.moisture_low[i],
// 			moisture_low_delay: attributes.moisture_low_delay[i],
// 			sensor_raw: attributes.sensor_raw[i],
// 			sensor_raw_max: attributes.sensor_raw_max[i],
// 			sensor_raw_min: attributes.sensor_raw_min[i],
// 			sensor_recorded_max: attributes.sensor_recorded_max[i],
// 			sensor_recorded_min: attributes.sensor_recorded_min[i]
// 		});
// 	}

// 	let rendered_plant_statuses = plant_statuses.map((obj) => {
// 		return render_plant_status(obj)
// 	})

// 	const [calibration_mode_target, set_calibration_mode_target] = useState( attributes.calibration_mode.value);
// 	const [calibration_plant_select, set_calibration_plant_select] = useState( attributes.calibration_plant_select.value);

// 	return (
// 		<div>
// 			<p>Device enabled: { attributes.enabled.value } &nbsp;
// 				<button className="set" onClick={ () => update_attribute(attributes.enabled.register, + !attributes.enabled.value) } > Toggle </button>
// 			</p>
// 			<p>Plants enabled: { attributes.plant_enable.value }</p>
// 			<p>Time until pump shutoff if no moisture change: { attributes.moisture_change_hysteresis_time.value }</p>
// 			<p>Sensor value difference threshold to be considered changing moisture: { attributes.moisture_change_hysteresis_amount.value }</p>
			
// 			<p><span>Calibration mode: { attributes.calibration_mode.value} &nbsp;
// 				<input type="number" min="0" max="4" onChange={ (e) => { set_calibration_mode_target(e.target.value); } } />
// 				&nbsp; Calibration plant_select: { attributes.calibration_plant_select.value } &nbsp;
// 				<input type="number" min="0" max="2" onChange={ (e) => { set_calibration_plant_select(e.target.value); } } />
// 				<button className="set" onClick={ () => update_attribute(attributes.calibration_mode.register, [calibration_mode_target, calibration_plant_select]) } > Set </button>
// 			</span></p>
			
// 			<ul>
// 				{ rendered_plant_statuses }
// 			</ul>
// 		</div>
// 	)
// }

// function Irrigation_Schedules({ attributes, schedules, submit_schedule }) {
// 	[schedule_data, set_schedule_data] = useState({
// 		time: "",
// 		days: "",
// 	});

// 	function render_schedule(obj) {
// 		return (
// 		<li key={ JSON.stringify(obj.id) }>
// 			{ JSON.stringify(obj) }
// 			<button className="set" onClick={ () => set_schedule(build_schedule(null, null, null, "delete", null, null, obj.id)) } > Remove </button>
// 		</li>
// 		)
// 	}

// 	let rendered_schedules = schedules.map((obj, i) => {
// 		return render_schedule(obj, i)
// 	})

// 	if (!rendered_schedules.length) {
// 		rendered_schedules = <p>None</p>;
// 	}

// 	return (
// 		<div>
// 			<b>Schedules</b>
// 			<ul>
// 				{ rendered_schedules }
// 			</ul>
// 		</div>
// 	)
// }