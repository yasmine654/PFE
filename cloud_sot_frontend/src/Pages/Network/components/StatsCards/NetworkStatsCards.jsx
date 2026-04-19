import { useEffect, useState } from "react";
import {
  getVPCs,
  getSubnets,
  getPeerings,
  getEIPs
} from "../../../../api/api";

import "./NetworkStatsCards.css";
import { FaNetworkWired, FaProjectDiagram, FaExchangeAlt, FaGlobe } from "react-icons/fa";

export default function NetworkStatsCards() {
  const [vpcs, setVpcs] = useState([]);
  const [subnets, setSubnets] = useState([]);
  const [peerings, setPeerings] = useState([]);
  const [eips, setEips] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
  try {
        const vpcRes = await fetch("http://127.0.0.1:8000/vpcs/");
        const subnetRes = await fetch("http://127.0.0.1:8000/subnets/");
        const peeringRes = await fetch("http://127.0.0.1:8000/vpc_peerings/");
        const eipRes = await fetch("http://127.0.0.1:8000/elastic_ips/");

        console.log("STATUS VPC:", vpcRes.status);
        console.log("STATUS SUBNET:", subnetRes.status);
        console.log("STATUS PEERING:", peeringRes.status);
        console.log("STATUS EIP:", eipRes.status);

        const vpcData = await vpcRes.json();
        const subnetData = await subnetRes.json();
        const peeringData = await peeringRes.json();
        const eipData = await eipRes.json();

        console.log("VPC:", vpcData);
        console.log("Subnets:", subnetData);
        console.log("Peerings:", peeringData);
        console.log("EIPs:", eipData);

        setVpcs(vpcData);
        setSubnets(subnetData);
        setPeerings(peeringData);
        setEips(eipData);

  } catch (error) {
    console.error("FETCH ERROR:", error);
  }
};

  return (
    <div className="cards-container">

        {/* VPC */}
        <div className="card blue">
        <div className="card-top">
            <p>Total VPCs</p>
            <div className="card-icon">
            <FaNetworkWired />
            </div>
        </div>
        <h2>{vpcs.length}</h2>
        </div>

        {/* Subnets */}
        <div className="card green">
        <div className="card-top">
            <p>Total Subnets</p>
            <div className="card-icon">
            <FaProjectDiagram />
            </div>
        </div>
        <h2>{subnets.length}</h2>
        </div>

        {/* Peerings */}
        <div className="card orange">
        <div className="card-top">
            <p>Total Peerings</p>
            <div className="card-icon">
            <FaExchangeAlt />
            </div>
        </div>
        <h2>{peerings.length}</h2>
        </div>

        {/* EIPs */}
        <div className="card purple">
        <div className="card-top">
            <p>Total Elastic IPs</p>
            <div className="card-icon">
            <FaGlobe />
            </div>
        </div>
        <h2>{eips.length}</h2>
        </div>

    </div>
);
}