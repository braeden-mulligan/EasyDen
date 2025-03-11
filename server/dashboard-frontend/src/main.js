import { BrowserRouter, Routes, Route } from "react-router"
import { isMobile, useMobileOrientation } from "react-device-detect";

import { NavbarTop, NavbarSide } from "./navigation";
import { DebugPage } from "./pages/debug";
import { OverviewPage } from "./pages/overview";
import { ThermostatPage } from "./pages/thermostat";
import { PowerOutletPage } from "./pages/poweroutlet";

const NotFoundPage = function () {
	return <div>404 Not Found</div>;
}

function AppMain() {
	const { isPortrait } = useMobileOrientation();
	const narrow_view = isMobile && isPortrait;

	return (
		<BrowserRouter>
			<header>
				<NavbarTop manage_sidebar={narrow_view} />
			</header>
			<div>
				{!narrow_view && <NavbarSide />}
				<main>
					<Routes>
						<Route path="/" element={<OverviewPage />} />
						<Route path="thermostat" element={<ThermostatPage />} />
						<Route path="poweroutlet" element={<PowerOutletPage/>} />
						<Route path="debug" element={<DebugPage />} />
						<Route path="*" element={<NotFoundPage />} />
					</Routes>
				</main>
			</div>
		</BrowserRouter>
	);
}

export default AppMain;
