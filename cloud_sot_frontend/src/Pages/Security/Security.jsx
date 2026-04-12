import { useEffect, useState, useContext } from "react";
import { FilterContext } from "../../Context/FilterContext";
import "./Security.css";

const endpoints = {
  "Security Group": "security_groups",
  "WAF": "wafs"
};

export default function Security() {
  const { tenant, provider, region } = useContext(FilterContext);

  const [activeTab, setActiveTab] = useState("Security Group");
  const [data, setData] = useState([]);

  useEffect(() => {
    let url = `http://127.0.0.1:8000/${endpoints[activeTab]}/`;

    const params = [];
    if (tenant) params.push(`tenant_id=${tenant}`);
    if (provider) params.push(`provider_id=${provider}`);
    if (region) params.push(`region_id=${region}`);

    if (params.length > 0) {
      url += "?" + params.join("&");
    }

    fetch(url)
      .then(res => res.json())
      .then(setData);

  }, [activeTab, tenant, provider, region]);

  return (
    <div className="security">

      <div className="header">
        <h1>Security</h1>
      </div>

      {/* Tabs */}
      <div className="tabs">
        {Object.keys(endpoints).map(tab => (
          <button
            key={tab}
            className={activeTab === tab ? "active" : ""}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="table-container">
        <table>

          <thead>
            <tr>
              {data[0] &&
                Object.keys(data[0]).map(key => (
                  <th key={key}>{key}</th>
                ))}
            </tr>
          </thead>

          <tbody>
            {data.map((item, i) => (
              <tr key={i}>
                {Object.entries(item).map(([key, val], j) => {

                  // 🎯 Badge spécial direction
                  if (key === "direction") {
                    return (
                      <td key={j}>
                        <span className={`badge ${val}`}>
                          {val}
                        </span>
                      </td>
                    );
                  }

                  return <td key={j}>{String(val)}</td>;
                })}
              </tr>
            ))}
          </tbody>

        </table>
      </div>

    </div>
  );
}