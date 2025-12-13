import { SERVER_ADDR } from "../defines"
import { useEffect, useRef, useState } from 'react';
import { DevicePanel } from "../layout/device-panel";

const root_url = (location.protocol || "https:") + "//" + SERVER_ADDR;

export const CameraPage = function() {
	const [connected, set_connected] = useState(false);

	return (
		<div>
			{connected ? (
				<img
					src={`${root_url}/stream/mjpeg`}
					alt="Live camera feed"
				/>
			) : (
				<p>Waiting for camera stream...</p>
			)}
			<DevicePanel entity_types={"camera"} kwargs={{
				set_connected: set_connected
			}} />
		</div>
	)
}

// export const CameraPage = function() {
// 	// return <DevicePanel entity_types={"camera"} />

// 	// TODO: refresh token when expired
// 	const [connected, setConnected] = useState(false);
//   const [error, setError] = useState(null);
//   const [clientCount, setClientCount] = useState(0);
//   const imgRef = useRef(null);


//   // Check connection status
//   useEffect(() => {
//     const checkStatus = async () => {
//       try {
//         const response = await fetch(`${API_URL}/stream/status`);
//         const data = await response.json();

// 		console.log("data", data);	

//         setConnected(data.connected);
//         setClientCount(data.clients);
//         setError(null);
//       } catch (err) {
//         setError('Cannot connect to server');
//         setConnected(false);
//       }
//     };

//     checkStatus();
//     const interval = setInterval(checkStatus, 3000);
//     return () => clearInterval(interval);
//   }, []);

//   const handleSnapshot = async () => {
//     // try {
//     //   const response = await fetch(`${API_URL}/stream/snapshot.jpg`);
//     //   const blob = await response.blob();
//     //   const url = URL.createObjectURL(blob);
//     //   const a = document.createElement('a');
//     //   a.href = url;
//     //   a.download = `snapshot_${new Date().toISOString()}.jpg`;
//     //   a.click();
//     //   URL.revokeObjectURL(url);
//     // } catch (err) {
//     //   console.error('Snapshot error:', err);
//     // }
//   };

//   return (
//     <div className="min-h-screen bg-gray-900 text-white p-6">
//       <div className="max-w-6xl mx-auto">
//         {/* Header */}
//         <div className="flex items-center justify-between mb-6">
//           <div className="flex items-center gap-3">
//             {/* <CamIcon className="w-8 h-8 text-blue-400" /> */}
//             <div>
//               <h1 className="text-3xl font-bold">Security Camera</h1>
//               <p className="text-sm text-gray-400">MJPEG Stream</p>
//             </div>
//           </div>
          
//           <div className="flex items-center gap-4">
//             <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg">
//               {/* <Circle 
//                 className={`w-3 h-3 ${connected ? 'text-green-500 fill-green-500' : 'text-red-500 fill-red-500'}`}
//               /> */}
//               <span className="text-sm">
//                 {connected ? 'Connected' : 'Disconnected'}
//               </span>
//             </div>
            
//             <div className="px-4 py-2 bg-gray-800 rounded-lg text-sm">
//               {clientCount} viewer{clientCount !== 1 ? 's' : ''}
//             </div>

//             <button
//               onClick={handleSnapshot}
//               disabled={!connected}
//               className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition-colors"
//             >
//               {/* <Download className="w-4 h-4" /> */}
//               Snapshot
//             </button>
//           </div>
//         </div>

//         {/* Error Message */}
//         {error && (
//           <div className="mb-6 p-4 bg-red-900/50 border border-red-500 rounded-lg flex items-center gap-3">
//             {/* <AlertCircle className="w-5 h-5 text-red-400" /> */}
//             <span>{error}</span>
//           </div>
//         )}

//         {/* MJPEG Stream */}
//         <div className="relative bg-black rounded-lg overflow-hidden shadow-2xl">
//           {connected ? (
//             <img
//               ref={imgRef}
//               src={`${API_URL}/stream/mjpeg`}
//               alt="Live camera feed"
//               className="w-full aspect-video object-contain"
//             />
//           ) : (
//             <div className="w-full aspect-video flex items-center justify-center bg-gray-800">
//               <div className="text-center">
//                 {/* <Camera className="w-16 h-16 text-gray-600 mx-auto mb-4" /> */}
//                 <p className="text-xl text-gray-400">Waiting for camera connection...</p>
//               </div>
//             </div>
//           )}
//         </div>

//         {/* Info Panel */}
//         <div className="mt-6 p-4 bg-gray-800 rounded-lg">
//           <h2 className="text-lg font-semibold mb-3">Stream Information</h2>
//           <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
//             <div>
//               <p className="text-gray-400">Status</p>
//               <p className="font-medium">{connected ? 'Live' : 'Offline'}</p>
//             </div>
//             <div>
//               <p className="text-gray-400">Format</p>
//               <p className="font-medium">MJPEG</p>
//             </div>
//             <div>
//               <p className="text-gray-400">Latency</p>
//               <p className="font-medium">~1-2 seconds</p>
//             </div>
//             <div>
//               <p className="text-gray-400">Active Viewers</p>
//               <p className="font-medium">{clientCount}</p>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );

// }
