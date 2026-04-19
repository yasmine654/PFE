import { useEffect, useState } from "react";
import PageHeader from "../../PageHeader/PageHeader";
import StatsCards from "./components/StatsCards/StatsCards";
import VMTable from "./components/VMTable/VMTable";
import Filters from "./components/Filters/Filters";
import VMCrudPanel from "./components/VMCrudPanel/VMCrudPanel";

function Compute() {

  const [vms, setVMs] = useState([]);
  const [providers, setProviders] = useState([]);
  const [regions, setRegions] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [eips, setEips] = useState([]);
  const [availability_zones, setAZs] = useState([]);
  const [subnets, setSubnets] = useState([]);
  const [vpcs, setVPCs] = useState([]);

  const [editingVM, setEditingVM] = useState(null);

  const [search, setSearch] = useState("");
  const [provider, setProvider] = useState("");
  const [region, setRegion] = useState("");
  const [tenant, setTenant] = useState("");
  const [state, setState] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [
        vmRes,
        providerRes,
        regionRes,
        tenantRes,
        eipRes,
        azRes,
        subnetRes,
        vpcRes
      ] = await Promise.all([
        fetch("http://127.0.0.1:8000/vms/"),
        fetch("http://127.0.0.1:8000/providers/"),
        fetch("http://127.0.0.1:8000/regions/"),
        fetch("http://127.0.0.1:8000/tenants/"),
        fetch("http://127.0.0.1:8000/elastic_ips/"),
        fetch("http://127.0.0.1:8000/availability-zones/"),
        fetch("http://127.0.0.1:8000/subnets/"),
        fetch("http://127.0.0.1:8000/vpcs/")
      ]);

      setVMs(await vmRes.json());
      setProviders(await providerRes.json());
      setRegions(await regionRes.json());
      setTenants(await tenantRes.json());
      setEips(await eipRes.json());
      setAZs(await azRes.json());
      setSubnets(await subnetRes.json());
      setVPCs(await vpcRes.json());

    } catch (err) {
      console.error(err);
    }
  };

  const filteredVMs = vms.filter(vm => {
    return (
      vm.name.toLowerCase().includes(search.toLowerCase()) &&
      (!provider || vm.provider_id == provider) &&
      (!region || vm.region_id == region) &&
      (!tenant || vm.tenant_id == tenant) &&
      (!state || vm.state == state)
    );
  });

  return (
    <div>

      <PageHeader title="Compute - Machines Virtuelles" />

      <StatsCards />

      <Filters
        search={search}
        setSearch={setSearch}
        provider={provider}
        setProvider={setProvider}
        region={region}
        setRegion={setRegion}
        tenant={tenant}
        setTenant={setTenant}
        state={state}
        setState={setState}
        providers={providers}
        regions={regions}
        tenants={tenants}
      />

      <VMCrudPanel
        refreshData={fetchData}
        providers={providers}
        regions={regions}
        tenants={tenants}
        availability_zones={availability_zones}
        subnets={subnets}
        vpcs={vpcs}
        editingVM={editingVM}
        setEditingVM={setEditingVM}
      />

      <VMTable
        vms={filteredVMs}
        providers={providers}
        regions={regions}
        tenants={tenants}
        eips={eips}
        onEdit={setEditingVM}
      />

    </div>
  );
}

export default Compute;