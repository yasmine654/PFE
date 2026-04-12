import { useEffect, useState } from "react";
import "./Anomalies.css";

export default function Anomalies() {
  const [vms, setVms] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/vms/")
      .then(res => res.json())
      .then(setVms);
  }, []);

  const anomalies = vms.filter(vm => vm.state !== "running");

  return (
    <div className="anomalies">
      <h1>Anomalies</h1>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>State</th>
              <th>Issue</th>
            </tr>
          </thead>

          <tbody>
            {anomalies.map(vm => (
              <tr key={vm.vm_id}>
                <td>{vm.name}</td>
                <td>{vm.state}</td>
                <td>
                  <span className="badge warning">Not Running</span>
                </td>
              </tr>
            ))}
          </tbody>

        </table>
      </div>
    </div>
  );
}