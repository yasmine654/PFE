import { useEffect, useState } from "react";
import "./Dashboard.css";

export default function Dashboard() {
  const [vms, setVms] = useState([]);
  const [vpcs, setVpcs] = useState([]);
  const [subnets, setSubnets] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/vms/").then(res => res.json()).then(setVms);
    fetch("http://127.0.0.1:8000/vpcs/").then(res => res.json()).then(setVpcs);
    fetch("http://127.0.0.1:8000/subnets/").then(res => res.json()).then(setSubnets);
  }, []);

  return (
    <div className="dashboard">

      <h1>Dashboard</h1>

      <div className="cards">

        <div className="card">
          <span className="icon">💻</span>
          <h3>VMs</h3>
          <p>{vms.length}</p>
        </div>

        <div className="card">
          <span className="icon">🌐</span>
          <h3>VPCs</h3>
          <p>{vpcs.length}</p>
        </div>

        <div className="card">
          <span className="icon">📡</span>
          <h3>Subnets</h3>
          <p>{subnets.length}</p>
        </div>

      </div>

    </div>
  );
}