import ipaddress
import logging
from app.models.vpc import VPC
from app.models.subnet import Subnet
from app.models.vm import VM

logger = logging.getLogger(__name__)


class ConflictDetectionError(Exception):
    pass


def detect_network_conflicts(db, vpcs=None, subnets=None, vms=None):
    conflicts = []

    try:
        if vpcs is None:
            vpcs = db.query(VPC).all()
        if subnets is None:
            subnets = db.query(Subnet).all()
        if vms is None:
            vms = db.query(VM).all()
    except Exception as e:
        logger.error(f"Database error while fetching resources: {e}")
        raise ConflictDetectionError("DB unavailable") from e

    net_cache = {}

    def get_network(cidr):
        if not cidr:
            return None
        if cidr in net_cache:
            return net_cache[cidr]
        try:
            net = ipaddress.ip_network(cidr, strict=False)
            net_cache[cidr] = net
            return net
        except ValueError:
            net_cache[cidr] = None
            return None

    for vpc in vpcs:
        if not get_network(vpc.cidr):
            logger.warning(f"Invalid CIDR (VPC {vpc.vpc_id}): {vpc.cidr}")
            conflicts.append({
                "category": "NETWORK",
                "subcategory": "VPC",
                "type": "INVALID_CIDR",
                "severity": "HIGH",
                "resource": "VPC",
                "resource_id": vpc.vpc_id,
                "primary_resource": {"type": "VPC", "id": vpc.vpc_id},
                "title": "Invalid VPC CIDR",
                "message": f"Invalid CIDR: {vpc.cidr}",
                "technical_summary": (
                    f"VPC {vpc.vpc_id} has invalid CIDR '{vpc.cidr}'."
                ),
                "impact": "network",
                "recommendation": (
                    "Replace the CIDR with a valid IPv4/IPv6 network prefix, then re-check dependent subnets."
                ),
                "related_resources": [vpc.vpc_id],
                "metadata": {
                    "vpc_id": vpc.vpc_id,
                    "vpc_name": getattr(vpc, "name", None),
                    "cidr": vpc.cidr,
                    "tenant_id": getattr(vpc, "tenant_id", None),
                    "account_id": getattr(vpc, "account_id", None),
                    "provider_id": getattr(vpc, "provider_id", None),
                    "region_id": getattr(vpc, "region_id", None),
                },
                "confidence": "HIGH",
            })

    for subnet in subnets:
        if not get_network(subnet.cidr):
            logger.warning(f"Invalid CIDR (Subnet {subnet.subnet_id}): {subnet.cidr}")
            conflicts.append({
                "category": "NETWORK",
                "subcategory": "SUBNET",
                "type": "INVALID_CIDR",
                "severity": "HIGH",
                "resource": "Subnet",
                "resource_id": subnet.subnet_id,
                "primary_resource": {"type": "Subnet", "id": subnet.subnet_id},
                "title": "Invalid subnet CIDR",
                "message": f"Invalid CIDR: {subnet.cidr}",
                "technical_summary": (
                    f"Subnet {subnet.subnet_id} has invalid CIDR '{subnet.cidr}'."
                ),
                "impact": "network",
                "recommendation": (
                    "Correct the subnet CIDR and ensure it is contained inside its parent VPC CIDR."
                ),
                "related_resources": [subnet.subnet_id],
                "metadata": {
                    "subnet_id": subnet.subnet_id,
                    "cidr": subnet.cidr,
                    "vpc_id": subnet.vpc_id,
                    "az_id": getattr(subnet, "az_id", None),
                },
                "confidence": "HIGH",
            })

    for i in range(len(vpcs)):
        for j in range(i + 1, len(vpcs)):
            vpc1 = vpcs[i]
            vpc2 = vpcs[j]

            if vpc1.region_id != vpc2.region_id:
                continue
            if vpc1.tenant_id != vpc2.tenant_id:
                continue
            if getattr(vpc1, "account_id", None) != getattr(vpc2, "account_id", None):
                continue

            net1 = get_network(vpc1.cidr)
            net2 = get_network(vpc2.cidr)

            if not net1 or not net2:
                continue

            if net1.overlaps(net2):
                conflicts.append({
                    "category": "NETWORK",
                    "subcategory": "VPC",
                    "type": "CIDR_OVERLAP",
                    "severity": "HIGH",
                    "resource": "VPC",
                    "resource_id": vpc1.vpc_id,
                    "primary_resource": {"type": "VPC", "id": vpc1.vpc_id},
                    "title": "Overlapping VPC CIDR ranges",
                    "message": f"CIDR overlap between {vpc1.cidr} and {vpc2.cidr}",
                    "technical_summary": (
                        f"VPC {vpc1.vpc_id} ({vpc1.cidr}) overlaps with VPC "
                        f"{vpc2.vpc_id} ({vpc2.cidr}) in the same tenant/account/region scope."
                    ),
                    "impact": "network",
                    "recommendation": (
                        "Reassign one of the VPC CIDR ranges before establishing routing, peering, VPN, "
                        "or interconnection between these networks."
                    ),
                    "related_resources": [vpc1.vpc_id, vpc2.vpc_id],
                    "metadata": {
                        "vpc_1_id": vpc1.vpc_id,
                        "vpc_1_cidr": vpc1.cidr,
                        "vpc_2_id": vpc2.vpc_id,
                        "vpc_2_cidr": vpc2.cidr,
                        "tenant_id": vpc1.tenant_id,
                        "account_id": getattr(vpc1, "account_id", None),
                        "region_id": vpc1.region_id,
                    },
                    "confidence": "HIGH",
                })

    vpc_map = {v.vpc_id: v for v in vpcs}

    for subnet in subnets:
        vpc = vpc_map.get(subnet.vpc_id)
        if not vpc:
            continue

        subnet_net = get_network(subnet.cidr)
        vpc_net = get_network(vpc.cidr)

        if not subnet_net or not vpc_net:
            continue

        if not subnet_net.subnet_of(vpc_net):
            conflicts.append({
                "category": "NETWORK",
                "subcategory": "SUBNET",
                "type": "SUBNET_OUTSIDE_VPC",
                "severity": "HIGH",
                "resource": "Subnet",
                "resource_id": subnet.subnet_id,
                "primary_resource": {"type": "Subnet", "id": subnet.subnet_id},
                "title": "Subnet outside parent VPC CIDR",
                "message": f"Subnet {subnet.cidr} not inside VPC {vpc.cidr}",
                "technical_summary": (
                    f"Subnet {subnet.subnet_id} ({subnet.cidr}) is attached to VPC "
                    f"{vpc.vpc_id}, but its CIDR is not contained in the VPC CIDR {vpc.cidr}."
                ),
                "impact": "network",
                "recommendation": (
                    "Move the subnet to the correct VPC or change its CIDR so it falls inside the parent VPC range."
                ),
                "related_resources": [subnet.subnet_id, vpc.vpc_id],
                "metadata": {
                    "subnet_id": subnet.subnet_id,
                    "subnet_cidr": subnet.cidr,
                    "vpc_id": vpc.vpc_id,
                    "vpc_cidr": vpc.cidr,
                    "az_id": getattr(subnet, "az_id", None),
                },
                "confidence": "HIGH",
            })

    for i in range(len(subnets)):
        for j in range(i + 1, len(subnets)):
            s1 = subnets[i]
            s2 = subnets[j]

            if s1.vpc_id != s2.vpc_id:
                continue

            net1 = get_network(s1.cidr)
            net2 = get_network(s2.cidr)

            if not net1 or not net2:
                continue

            if net1.overlaps(net2):
                conflicts.append({
                    "category": "NETWORK",
                    "subcategory": "SUBNET",
                    "type": "SUBNET_OVERLAP",
                    "severity": "HIGH",
                    "resource": "Subnet",
                    "resource_id": s1.subnet_id,
                    "primary_resource": {"type": "Subnet", "id": s1.subnet_id},
                    "title": "Overlapping subnets inside same VPC",
                    "message": f"Overlap between {s1.cidr} and {s2.cidr}",
                    "technical_summary": (
                        f"Subnet {s1.subnet_id} ({s1.cidr}) overlaps with subnet "
                        f"{s2.subnet_id} ({s2.cidr}) inside VPC {s1.vpc_id}."
                    ),
                    "impact": "network",
                    "recommendation": (
                        "Redesign the subnet CIDR plan so each subnet in the VPC has a unique, non-overlapping range."
                    ),
                    "related_resources": [s1.subnet_id, s2.subnet_id],
                    "metadata": {
                        "subnet_1_id": s1.subnet_id,
                        "subnet_1_cidr": s1.cidr,
                        "subnet_2_id": s2.subnet_id,
                        "subnet_2_cidr": s2.cidr,
                        "vpc_id": s1.vpc_id,
                    },
                    "confidence": "HIGH",
                })

    subnet_map = {s.subnet_id: s for s in subnets}

    for vm in vms:
        if not vm.private_ip or not vm.subnet_id:
            continue

        subnet = subnet_map.get(vm.subnet_id)
        if not subnet:
            continue

        subnet_net = get_network(subnet.cidr)

        try:
            ip = ipaddress.ip_address(vm.private_ip)
        except ValueError:
            continue

        if subnet_net and ip not in subnet_net:
            conflicts.append({
                "category": "NETWORK",
                "subcategory": "VM",
                "type": "VM_OUTSIDE_SUBNET",
                "severity": "HIGH",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "primary_resource": {"type": "VM", "id": vm.vm_id},
                "title": "VM private IP outside subnet CIDR",
                "message": f"VM IP {vm.private_ip} not in subnet {subnet.cidr}",
                "technical_summary": (
                    f"VM {vm.vm_id} has private IP {vm.private_ip}, but it is attached to "
                    f"subnet {subnet.subnet_id} with CIDR {subnet.cidr}."
                ),
                "impact": "network",
                "recommendation": (
                    "Move the VM to the correct subnet or assign a private IP that belongs to the current subnet CIDR."
                ),
                "related_resources": [vm.vm_id, subnet.subnet_id],
                "metadata": {
                    "vm_id": vm.vm_id,
                    "vm_name": getattr(vm, "name", None),
                    "private_ip": vm.private_ip,
                    "subnet_id": subnet.subnet_id,
                    "subnet_cidr": subnet.cidr,
                    "vpc_id": getattr(vm, "vpc_id", None),
                },
                "confidence": "HIGH",
            })

    logger.info(f"{len(conflicts)} network conflicts detected")
    return conflicts