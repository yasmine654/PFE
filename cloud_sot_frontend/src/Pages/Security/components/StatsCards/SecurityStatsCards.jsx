import { useEffect, useState } from "react";
import { FaShieldAlt, FaExclamationTriangle, FaNetworkWired, FaLock } from "react-icons/fa";

import "./SecurityStatsCards.css";

export default function SecurityStatsCards() {
  const [securityGroups, setSecurityGroups] = useState([]);
  const [wafs, setWafs] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const sgRes = await fetch("http://127.0.0.1:8000/security_groups/");
      const wafRes = await fetch("http://127.0.0.1:8000/wafs/");

      const sgData = await sgRes.json();
      const wafData = await wafRes.json();

      setSecurityGroups(sgData);
      setWafs(wafData);

    } catch (error) {
      console.error(error);
    }
  };

  // 🔥 CALCULS INTELLIGENTS

  const totalSG = securityGroups.length;

  // ⚠️ règles exposées (public)
  const exposedRules = securityGroups.filter(
    (sg) => sg.source === "0.0.0.0/0"
  ).length;

  // 🌐 ports sensibles
  const sensitivePorts = [22, 3389, 80, 443];

  const riskyPorts = securityGroups.filter(
    (sg) => sensitivePorts.includes(sg.port)
  ).length;

  // 🔒 WAF actifs
  const totalWAF = wafs.length;

  return (
    <div className="cards-container">

      {/* Total SG */}
      <div className="card blue">
        <div className="card-top">
          <p>Security Groups</p>
          <div className="card-icon">
            <FaShieldAlt />
          </div>
        </div>
        <h2>{totalSG}</h2>
      </div>

      {/* Exposed */}
      <div className="card green">
        <div className="card-top">
          <p>Règles exposées</p>
          <div className="card-icon">
            <FaExclamationTriangle />
          </div>
        </div>
        <h2>{exposedRules}</h2>
      </div>

      {/* Ports */}
      <div className="card orange">
        <div className="card-top">
          <p>Ports sensibles</p>
          <div className="card-icon">
            <FaNetworkWired />
          </div>
        </div>
        <h2>{riskyPorts}</h2>
      </div>

      {/* WAF */}
      <div className="card purple">
        <div className="card-top">
          <p>WAF actifs</p>
          <div className="card-icon">
            <FaLock />
          </div>
        </div>
        <h2>{totalWAF}</h2>
      </div>

    </div>
  );
}