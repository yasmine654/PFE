import { useState, useEffect } from "react";
import "./VMCrudPanel.css";

export default function VMCrudPanel({
  refreshData,
  providers = [],
  regions = [],
  tenants = [],
  availability_zones = [],
  subnets = [],
  vpcs = [],
  editingVM,
  setEditingVM
}) {

  const [showModal, setShowModal] = useState(false);

  const initialForm = {
    name: "",
    tenant_id: "",
    provider_id: "",
    region_id: "",
    az_id: "",
    subnet_id: "",
    vpc_id: "",
    instance_type: "",
    vcpu: "",
    ram: "",
    os: "",
    image: "",
    private_ip: "",
    state: "running"
  };

  const [form, setForm] = useState(initialForm);

  useEffect(() => {
    if (editingVM) {
      setForm(editingVM);
      setShowModal(true);
    }
  }, [editingVM]);

  const handleAdd = () => {
    setEditingVM(null);
    setForm(initialForm);
    setShowModal(true);
  };

  const handleSubmit = async () => {
    const url = editingVM
      ? `http://127.0.0.1:8000/vms/${editingVM.vm_id}`
      : `http://127.0.0.1:8000/vms/`;

    const method = editingVM ? "PUT" : "POST";

    await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });

    setShowModal(false);
    setEditingVM(null);
    refreshData();
  };

  const filteredVPCs = vpcs.filter(v => v.region_id == form.region_id);
  const filteredSubnets = subnets.filter(s => s.vpc_id == form.vpc_id);
  const filteredAZ = availability_zones.filter(az => az.region_id == form.region_id);

  return (
    <div className="crud-container">

      <button className="add-btn" onClick={handleAdd}>
        + Ajouter VM
      </button>

      {showModal && (
        <div className="crud-overlay">
          <div className="crud-modal">

            <h2>{editingVM ? "Modifier VM" : "Ajouter VM"}</h2>

            <div className="form-grid">

              <input
                placeholder="Nom"
                value={form.name}
                onChange={e => setForm({...form, name: e.target.value})}
              />

              <select value={form.tenant_id} onChange={e => setForm({...form, tenant_id: Number(e.target.value)})}>
                <option value="">Tenant</option>
                {tenants.map(t => <option key={t.tenant_id} value={t.tenant_id}>{t.name}</option>)}
              </select>

              <select value={form.provider_id} onChange={e => setForm({...form, provider_id: Number(e.target.value)})}>
                <option value="">Provider</option>
                {providers.map(p => <option key={p.provider_id} value={p.provider_id}>{p.name}</option>)}
              </select>

              <select value={form.region_id} onChange={e => setForm({...form, region_id: Number(e.target.value), vpc_id: "", subnet_id: "", az_id: ""})}>
                <option value="">Region</option>
                {regions.map(r => <option key={r.region_id} value={r.region_id}>{r.name}</option>)}
              </select>

              <select value={form.az_id} onChange={e => setForm({...form, az_id: Number(e.target.value)})}>
                <option value="">AZ</option>
                {filteredAZ.map(az => <option key={az.az_id} value={az.az_id}>{az.name || az.az_id}</option>)}
              </select>

              <select value={form.vpc_id} onChange={e => setForm({...form, vpc_id: Number(e.target.value), subnet_id: ""})}>
                <option value="">VPC</option>
                {filteredVPCs.map(v => <option key={v.vpc_id} value={v.vpc_id}>{v.name || v.vpc_id}</option>)}
              </select>

              <select value={form.subnet_id} onChange={e => setForm({...form, subnet_id: Number(e.target.value)})}>
                <option value="">Subnet</option>
                {filteredSubnets.map(s => <option key={s.subnet_id} value={s.subnet_id}>{s.name || s.subnet_id}</option>)}
              </select>

              <input
                placeholder="Instance Type"
                value={form.instance_type}
                onChange={e => setForm({...form, instance_type: e.target.value})}
              />

              <input
                type="number"
                placeholder="vCPU"
                value={form.vcpu}
                onChange={e => setForm({...form, vcpu: Number(e.target.value)})}
              />

              <input
                type="number"
                placeholder="RAM (GB)"
                value={form.ram}
                onChange={e => setForm({...form, ram: Number(e.target.value)})}
              />

              <input
                placeholder="OS"
                value={form.os}
                onChange={e => setForm({...form, os: e.target.value})}
              />

              <input
                placeholder="Image"
                value={form.image}
                onChange={e => setForm({...form, image: e.target.value})}
              />

              <input
                placeholder="Private IP"
                value={form.private_ip}
                onChange={e => setForm({...form, private_ip: e.target.value})}
              />

            </div>

            <div className="modal-actions">
              <button onClick={() => { setShowModal(false); setEditingVM(null); }}>Annuler</button>
              <button className="save-btn" onClick={handleSubmit}>Sauvegarder</button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}