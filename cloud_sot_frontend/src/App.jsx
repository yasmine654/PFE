import Navbar from "./NavBar/Navbar";
import "./App.css";

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Dashboard from "./Pages/Dashboard/Dashboard";
import Compute from "./Pages/Compute/Compute";
import Network from "./Pages/Network/Network";
import Storage from "./Pages/Storage/Storage";
import Security from "./Pages/Security/Security";
import VPN from "./Pages/VPN/VPN";
import Anomalies from "./Pages/Anomalies/Anomalies";
import FinOps from "./Pages/FinOps/FinOps";

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Navbar />

        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/compute" element={<Compute />} />
            <Route path="/network" element={<Network />} />
            <Route path="/storage" element={<Storage />} />
            <Route path="/security" element={<Security />} />
            <Route path="/vpn" element={<VPN />} />
            <Route path="/anomalies" element={<Anomalies />} />
            <Route path="/finops" element={<FinOps />} />
          </Routes>
        </div>

      </div>
    </Router>
  );
}

export default App;