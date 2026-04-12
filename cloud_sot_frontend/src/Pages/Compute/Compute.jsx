import { useEffect, useState, useContext } from "react";
import { FilterContext } from "../../Context/FilterContext";
import "./Compute.css";

export default function Compute() {
  const { tenant, provider, region } = useContext(FilterContext);

  const [vms, setVms] = useState([]);
  const [selectedVM, setSelectedVM] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const [form, setForm] = useState({
    name: "",
    instance_type: "",
    vcpu: "",
    ram: "",
    os: "",
    image: "",
    private_ip: "",
    state: "running"
  });

  // GET ALL
  const fetchVMs = () => {
    let url = "http://127.0.0.1:8000/vms/";

    const params = [];
    if (tenant) params.push(`tenant_id=${tenant}`);
    if (provider) params.push(`provider_id=${provider}`);
    if (region) params.push(`region_id=${region}`);

    if (params.length > 0) {
      url += "?" + params.join("&");
    }

    fetch(url)
      .then(res => res.json())
      .then(setVms);
  };

  useEffect(() => {
    fetchVMs();
  }, [tenant, provider, region]);

  // VIEW
  const viewVM = (vm) => {
    setSelectedVM(vm);
    setShowModal(true);
  };

  // EDIT
  const editVM = (vm) => {
    setSelectedVM(vm);
    setForm(vm);
  };

  // CREATE
  const createVM = () => {
    fetch("http://127.0.0.1:8000/vms/", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(form)
    }).then(() => {
      fetchVMs();
      resetForm();
    });
  };

  // UPDATE
  const updateVM = () => {
    fetch(`http://127.0.0.1:8000/vms/${selectedVM.vm_id}`, {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(form)
    }).then(() => {
      fetchVMs();
      resetForm();
    });
  };

  // DELETE
  const deleteVM = (id) => {
    fetch(`http://127.0.0.1:8000/vms/${id}`, {
      method: "DELETE"
    }).then(fetchVMs);
  };

  // DELETE FORCE
  const deleteForceVM = (id) => {
    fetch(`http://127.0.0.1:8000/vms/${id}/force`, {
      method: "DELETE"
    }).then(fetchVMs);
  };

  // RESET
  const resetForm = () => {
    setSelectedVM(null);
    setForm({
      name: "",
      instance_type: "",
      vcpu: "",
      ram: "",
      os: "",
      image: "",
      private_ip: "",
      state: "running"
    });
  };

  return (
    <div className="compute">

      <h1>Compute</h1>

      {/* FORM */}
      <div className="form">

        <input placeholder="Name"
          value={form.name}
          onChange={e => setForm({...form, name: e.target.value})}
        />

        <input placeholder="Instance Type"
          value={form.instance_type}
          onChange={e => setForm({...form, instance_type: e.target.value})}
        />

        <input placeholder="vCPU"
          value={form.vcpu}
          onChange={e => setForm({...form, vcpu: e.target.value})}
        />

        <input placeholder="RAM"
          value={form.ram}
          onChange={e => setForm({...form, ram: e.target.value})}
        />

        <input placeholder="OS"
          value={form.os}
          onChange={e => setForm({...form, os: e.target.value})}
        />

        <input placeholder="Image"
          value={form.image}
          onChange={e => setForm({...form, image: e.target.value})}
        />

        <input placeholder="Private IP"
          value={form.private_ip}
          onChange={e => setForm({...form, private_ip: e.target.value})}
        />

        <select
          value={form.state}
          onChange={e => setForm({...form, state: e.target.value})}
        >
          <option value="running">running</option>
          <option value="stopped">stopped</option>
        </select>

        {selectedVM ? (
          <button className="update" onClick={updateVM}>Update</button>
        ) : (
          <button className="create" onClick={createVM}>Create</button>
        )}

        <button className="reset" onClick={resetForm}>Reset</button>

      </div>

      {/* TABLE */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>IP</th>
              <th>Type</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {vms.map(vm => (
              <tr key={vm.vm_id}>
                <td>{vm.name}</td>

                <td>
                  <span className={`status ${vm.state}`}>
                    {vm.state}
                  </span>
                </td>

                <td>{vm.private_ip}</td>
                <td>{vm.instance_type}</td>

                <td className="actions">
                  <button onClick={() => viewVM(vm)}>👁</button>
                  <button onClick={() => editVM(vm)}>Edit</button>
                  <button className="delete" onClick={() => deleteVM(vm.vm_id)}>Delete</button>
                  <button className="force" onClick={() => deleteForceVM(vm.vm_id)}>Force</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* MODAL */}
      {showModal && selectedVM && (
        <div className="modal-overlay">
          <div className="modal">

            <div className="modal-header">
              <h2>Détails VM</h2>
              <button onClick={() => setShowModal(false)}>X</button>
            </div>

            <div className="modal-body">
              <p><b>Name:</b> {selectedVM.name}</p>
              <p><b>ID:</b> {selectedVM.vm_id}</p>
              <p><b>Type:</b> {selectedVM.instance_type}</p>
              <p><b>vCPU:</b> {selectedVM.vcpu}</p>
              <p><b>RAM:</b> {selectedVM.ram}</p>
              <p><b>OS:</b> {selectedVM.os}</p>
              <p><b>Image:</b> {selectedVM.image}</p>
              <p><b>Private IP:</b> {selectedVM.private_ip}</p>
              <p><b>State:</b> {selectedVM.state}</p>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}