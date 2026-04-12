import { useEffect, useState } from "react";
import "./FinOps.css";

export default function FinOps() {
  const [vms, setVms] = useState([]);
  const [volumes, setVolumes] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/vms/").then(res => res.json()).then(setVms);
    fetch("http://127.0.0.1:8000/volumes/").then(res => res.json()).then(setVolumes);
  }, []);

  return (
    <div className="finops">

      <h1>FinOps</h1>

      <div className="cards">

        <div className="card">
          <h3>VMs</h3>
          <p>{vms.length}</p>
        </div>

        <div className="card">
          <h3>Volumes</h3>
          <p>{volumes.length}</p>
        </div>

      </div>

    </div>
  );
}