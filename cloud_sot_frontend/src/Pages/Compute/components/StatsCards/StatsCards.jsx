import { useEffect, useState } from "react";
import { getVMs } from "../../../../api/api";
import "./StatsCards.css";

// 🔥 icônes
import { FaServer, FaPlay, FaStop, FaMicrochip } from "react-icons/fa";

export default function StatsCards() {
  const [vms, setVMs] = useState([]);

  useEffect(() => {
    fetchVMs();
  }, []);

  const fetchVMs = async () => {
    try {
      const data = await getVMs();
      setVMs(data);
    } catch (error) {
      console.error(error);
    }
  };

  const totalVMs = vms.length;
  const runningVMs = vms.filter(vm => vm.state === "running").length;
  const stoppedVMs = vms.filter(vm => vm.state === "stopped").length;
  const totalCPU = vms.reduce((acc, vm) => acc + (vm.vcpu || 0), 0);
   console.log("VM DATA:", vms);
  return (
    <div className="cards-container">

      {/* Total */}
      <div className="card blue">
        <div className="card-top">
          <p>Total VMs</p>
          <div className="card-icon">
            <FaServer />
          </div>
        </div>
        <h2>{totalVMs}</h2>
      </div>

      {/* Running */}
      <div className="card green">
        <div className="card-top">
          <p>En cours</p>
          <div className="card-icon">
            <FaPlay />
          </div>
        </div>
        <h2>{runningVMs}</h2>
      </div>

      {/* Stopped */}
      <div className="card orange">
        <div className="card-top">
          <p>Arrêtées</p>
          <div className="card-icon">
            <FaStop />
          </div>
        </div>
        <h2>{stoppedVMs}</h2>
      </div>
        
      {/* CPU */}
      <div className="card purple">
        <div className="card-top">
          <p>Total vCPU</p>
          <div className="card-icon">
            <FaMicrochip />
          </div>
        </div>
        <h2>{totalCPU}</h2>
      </div>

    </div>
  );
}