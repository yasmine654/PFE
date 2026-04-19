import PageHeader from "../../PageHeader/PageHeader";
import StorageStatsCards from "./components/StatsCards/StorageStatsCards";

function Storage() {
  return (
    <div className="storage-page">

      <PageHeader 
        title="Storage - Volumes" 
        breadcrumb="Dashboard > Storage" 
      />

      <div className="storage-content">
        <StorageStatsCards />
      </div>

    </div>
  );
}

export default Storage;