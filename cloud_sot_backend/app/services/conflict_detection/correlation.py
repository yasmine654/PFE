def correlate_conflicts(conflicts):
    correlated = []

    by_type = {}
    for c in conflicts:
        by_type.setdefault(c["type"], []).append(c)

    seen = set()

    # 🔴 1. SUBNET_OVERLAP + DUPLICATE_PRIVATE_IP_OVERLAP
    for overlap in by_type.get("SUBNET_OVERLAP", []):
        overlap_subnets = set(overlap.get("related_resources", []))

        for dup in by_type.get("DUPLICATE_PRIVATE_IP_OVERLAP", []):

            resources = dup.get("related_resources", [])

            if len(resources) < 4:
                continue

            vm1, vm2, subnet1, subnet2 = resources
            ip = dup.get("ip")

            key = ("IP_CONFLICT", overlap["resource_id"], subnet1, subnet2, ip)

            if key in seen:
                continue

            if subnet1 in overlap_subnets and subnet2 in overlap_subnets:
                seen.add(key)
                correlated.append({
                    "category": "CORRELATED",
                    "type": "CRITICAL_NETWORK_IP_CONFLICT",
                    "severity": "CRITICAL",
                    "message": f"Same IP {ip} used across overlapping subnets",
                    "caused_by": [overlap, dup]
                })

    # 🔴 2
    for overlap in by_type.get("SUBNET_OVERLAP", []):
        overlap_subnets = set(overlap.get("related_resources", []))

        for vm_out in by_type.get("VM_OUTSIDE_SUBNET", []):
            vm_resources = set(vm_out.get("related_resources", []))

            key = ("ROUTING", overlap["resource_id"], vm_out["resource_id"])
            if key in seen:
                continue

            if overlap_subnets & vm_resources:
                seen.add(key)
                correlated.append({
                    "category": "CORRELATED",
                    "type": "SUBNET_ROUTING_CONFLICT",
                    "severity": "HIGH",
                    "caused_by": [overlap, vm_out]
                })

    # 🔴 3
    for exposed in by_type.get("EXPOSED_VM", []):
        for vm_out in by_type.get("VM_OUTSIDE_SUBNET", []):

            key = ("EXPOSED_MISCONFIG", exposed["resource_id"], vm_out["resource_id"])
            if key in seen:
                continue

            if exposed["resource_id"] == vm_out["resource_id"]:
                seen.add(key)
                correlated.append({
                    "category": "CORRELATED",
                    "type": "EXPOSED_MISCONFIGURED_VM",
                    "severity": "CRITICAL",
                    "caused_by": [exposed, vm_out]
                })

    # 🔴 4
    for exposed in by_type.get("FULLY_EXPOSED_VM", []):
        for dup in by_type.get("DUPLICATE_PRIVATE_IP_SUBNET", []):

            key = ("EXPOSED_DUP_IP", exposed["resource_id"], dup["resource_id"])
            if key in seen:
                continue

            dup_vms = set(dup.get("related_resources", []))

            if exposed["resource_id"] in dup_vms:
                seen.add(key)
                correlated.append({
                    "category": "CORRELATED",
                    "type": "CRITICAL_EXPOSED_DUPLICATE_VM",
                    "severity": "CRITICAL",
                    "caused_by": [exposed, dup]
                })

    # 🔴 5
    for cidr in by_type.get("CIDR_OVERLAP", []):
        cidr_vpcs = set(cidr.get("related_resources", []))

        for subnet in by_type.get("SUBNET_OUTSIDE_VPC", []):
            subnet_resources = set(subnet.get("related_resources", []))

            key = ("VPC_BOUNDARY", cidr["resource_id"], subnet["resource_id"])
            if key in seen:
                continue

            if cidr_vpcs & subnet_resources:
                seen.add(key)
                correlated.append({
                    "category": "CORRELATED",
                    "type": "VPC_BOUNDARY_CONFLICT",
                    "severity": "HIGH",
                    "caused_by": [cidr, subnet]
                })

    return correlated