import PageHeader from "../../PageHeader/PageHeader";
import SecurityStatsCards from "./components/StatsCards/SecurityStatsCards";

function Security() {
  return (
    <div className="security-page">

      <PageHeader 
        title="Security - Protection & Access" 
        breadcrumb="Dashboard > Security" 
      />

      <div className="security-content">
        <SecurityStatsCards />
      </div>

    </div>
  );
}

export default Security;