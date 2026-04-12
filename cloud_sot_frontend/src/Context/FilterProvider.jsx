import { useState } from "react";
import { FilterContext } from "./FilterContext";

export default function FilterProvider({ children }) {
  const [tenant, setTenant] = useState("");
  const [provider, setProvider] = useState("");
  const [region, setRegion] = useState("");

  return (
    <FilterContext.Provider value={{
      tenant, setTenant,
      provider, setProvider,
      region, setRegion
    }}>
      {children}
    </FilterContext.Provider>
  );
}