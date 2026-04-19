import PageHeader from "../../PageHeader/PageHeader";
import NetworkStatsCards from "./components/StatsCards/NetworkStatsCards";

function Network() {
  return (
    <div className="network-page">

      {/* ✅ Header */}
      <PageHeader 
        title="Network - Ressources Réseau" 
        breadcrumb="Dashboard > Network" 
      />

      {/* ✅ Cards en dessous */}
      <div className="network-content">
        <NetworkStatsCards />
      </div>

    </div>
  );
}

export default Network;