
import { useEffect, useState } from "react";
import { add_notification } from "../../store";
import { request } from "../../api";
import { theme } from "../../styles/theme";
import { isMobile, useMobileOrientation } from "react-device-detect";
import { CircularSpinner } from "../loading-spinner/circular-spinner";

// TODO: share styles with weather widget
// TODO: genericize to accept arbitrary tickers

const styles = {
	summaries_container: {
		...theme.light.card,
		justifyContent: "space-between",
		paddingRight: "8px",
		marginBottom: "1rem",
		maxHeight: "48px",
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

const fetch_market = async () => {
	const request_data = {
		entity: "server",
		directive: "fetch",
		parameters: {
			"service": "market"
		}
	};

	const response = await request(request_data);

	if (response.error) {
		add_notification(response)
	}

	return response;
};

const PriceSummary = function({ image_url, ticker, price }) {
	const { isPortrait, isLandscape } = useMobileOrientation();
	const mobile_portrait = isMobile && isPortrait;

	const icon_size = mobile_portrait ? "28px" : "32px";

	return (
		<div className="flex-row" style={{ width: "100%" }}>
			<div className="flex-column" style={{ padding: "0 8px", height: mobile_portrait ? "40px" : "48px", justifyContent: "center" }}>
				{ image_url ?
					<img
						src={image_url}
						alt={ticker}
						title={ticker}
						style={{ width: icon_size }}
					/>
					: <p>{ticker}</p>
				}
			</div>
			<div className="flex-column" style={{ textAlign: "center" }}>
				<p style={{ margin: 0, overflow: "hidden", whiteSpace: "nowrap" }}>{price}</p>
			</div>
		</div>
	)
}

export const MarketWidget = function() {
	const [current_data, set_current_data] = useState(null);
	const { isPortrait, isLandscape } = useMobileOrientation();
	const mobile_portrait = isMobile && isPortrait;

	useEffect(() => {
		fetch_market().then((data) => {
			set_current_data(data);
		}).catch((err) => {
			console.error("Error fetching market data:", err);
			add_notification("Could not load market data.");
		});
	}, []);

	console.log("Current market data:", current_data);

	return (!current_data ?
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
				<PriceSummary image_url={current_data["bitcoin-image-url"]} ticker={"BTC"} price={current_data["bitcoin-price"] == null ? "N/A" :
					new Intl.NumberFormat("en-US", { style: "currency", currency: "CAD" }).format(current_data["bitcoin-price"])
				} />
				<PriceSummary ticker={"S&P 500 - "} price={current_data["sp500-price"] == null ? "N/A" :
					new Intl.NumberFormat("en-US", { style: "currency", currency: "CAD" }).format(current_data["sp500-price"])
				} />
			</div>
			<style>{styles.daily_summaries_css}</style>
		</>
		)
	);
  }
