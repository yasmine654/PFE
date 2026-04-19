import { useState } from "react";
import "./VMTable.css";

export default function VMModal({ vm, mode, onClose, refreshData }) {

  const [form, setForm] = useState({ ...vm });

  const handleSubmit = async () => {
    await fetch(`http://127.0.0.1:8000/vms/${vm.vm_id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });
    if (refreshData) refreshData();
    onClose();
  };

  const isView = mode === "view";

  return (
    <div className="vm-overlay">
      <div className="vm-modal">

        <div className="vm-modal-header">
          <h2>{isView ? "Détails VM" : "Modifier VM"}</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="vm-modal-body">

          <div className="vm-field">
            <label>Nom</label>
            {isView
              ? <span>{vm.name}</span>
              : <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
            }
          </div>

          <div className="vm-field">
            <label>Instance Type</label>
            {isView
              ? <span>{vm.instance_type}</span>
              : <input value={form.instance_type} onChange={e => setForm({...form, instance_type: e.target.value})} />
            }
          </div>

          <div className="vm-field">
            <label>vCPU</label>
            {isView
              ? <span>{vm.vcpu}</span>
              : <input type="number" value={form.vcpu} onChange={e => setForm({...form, vcpu: Number(e.target.value)})} />
            }
          </div>

          <div className="vm-field">
            <label>RAM (GB)</label>
            {isView
              ? <span>{vm.ram}</span>
              : <input type="number" value={form.ram} onChange={e => setForm({...form, ram: Number(e.target.value)})} />
            }
          </div>

          <div className="vm-field">
            <label>OS</label>
            {isView
              ? <span>{vm.os}</span>
              : <input value={form.os} onChange={e => setForm({...form, os: e.target.value})} />
            }
          </div>

          <div className="vm-field">
            <label>Image</label>
            {isView
              ? <span>{vm.image}</span>
              : <input value={form.image} onChange={e => setForm({...form, image: e.target.value})} />
            }
          </div>

          <div className="vm-field">
            <label>IP Privée</label>
            {isView
              ? <span>{vm.private_ip || "-"}</span>
              : <input value={form.private_ip} onChange={e => setForm({...form, private_ip: e.target.value})} />
            }
          </div>

          <div className="vm-field">
            <label>IP Publique</label>
            {isView
              ? <span>{vm.elastic_ip_id || "-"}</span>
              : <input value={form.elastic_ip_id || ""} onChange={e => setForm({...form, elastic_ip_id: e.target.value || null})} />
            }
          </div>

          <div className="vm-field">
            <label>État</label>
            {isView
              ? <span className={`status-text ${vm.state}`}>{vm.state === "running" ? "En cours" : "Arrêtée"}</span>
              : <select value={form.state} onChange={e => setForm({...form, state: e.target.value})}>
                  <option value="running">En cours</option>
                  <option value="stopped">Arrêtée</option>
                </select>
            }
          </div>

          <div className="vm-field">
            <label>VM ID</label>
            <span>{vm.vm_id}</span>
          </div>

        </div>

        <div className="modal-actions">
          <button onClick={onClose}>Fermer</button>
          {!isView && (
            <button className="save-btn" onClick={handleSubmit}>Sauvegarder</button>
          )}
        </div>

      </div>
    </div>
  );
}