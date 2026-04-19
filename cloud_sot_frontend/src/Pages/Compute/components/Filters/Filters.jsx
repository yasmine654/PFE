import "./Filters.css";
import { FaSearch } from "react-icons/fa";

export default function Filters({
  search,
  setSearch,
  provider,
  setProvider,
  region,
  setRegion,
  tenant,
  setTenant,
  state,
  setState,
  providers,
  regions,
  tenants
}) {
  return (
    <div className="filters-container">

      {/* 🔍 SEARCH */}
      <div className="search-box">
        <FaSearch className="search-icon" />
        <input
          type="text"
          placeholder="Rechercher une VM..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* FILTERS */}
      <div className="filters-group">

        <select value={provider} onChange={(e) => setProvider(e.target.value)}>
          <option value="">Provider</option>
          {providers.map(p => (
            <option key={p.provider_id} value={p.provider_id}>
              {p.name}
            </option>
          ))}
        </select>

        <select value={region} onChange={(e) => setRegion(e.target.value)}>
          <option value="">Région</option>
          {regions.map(r => (
            <option key={r.region_id} value={r.region_id}>
              {r.name}
            </option>
          ))}
        </select>

        <select value={tenant} onChange={(e) => setTenant(e.target.value)}>
          <option value="">Tenant</option>
          {tenants.map(t => (
            <option key={t.tenant_id} value={t.tenant_id}>
              {t.name}
            </option>
          ))}
        </select>

        <select value={state} onChange={(e) => setState(e.target.value)}>
          <option value="">État</option>
          <option value="running">Running</option>
          <option value="stopped">Stopped</option>
        </select>

        {/* RESET */}
        <button
          className="reset-btn"
          onClick={() => {
            setSearch("");
            setProvider("");
            setRegion("");
            setTenant("");
            setState("");
          }}
        >
          Reset
        </button>

      </div>
    </div>
  );
}