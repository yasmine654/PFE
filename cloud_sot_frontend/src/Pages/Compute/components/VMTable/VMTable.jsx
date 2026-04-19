import { useState } from "react";
import VMModal from "./VMModal";
import "./VMTable.css";

export default function VMTable({ vms = [], providers = [], regions = [], eips = [] }) {

  const [selectedVM, setSelectedVM] = useState(null);

  const getProvider = id => providers.find(p => p.provider_id === id)?.name || "-";
  const getRegion = id => regions.find(r => r.region_id === id)?.name || "-";

  const getPublicIP = id => {
    if (!id) return "-";
    const match = eips.find(e => e.elastic_ip_id === id);
    return match ? match.ip : "-";
  };

  return (
    <div className="table-container">

      <table>
        <thead>
          <tr>
            <th>NOM</th>
            <th>ÉTAT</th>
            <th>PROVIDER</th>
            <th>RÉGION</th>
            <th>TYPE</th>
            <th>RESSOURCES</th>
            <th>IP PRIVÉE</th>
            <th>IP PUBLIQUE</th>
            <th>ACTIONS</th>
          </tr>
        </thead>

        <tbody>
          {vms.map(vm => (
            <tr key={vm.vm_id}>

              <td>
                <strong className="vm-name">{vm.name}</strong><br />
                <span className="vm-id">vm-{vm.vm_id}</span>
              </td>

              <td>
                <span className={`status ${vm.state}`}>
                  {vm.state === "running" ? "En cours" : "Arrêtée"}
                </span>
              </td>

              <td>{getProvider(vm.provider_id)}</td>
              <td>{getRegion(vm.region_id)}</td>
              <td>{vm.instance_type}</td>

              <td>
                <div className="resources">
                  <span className="vcpu">{vm.vcpu} vCPU</span>
                  <span className="ram">{vm.ram} GB RAM</span>
                </div>
              </td>

              <td>{vm.private_ip}</td>
              <td>{getPublicIP(vm.elastic_ip_id)}</td>

              <td className="actions">
                <img
                  src="/img_crud/eye_.png"
                  className="action-icon"
                  onClick={() => setSelectedVM({ ...vm, mode: "view" })}
                />
                <img
                  src="/img_crud/edit_.png"
                  className="action-icon"
                  onClick={() => setSelectedVM({ ...vm, mode: "edit" })}
                />
              </td>

            </tr>
          ))}
        </tbody>
      </table>

      {selectedVM && (
        <VMModal
          vm={selectedVM}
          mode={selectedVM.mode}
          onClose={() => setSelectedVM(null)}
        />
      )}

    </div>
  );
}