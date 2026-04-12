import { useEffect, useState, useContext } from "react";
import { FilterContext } from "../../Context/FilterContext";
import "./Storage.css";

export default function Storage() {
  const { tenant, provider, region } = useContext(FilterContext);
  const [data, setData] = useState([]);

  useEffect(() => {
    let url = "http://127.0.0.1:8000/volumes/";

    const params = [];
    if (tenant) params.push(`tenant_id=${tenant}`);
    if (provider) params.push(`provider_id=${provider}`);
    if (region) params.push(`region_id=${region}`);

    if (params.length > 0) {
      url += "?" + params.join("&");
    }

    fetch(url).then(res => res.json()).then(setData);
  }, [tenant, provider, region]);

  return (
    <div className="storage">
      <h1>Storage</h1>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              {data[0] && Object.keys(data[0]).map(k => <th key={k}>{k}</th>)}
            </tr>
          </thead>
          <tbody>
            {data.map((item, i) => (
              <tr key={i}>
                {Object.values(item).map((val, j) => (
                  <td key={j}>{String(val)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}