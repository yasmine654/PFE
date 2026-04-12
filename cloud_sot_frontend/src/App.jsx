import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./Layout/Layout";
import FilterProvider from "./Context/FilterProvider";

// Pages
import Dashboard from "./Pages/Dashboard/Dashboard";
import Compute from "./Pages/Compute/Compute";
import Network from "./Pages/Network/Network";
import Security from "./Pages/Security/Security";
import Anomalies from "./Pages/Anomalies/Anomalies";
import FinOps from "./Pages/FinOps/FinOps";
import Storage from "./Pages/Storage/Storage";   // ✅ AJOUT
import Vpn from "./Pages/Vpn/Vpn";               // ✅ AJOUT

function App() {
  return (
    <BrowserRouter>
      <FilterProvider>
        <Routes>
          <Route path="/" element={<Layout />}>

            <Route index element={<Dashboard />} />

            <Route path="compute" element={<Compute />} />
            <Route path="network" element={<Network />} />
            <Route path="storage" element={<Storage />} />
            <Route path="security" element={<Security />} />
            <Route path="vpn" element={<Vpn />} />
            <Route path="anomalies" element={<Anomalies />} />
            <Route path="finops" element={<FinOps />} />

          </Route>
        </Routes>
      </FilterProvider>
    </BrowserRouter>
  );
}

export default App;