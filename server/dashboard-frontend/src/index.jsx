import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from "react-router"
import { isMobile, useMobileOrientation } from "react-device-detect";
import { useGlobalStore } from './store';
import { PageBlocker } from './components/loading-spinner/page-overlay-spinner';
import { get_cookie } from './utils';

import { NavbarTop, NavbarSide } from "./layout/navigation";
import { NotificationSnackbar } from "./layout/notification";
import { DebugPage } from "./pages/debug";
import { OverviewPage } from "./pages/overview";
import { ThermostatPage } from "./pages/thermostat";
import { PowerOutletPage } from "./pages/poweroutlet";
import { CameraPage } from './pages/camera';
import { NotFoundPage } from "./pages/not-found";
import { LoginPage } from './pages/login';

import "./styles/main-layout.css"
import "./styles/theme.css"
import "./styles/common.css"
import { theme } from './styles/theme';

function AppMain() {
	const { isPortrait, isLandscape } = useMobileOrientation();
	const mobile_portrait = isMobile && isPortrait;
	const mobile_landscape = isMobile && isLandscape;

	const jwt_expired = get_cookie("access_token_expiry") < Date.now() && get_cookie("refresh_token_expiry") < Date.now();
	// const loading = useGlobalStore((state) => state.global_loading);

	if (jwt_expired) {
		return (
			<BrowserRouter>
				<Routes>
					<Route path="/" element={<LoginPage/>} />
					<Route path="*" element={<Navigate to="/" replace />} /> 
				</Routes>
				<NotificationSnackbar />
			</BrowserRouter>
		);
	} 

	return (
		<BrowserRouter>
			{/* {loading && <PageBlocker spinner />} */}
			{!mobile_landscape && <NavbarTop manage_sidebar={mobile_portrait} />}
			<div className="layout-main">
				{!mobile_portrait && <NavbarSide />}
				<div className="content-main" style={{backgroundColor: theme.light.gutter_color}}>
					<Routes>
						<Route path="/" element={<OverviewPage />} />
						<Route path="thermostat" element={<ThermostatPage />} />
						<Route path="poweroutlet" element={<PowerOutletPage/>} />
						<Route path="camera" element={<CameraPage/>} />
						<Route path="debug" element={<DebugPage />} />
						<Route path="*" element={<NotFoundPage />} />
					</Routes>
				</div>
			</div>
			<NotificationSnackbar />
		</BrowserRouter>
	);
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<AppMain />);