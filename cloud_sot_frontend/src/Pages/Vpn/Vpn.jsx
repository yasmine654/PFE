import PageHeader from "../../PageHeader/PageHeader";
import VPNStatsCards from "./components/StatsCards/VPNStatsCards";

function VPN() {
  return (
    <div className="vpn-page">

      <PageHeader 
        title="VPN - Connectivity & Security" 
        breadcrumb="Dashboard > VPN" 
      />

      <div className="vpn-content">
        <VPNStatsCards />
      </div>

    </div>
  );
}

export default VPN;