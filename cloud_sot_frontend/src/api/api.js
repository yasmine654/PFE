const API_URL = "http://127.0.0.1:8000";

export const getVMs = async () => {
  const response = await fetch(`${API_URL}/vms/`);
  const data = await response.json();
  return data;
};
export const getVPCs = async () => {
  const res = await fetch(`${API_URL}/vpcs/`);
  return await res.json();
};

export const getSubnets = async () => {
  const res = await fetch(`${API_URL}/subnets/`);
  return await res.json();
};

// 🔥 FIX ICI
export const getPeerings = async () => {
  const res = await fetch(`${API_URL}/vpc_peerings/`);
  return await res.json();
};

// 🔥 FIX ICI
export const getEIPs = async () => {
  const res = await fetch(`${API_URL}/elastic_ips/`);
  return await res.json();
};