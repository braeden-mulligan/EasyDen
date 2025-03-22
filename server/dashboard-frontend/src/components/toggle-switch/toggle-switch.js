import "./toggle-switch.css"

const styles ={
	slider_disabled_css: `
		input:checked + .toggle-slider-disabled {
			background-color: lightgrey;
		}

		.toggle-slider-disabled:before {
			background-color: grey;
		}
	`
}

export const ToggleSwitch = function({ value, onChange, style, disabled }) {
	return (
		<div style={style}>
			<label className="toggle-switch" style={{ ...(disabled && {color: "grey"}) }}>
				<input type="checkbox" checked={value} onChange={(e) => onChange(e.target.checked)} disabled={disabled}/>
				<span className={`toggle-slider ${disabled ? "toggle-slider-disabled" : ""}`} />
				{disabled && <style>{styles.slider_disabled_css}</style>}
			</label>
		</div>
	)
}