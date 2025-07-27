import { useEffect, useState } from "react";
import { add_notification } from "../../store";
import { request } from "../../api";
import { theme } from "../../styles/theme";
import { isMobile, useMobileOrientation } from "react-device-detect";
import { CircularSpinner } from "../loading-spinner/circular-spinner";

const styles = {
	summaries_container: {
		...theme.light.card,
		justifyContent: "space-between",
		paddingRight: "8px",
		marginBottom: "1rem",
	},
	daily_summaries_css:
	`
		.daily-summaries > div {
			padding-right: 6px;
			border-right: 1px solid #ccc;
		}
		.daily-summaries > div:last-child {
			border-right: none; 
		}
	`
}

const fetch_weather = async () => {
	const request_data = {
		entity: "server",
		directive: "fetch",
		parameters: {
			"service": "weather"
		}
	};

	navigator.geolocation.getCurrentPosition(
		(position) => {
			request_data.parameters.latitude = position.coords.latitude;
			request_data.parameters.longitude = position.coords.longitude;
		},
		(err) => {
			add_notification("Warning: Could not get location for weather data, using default coordinates.");
		}
	);

	const response = await request(request_data);

	if (response.error) {
		add_notification(response)
	}

	return response;
};

const DailySummary = function({ weather_data }) {
	const { isPortrait, isLandscape } = useMobileOrientation();
	const mobile_portrait = isMobile && isPortrait;

	const icon_size = mobile_portrait ? "40px" : "48px";

	if (mobile_portrait) {
		weather_data.date = weather_data.date.split(",")[0];
		weather_data.temp = weather_data.temp.split(" ").join("");
	}

	return (
		<div className="flex-row" style={{ width: "100%" }}>
			<div className="flex-column">
				<img
					src={`https://openweathermap.org/img/wn/${weather_data.icon}@2x.png`}
					alt={weather_data.description}
					title={weather_data.description}
					style={{ width: icon_size, height: icon_size }}
				/>
			</div>
			<div className="flex-column" style={{ textAlign: "center" }}>
				<p style={{ margin: 0, overflow: "hidden", whiteSpace: "nowrap" }}>{weather_data.date}</p>
				<p style={{ margin: 0 }}>{weather_data.temp}</p>
			</div>
		</div>
	)
}

export const WeatherWidget = function() {
	const [current_weather, set_current_weather] = useState(null);
	const [forecast, set_forecast] = useState([]);
	const { isPortrait, isLandscape } = useMobileOrientation();
	const mobile_portrait = isMobile && isPortrait;

	useEffect(() => {
		fetch_weather().then((data) => {
			set_current_weather({
				temp: data.current.main.temp,
				icon: data.current.weather[0].icon,
				description: data.current.weather[0].description,
			});

			const daily_data = {};
			data.forecast.list.forEach((item) => {
				const date = new Date(item.dt * 1000).toLocaleDateString(undefined, {
					weekday: 'short',
					month: 'short',
					day: 'numeric',
				})

				if (!daily_data[date]) {
					daily_data[date] = [];
				}

				daily_data[date].push(item);
			});

			const current_date = new Date(data.current.dt * 1000).toLocaleDateString(undefined, {
				weekday: 'short',
				month: 'short',
				day: 'numeric',
			});

			delete daily_data[current_date];

			const daily_summaries = Object.entries(daily_data).map(([date, values]) => {
				const temps = values.map(v => v.main.temp);
				return {
					date,
					high: Math.max(...temps),
					low: Math.min(...temps),
					icon: values[2].weather[0].icon,
					description: values[2].weather[0].description,
				};
			}).slice(0, isMobile ? 3 : 5); 

			set_forecast(daily_summaries);

		}).catch((err) => {
			console.error("Error fetching weather data:", err);
			add_notification("Could not load weather data.");
		});
	}, []);

	return (!current_weather || forecast.length == 0 ?
		(<div className="flex-column" style={{ ...styles.summaries_container, textAlign: "center" }}>
			<CircularSpinner size={"40px"} />
		</div>) :
		(<>
			<div className="flex-row daily-summaries"
				style={{
					...styles.summaries_container,
					...(mobile_portrait &&
						{ borderLeft: "none", borderRight: "none", borderRadius: "0px", marginLeft: "-1rem", marginRight: "-1rem" })
				}}>
				<DailySummary weather_data={{ ...current_weather, date: "Now", temp: `${Math.round(current_weather.temp)}°` }} />
				{forecast.map((day) => (
					<DailySummary weather_data={{ ...day, temp: `${Math.round(day.high)}° / ${Math.round(day.low)}°` }} />
				))}
			</div>
			<style>{styles.daily_summaries_css}</style>
		</>
		)
	);
  }
