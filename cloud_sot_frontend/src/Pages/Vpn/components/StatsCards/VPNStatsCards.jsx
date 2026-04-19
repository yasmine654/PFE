import { useEffect, useState } from "react";
import { FaLock, FaShieldAlt, FaExclamationTriangle, FaNetworkWired } from "react-icons/fa";

import "./VPNStatsCards.css";

export default function VPNStatsCards() {
  const [vpns, setVpns] = useState([]);

  useEffect(() => {
    fetchVPNs();
  }, []);

  const fetchVPNs = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/vpn_gateways/");
      const data = await res.json();
      setVpns(data);
    } catch (error) {
      console.error(error);
    }
  };

  // 🔥 CALCULS

  const totalVPNs = vpns.length;

  // 🛡️ VPN IPSec
  const ipsecVPNs = vpns.filter(
    (v) => v.type === "ipsec"
  ).length;

  // ⚠️ VPN non protégés (pas d’IP publique)
  const unprotectedVPNs = vpns.filter(
    (v) => v.elastic_ip_id === null
  ).length;

  // 🌐 VPC connectés
  const connectedVPCs = new Set(
    vpns.map((v) => v.vpc_id)
  ).size;

  return (
    <div className="cards-container">

      {/* Total VPN */}
      <div className="card blue">
        <div className="card-top">
          <p>Total VPNs</p>
          <div className="card-icon">
            <FaLock />
          </div>
        </div>
        <h2>{totalVPNs}</h2>
      </div>

      {/* IPSec */}
      <div className="card green">
        <div className="card-top">
          <p>VPN IPSec</p>
          <div className="card-icon">
            <FaShieldAlt />
          </div>
        </div>
        <h2>{ipsecVPNs}</h2>
      </div>

      {/* Non protégés */}
      <div className="card orange">
        <div className="card-top">
          <p>VPN non protégés</p>
          <div className="card-icon">
            <FaExclamationTriangle />
          </div>
        </div>
        <h2>{unprotectedVPNs}</h2>
      </div>

      {/* VPC connectés */}
      <div className="card purple">
        <div className="card-top">
          <p>VPC connectés</p>
          <div className="card-icon">
            <FaNetworkWired />
          </div>
        </div>
        <h2>{connectedVPCs}</h2>
      </div>

    </div>
  );
}