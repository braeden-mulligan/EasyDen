class Plant_Status extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		let attrs = this.props.attributes;

		return (
			<div>
				<b>Plant { attrs.id }</b>
				<p>Current moisture: { attrs.moisture.value?.toFixed(1) + " %" }  ({ attrs.sensor_raw?.value })</p>
				<p>Target moisture: { attrs.target_moisture.value?.toFixed(1) + " %" }  ({ attrs.sensor_raw?.value })</p>
				<p>Moisture low threshold: { attrs.moisture_low.value?.toFixed(1) + " %" }</p>
				<p>Watering delay after moisture low { attrs.moisture_low_delay.value + " s" }</p>
				<p>Raw sensor value limits (configured) - Max: { attrs.sensor_raw_max.value }, Min: { attrs.sensor_raw_min.value }</p>
				<p>Raw sensor value limits (recorded) - Max: { attrs.sensor_recorded_max.value }, Min: { attrs.sensor_recorded_min.value }</p>
			</div>
		);
	}
}

class Irrigation_Attributes extends React.Component {
	constructor(props) {
		super(props);
	}

	render_plant_status(obj) {
		return (
			<li key={ obj.id }>
				<Plant_Status attributes={ obj } />
			</li>
		)
	}

	render() {
		let attrs = this.props.attributes;

		let plant_statuses = [];
		for (let i = 0; i < attrs.sensor_count?.value; ++i) {
			// error check indicies
			plant_statuses.push({
				id: i,
				moisture: attrs.moisture[i],
				target_moisture: attrs.target_moisture[i],
				moisture_low: attrs.moisture_low[i],
				moisture_low_delay: attrs.moisture_low_delay[i],
				sensor_raw: attrs.sensor_raw[i],
				sensor_raw_max: attrs.sensor_raw_max[i],
				sensor_raw_min: attrs.sensor_raw_min[i],
				sensor_recorded_max: attrs.sensor_recorded_max[i],
				sensor_recorded_min: attrs.sensor_recorded_min[i]
			});
		}

		let rendered_plant_statuses = plant_statuses.map((obj) => {
			return this.render_plant_status(obj)
		})

		return (
			<div>
				<p>Device enabled: { attrs.enabled.value } &nbsp;
					<button className="set" onClick={
						() => this.props.update_attribute(attrs.enabled.register, + !attrs.enabled.value)
					} > Toggle </button>
				</p>
				<p>Plants enabled: { attrs.plant_enable.value }</p>
				<p>Time until pump shutoff if no moisture change: { attrs.moisture_change_hysteresis_time.value }</p>
				<p>Sensor value difference threshold to be considered changing moisture: { attrs.moisture_change_hysteresis_amount.value }</p>
				<Mutable_Attribute description="Calibration mode" attribute={ attrs.calibration_mode } update_attribute={ this.props.update_attribute } />

				<ul>
					{ rendered_plant_statuses }
				</ul>
			</div>
		)
	}
}

class Irrigation_Schedules extends React.Component {
	constructor(props) {
		super(props);
	}

	render_schedule(obj) {
		return (
			<li key={ JSON.stringify(obj.id_tag) }>
				{ JSON.stringify(obj) }
			<button className="set" onClick={
					() => this.props.set_schedule(JSON.stringify(Object.assign({ "action": "delete" }, obj.id_tag)))
				} > Remove </button>
			</li>
		)
	}

	render() {
		let schedules = this.props.schedules.map((obj, i) => {
			return this.render_schedule(obj, i)
		})

		if (!schedules.length) {
			schedules = <p>None</p>;
		}

		return null;
	}
}