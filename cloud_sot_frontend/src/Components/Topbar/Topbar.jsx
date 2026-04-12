import { useEffect, useState, useContext } from "react";
import { FilterContext } from "../../Context/FilterContext";
import "./Topbar.css";

export default function Topbar() {
  const { setTenant, setProvider, setRegion } = useContext(FilterContext);

  const [tenants, setTenants] = useState([]);
  const [providers, setProviders] = useState([]);
  const [regions, setRegions] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/tenants/")
      .then(res => res.json())
      .then(setTenants);

    fetch("http://127.0.0.1:8000/providers/")
      .then(res => res.json())
      .then(setProviders);

    fetch("http://127.0.0.1:8000/regions/")
      .then(res => res.json())
      .then(setRegions);
  }, []);

  return (
    <div className="topbar">

      <div className="left">
        <h2>Cloud Dashboard</h2>
      </div>

      <div className="filters">

        <select onChange={(e) => setTenant(e.target.value)}>
          <option value="">Tenant</option>
          {tenants.map(t => (
            <option key={t.tenant_id} value={t.tenant_id}>
              {t.name}
            </option>
          ))}
        </select>

        <select onChange={(e) => setProvider(e.target.value)}>
          <option value="">Provider</option>
          {providers.map(p => (
            <option key={p.provider_id} value={p.provider_id}>
              {p.name}
            </option>
          ))}
        </select>

        <select onChange={(e) => setRegion(e.target.value)}>
          <option value="">Region</option>
          {regions.map(r => (
            <option key={r.region_id} value={r.region_id}>
              {r.name}
            </option>
          ))}
        </select>

      </div>

    </div>
  );
}