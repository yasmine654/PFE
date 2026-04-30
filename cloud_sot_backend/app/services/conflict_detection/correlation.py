def _correlated_conflict(
    conflict_type,
    severity,
    message,
    title,
    technical_summary,
    impact,
    recommendation,
    caused_by,
    primary_resource=None,
    related_resources=None,
    metadata=None,
):
    return {
        "category": "CORRELATED",
        "subcategory": "MULTI_SIGNAL",
        "type": conflict_type,
        "severity": severity,
        "resource": primary_resource.get("type") if primary_resource else None,
        "resource_id": primary_resource.get("id") if primary_resource else None,
        "primary_resource": primary_resource,
        "title": title,
        "message": message,
        "technical_summary": technical_summary,
        "impact": impact,
        "recommendation": recommendation,
        "related_resources": related_resources or [],
        "metadata": metadata or {},
        "caused_by": caused_by,
        "confidence": "HIGH",
    }


def correlate_conflicts(conflicts):
    correlated = []

    by_type = {}
    for c in conflicts:
        by_type.setdefault(c["type"], []).append(c)

    seen = set()

    for overlap in by_type.get("SUBNET_OVERLAP", []):
        overlap_subnets = set(overlap.get("related_resources", []))

        for dup in by_type.get("DUPLICATE_PRIVATE_IP_OVERLAP", []):
            resources = dup.get("related_resources", [])

            if len(resources) != 4:
                continue

            vm1, vm2, subnet1, subnet2 = resources
            ip = dup.get("ip")

            key = ("IP_CONFLICT", subnet1, subnet2, ip)

            if key in seen:
                continue

            if subnet1 in overlap_subnets and subnet2 in overlap_subnets:
                seen.add(key)
                correlated.append(_correlated_conflict(
                    conflict_type="CRITICAL_NETWORK_IP_CONFLICT",
                    severity="CRITICAL",
                    message=f"Same IP {ip} used across overlapping subnets",
                    title="Critical IP conflict caused by overlapping subnets",
                    technical_summary=(
                        f"Subnets {subnet1} and {subnet2} overlap, and the same private IP "
                        f"{ip} is used by VM {vm1} and VM {vm2}."
                    ),
                    impact="network",
                    recommendation=(
                        "Resolve the subnet overlap and reassign one of the duplicated VM IP addresses. "
                        "This must be treated as a routing/IPAM integrity issue."
                    ),
                    primary_resource={"type": "VM", "id": vm1},
                    related_resources=[vm1, vm2, subnet1, subnet2],
                    metadata={
                        "ip": ip,
                        "vm_ids": [vm1, vm2],
                        "subnet_ids": [subnet1, subnet2],
                    },
                    caused_by=[overlap, dup],
                ))

    for overlap in by_type.get("SUBNET_OVERLAP", []):
        overlap_subnets = set(overlap.get("related_resources", []))

        for vm_out in by_type.get("VM_OUTSIDE_SUBNET", []):
            vm_resources = set(vm_out.get("related_resources", []))

            key = ("ROUTING", overlap.get("resource_id"), vm_out.get("resource_id"))
            if key in seen:
                continue

            if overlap_subnets & vm_resources:
                seen.add(key)
                correlated.append(_correlated_conflict(
                    conflict_type="SUBNET_ROUTING_CONFLICT",
                    severity="HIGH",
                    message="VM outside subnet due to overlapping subnets",
                    title="Routing ambiguity caused by subnet overlap",
                    technical_summary=(
                        f"VM {vm_out.get('resource_id')} is outside its assigned subnet while the same "
                        "routing domain also contains overlapping subnets."
                    ),
                    impact="network",
                    recommendation=(
                        "Fix the subnet CIDR overlap first, then validate the VM subnet assignment and private IP."
                    ),
                    primary_resource={"type": "VM", "id": vm_out.get("resource_id")},
                    related_resources=list(overlap_subnets | vm_resources),
                    metadata={
                        "vm_id": vm_out.get("resource_id"),
                        "overlap_resource_id": overlap.get("resource_id"),
                    },
                    caused_by=[overlap, vm_out],
                ))

    for exposed in by_type.get("EXPOSED_VM", []):
        for vm_out in by_type.get("VM_OUTSIDE_SUBNET", []):
            key = ("EXPOSED_MISCONFIG", exposed.get("resource_id"), vm_out.get("resource_id"))
            if key in seen:
                continue

            if exposed.get("resource_id") == vm_out.get("resource_id"):
                vm_id = exposed.get("resource_id")
                seen.add(key)
                correlated.append(_correlated_conflict(
                    conflict_type="EXPOSED_MISCONFIGURED_VM",
                    severity="CRITICAL",
                    message=f"VM {vm_id} is exposed while its network placement is inconsistent",
                    title="Exposed VM with invalid subnet placement",
                    technical_summary=(
                        f"VM {vm_id} is publicly exposed and its private IP does not belong to the assigned subnet."
                    ),
                    impact="security",
                    recommendation=(
                        "Remove or restrict public exposure, then correct the VM subnet/IP assignment."
                    ),
                    primary_resource={"type": "VM", "id": vm_id},
                    related_resources=list(set(
                        exposed.get("related_resources", []) + vm_out.get("related_resources", [])
                    )),
                    metadata={"vm_id": vm_id},
                    caused_by=[exposed, vm_out],
                ))

    for exposed in by_type.get("FULLY_EXPOSED_VM", []):
        for dup in by_type.get("DUPLICATE_PRIVATE_IP_SUBNET", []):
            key = ("EXPOSED_DUP_IP", exposed.get("resource_id"), dup.get("resource_id"))
            if key in seen:
                continue

            dup_vms = set(dup.get("related_resources", []))

            if exposed.get("resource_id") in dup_vms:
                vm_id = exposed.get("resource_id")
                seen.add(key)
                correlated.append(_correlated_conflict(
                    conflict_type="CRITICAL_EXPOSED_DUPLICATE_VM",
                    severity="CRITICAL",
                    message=f"VM {vm_id} is exposed and shares a duplicated private IP",
                    title="Public exposure combined with duplicate private IP",
                    technical_summary=(
                        f"VM {vm_id} is publicly exposed and is also part of a duplicate private IP conflict."
                    ),
                    impact="security",
                    recommendation=(
                        "Immediately restrict public access, then resolve the duplicated private IP assignment."
                    ),
                    primary_resource={"type": "VM", "id": vm_id},
                    related_resources=list(dup_vms),
                    metadata={
                        "vm_id": vm_id,
                        "duplicated_ip": dup.get("ip"),
                    },
                    caused_by=[exposed, dup],
                ))

    for cidr in by_type.get("CIDR_OVERLAP", []):
        cidr_vpcs = set(cidr.get("related_resources", []))

        for subnet in by_type.get("SUBNET_OUTSIDE_VPC", []):
            subnet_resources = set(subnet.get("related_resources", []))

            key = ("VPC_BOUNDARY", cidr.get("resource_id"), subnet.get("resource_id"))
            if key in seen:
                continue

            if cidr_vpcs & subnet_resources:
                seen.add(key)
                correlated.append(_correlated_conflict(
                    conflict_type="VPC_BOUNDARY_CONFLICT",
                    severity="HIGH",
                    message="Subnet outside VPC boundary due to overlapping VPC CIDRs",
                    title="VPC boundary and subnet placement inconsistency",
                    technical_summary=(
                        "A VPC CIDR overlap is present and a subnet is also outside its parent VPC boundary."
                    ),
                    impact="network",
                    recommendation=(
                        "Review the VPC addressing plan, fix overlapping VPC CIDRs, and correct the subnet placement."
                    ),
                    primary_resource={"type": "Subnet", "id": subnet.get("resource_id")},
                    related_resources=list(cidr_vpcs | subnet_resources),
                    metadata={
                        "vpc_conflict_id": cidr.get("resource_id"),
                        "subnet_id": subnet.get("resource_id"),
                    },
                    caused_by=[cidr, subnet],
                ))

    for acl_danger in by_type.get("ACL_DANGEROUS_PORT_OPEN", []):
        acl_subnet_id = acl_danger.get("resource_id")

        for vm_critical in (
            by_type.get("CRITICAL_EXPOSED_VM", []) +
            by_type.get("FULLY_EXPOSED_VM", [])
        ):
            vm_subnet_id = vm_critical.get("subnet_id")

            if vm_subnet_id != acl_subnet_id:
                continue

            vm_id = vm_critical.get("resource_id")
            key = ("INTERNET_EXPOSED_DANGEROUS_PORT", acl_subnet_id, vm_id)
            if key in seen:
                continue

            seen.add(key)
            correlated.append(_correlated_conflict(
                conflict_type="INTERNET_EXPOSED_DANGEROUS_PORT",
                severity="CRITICAL",
                message=(
                    f"VM {vm_id} publicly reachable on a dangerous port confirmed by ACL on subnet {acl_subnet_id}"
                ),
                title="Internet exposure confirmed by VM and ACL signals",
                technical_summary=(
                    f"VM {vm_id} is publicly exposed and subnet {acl_subnet_id} has an ACL allowing "
                    "Internet traffic to a dangerous port."
                ),
                impact="security",
                recommendation=(
                    "Treat this as an immediate exposure. Restrict the ACL and security group sources, "
                    "close dangerous ports from the Internet, and use VPN/bastion access."
                ),
                primary_resource={"type": "VM", "id": vm_id},
                related_resources=list(set(
                    [vm_id, acl_subnet_id] +
                    acl_danger.get("related_resources", []) +
                    vm_critical.get("related_resources", [])
                )),
                metadata={
                    "vm_id": vm_id,
                    "subnet_id": acl_subnet_id,
                    "acl_conflict_type": acl_danger.get("type"),
                    "vm_conflict_type": vm_critical.get("type"),
                },
                caused_by=[acl_danger, vm_critical],
            ))

    for acl_block in by_type.get("ACL_DENY_ALL_INBOUND", []):
        acl_subnet_id = acl_block.get("resource_id")

        for vm_conflict in (
            by_type.get("EXPOSED_VM", []) +
            by_type.get("CRITICAL_EXPOSED_VM", [])
        ):
            vm_subnet_id = vm_conflict.get("subnet_id")

            if vm_subnet_id != acl_subnet_id:
                continue

            vm_id = vm_conflict.get("resource_id")
            key = ("BLOCKED_EXPOSED_VM", acl_subnet_id, vm_id)
            if key in seen:
                continue

            seen.add(key)
            correlated.append(_correlated_conflict(
                conflict_type="BLOCKED_EXPOSED_VM",
                severity="HIGH",
                message=f"VM {vm_id} is public but unreachable: ACL on subnet {acl_subnet_id} blocks all inbound traffic",
                title="Public VM blocked by subnet ACL",
                technical_summary=(
                    f"VM {vm_id} has public exposure, but subnet {acl_subnet_id} blocks all inbound traffic."
                ),
                impact="availability",
                recommendation=(
                    "Clarify the intended state: if the VM must be public, add explicit inbound ACL allow rules. "
                    "If it must stay isolated, remove the public exposure."
                ),
                primary_resource={"type": "VM", "id": vm_id},
                related_resources=list(set(
                    [vm_id, acl_subnet_id] +
                    acl_block.get("related_resources", []) +
                    vm_conflict.get("related_resources", [])
                )),
                metadata={
                    "vm_id": vm_id,
                    "subnet_id": acl_subnet_id,
                    "acl_conflict_type": acl_block.get("type"),
                    "vm_conflict_type": vm_conflict.get("type"),
                },
                caused_by=[acl_block, vm_conflict],
            ))

    return correlated