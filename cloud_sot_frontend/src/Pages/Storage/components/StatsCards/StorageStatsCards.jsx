import { useEffect, useState } from "react";
import { FaHdd, FaDatabase, FaUnlink, FaLock } from "react-icons/fa";

import "./StorageStatsCards.css";

export default function StorageStatsCards() {
  const [volumes, setVolumes] = useState([]);

  useEffect(() => {
    fetchVolumes();
  }, []);

  const fetchVolumes = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/volumes/");
      const data = await res.json();
      setVolumes(data);
    } catch (error) {
      console.error(error);
    }
  };

  // 🔥 CALCULS

  const totalVolumes = volumes.length;

  const totalStorageGB = volumes.reduce(
    (acc, v) => acc + (v.size || 0),
    0
  );

  const totalStorage =
    totalStorageGB >= 1000
      ? (totalStorageGB / 1000).toFixed(2) + " TB"
      : totalStorageGB + " GB";

  const orphanVolumes = volumes.filter(
    (v) => v.vm_id === null
  ).length;

  const encryptedCount = volumes.filter(
    (v) => v.encrypted === true
  ).length;

  const encryptionRate =
    totalVolumes > 0
      ? ((encryptedCount / totalVolumes) * 100).toFixed(1) + "%"
      : "0%";

  return (
    <div className="cards-container">

      {/* Total volumes */}
      <div className="card blue">
        <div className="card-top">
          <p>Total Volumes</p>
          <div className="card-icon">
            <FaHdd />
          </div>
        </div>
        <h2>{totalVolumes}</h2>
      </div>

      {/* Stockage total */}
      <div className="card green">
        <div className="card-top">
          <p>Stockage total</p>
          <div className="card-icon">
            <FaDatabase />
          </div>
        </div>
        <h2>{totalStorage}</h2>
      </div>

      {/* Orphelins */}
      <div className="card orange">
        <div className="card-top">
          <p>Volumes orphelins</p>
          <div className="card-icon">
            <FaUnlink />
          </div>
        </div>
        <h2>{orphanVolumes}</h2>
      </div>

      {/* Chiffrement */}
      <div className="card purple">
        <div className="card-top">
          <p>% Chiffrement</p>
          <div className="card-icon">
            <FaLock />
          </div>
        </div>
        <h2>{encryptionRate}</h2>
      </div>

    </div>
  );
}