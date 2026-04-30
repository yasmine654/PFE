from app.models.vm import VM
from collections import defaultdict
import ipaddress
import logging
from itertools import combinations

logger = logging.getLogger(__name__)


class ConflictDetectionError(Exception):
    pass


def detect_ip_conflicts(db):
    conflicts = []

    try:
        vms = db.query(VM).all()
    except Exception as e:
        logger.error(f"Database error while fetching VMs: {e}")
        raise ConflictDetectionError("DB unavailable") from e

    subnet_ip_map = defaultdict(list)
    vpc_ip_map = defaultdict(list)

    for vm in vms:
        if not vm.private_ip:
            continue

        try:
            ip = str(ipaddress.ip_address(vm.private_ip))
        except ValueError:
            conflicts.append({
                "category": "NETWORK",
                "subcategory": "IP",
                "type": "INVALID_IP",
                "severity": "HIGH",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "primary_resource": {"type": "VM", "id": vm.vm_id},
                "title": "Invalid private IP format",
                "message": f"Invalid IP format: {vm.private_ip}",
                "technical_summary": (
                    f"VM {vm.vm_id} has private_ip='{vm.private_ip}', which is not a valid IPv4/IPv6 address."
                ),
                "impact": "network",
                "recommendation": (
                    "Correct the VM private IP value and ensure it belongs to the assigned subnet CIDR."
                ),
                "related_resources": [vm.vm_id],
                "metadata": {
                    "vm_id": vm.vm_id,
                    "vm_name": getattr(vm, "name", None),
                    "private_ip": vm.private_ip,
                    "subnet_id": vm.subnet_id,
                    "vpc_id": vm.vpc_id,
                },
                "confidence": "HIGH",
            })
            continue

        if vm.subnet_id:
            subnet_ip_map[(vm.subnet_id, ip)].append(vm.vm_id)

        if vm.vpc_id:
            vpc_ip_map[(vm.vpc_id, ip)].append(vm.vm_id)

    reported_subnet_conflicts = set()

    for (subnet_id, ip), vm_ids in subnet_ip_map.items():
        if len(vm_ids) > 1:
            key = (frozenset(vm_ids), ip)
            reported_subnet_conflicts.add(key)

            conflicts.append({
                "category": "NETWORK",
                "subcategory": "IP",
                "type": "DUPLICATE_PRIVATE_IP_SUBNET",
                "severity": "CRITICAL",
                "resource": "VM",
                "resource_id": vm_ids[0],
                "primary_resource": {"type": "VM", "id": vm_ids[0]},
                "title": "Duplicate private IP inside same subnet",
                "message": f"Duplicate IP {ip} in same subnet {subnet_id}",
                "technical_summary": (
                    f"Private IP {ip} is assigned to multiple VMs inside subnet {subnet_id}."
                ),
                "impact": "network",
                "recommendation": (
                    "Assign a unique private IP to each VM in the subnet. Check DHCP/IPAM allocation "
                    "and update the duplicated VM records."
                ),
                "ip": ip,
                "related_resources": vm_ids + [subnet_id],
                "metadata": {
                    "ip": ip,
                    "subnet_id": subnet_id,
                    "vm_ids": vm_ids,
                },
                "confidence": "HIGH",
            })

    for (vpc_id, ip), vm_ids in vpc_ip_map.items():
        if len(vm_ids) <= 1:
            continue

        key = (frozenset(vm_ids), ip)

        if key in reported_subnet_conflicts:
            continue

        conflicts.append({
            "category": "NETWORK",
            "subcategory": "IP",
            "type": "DUPLICATE_PRIVATE_IP_VPC",
            "severity": "HIGH",
            "resource": "VM",
            "resource_id": vm_ids[0],
            "primary_resource": {"type": "VM", "id": vm_ids[0]},
            "title": "Duplicate private IP inside same VPC",
            "message": f"Duplicate IP {ip} across VPC {vpc_id}",
            "technical_summary": (
                f"Private IP {ip} appears on multiple VMs within VPC {vpc_id}."
            ),
            "impact": "network",
            "recommendation": (
                "Review IP allocation inside the VPC and ensure each VM has a unique private IP."
            ),
            "ip": ip,
            "related_resources": vm_ids,
            "metadata": {
                "ip": ip,
                "vpc_id": vpc_id,
                "vm_ids": vm_ids,
            },
            "confidence": "HIGH",
        })

    for vm1, vm2 in combinations(vms, 2):
        if not vm1.private_ip or not vm2.private_ip:
            continue

        if vm1.private_ip != vm2.private_ip:
            continue

        if not vm1.subnet or not vm2.subnet:
            continue

        try:
            net1 = ipaddress.ip_network(vm1.subnet.cidr, strict=False)
            net2 = ipaddress.ip_network(vm2.subnet.cidr, strict=False)
        except ValueError:
            continue

        if net1.overlaps(net2) and vm1.subnet_id != vm2.subnet_id:
            conflicts.append({
                "category": "NETWORK",
                "subcategory": "IP",
                "type": "DUPLICATE_PRIVATE_IP_OVERLAP",
                "severity": "CRITICAL",
                "resource": "VM",
                "resource_id": vm1.vm_id,
                "primary_resource": {"type": "VM", "id": vm1.vm_id},
                "title": "Duplicate private IP across overlapping subnets",
                "message": f"Same IP {vm1.private_ip} used in overlapping subnets",
                "technical_summary": (
                    f"VM {vm1.vm_id} and VM {vm2.vm_id} use the same private IP "
                    f"{vm1.private_ip} while their subnets overlap "
                    f"({vm1.subnet.cidr} and {vm2.subnet.cidr})."
                ),
                "impact": "network",
                "recommendation": (
                    "Resolve the subnet overlap or reassign one of the duplicated VM IPs. "
                    "Do not keep identical addresses in overlapping routing domains."
                ),
                "ip": vm1.private_ip,
                "related_resources": [
                    vm1.vm_id,
                    vm2.vm_id,
                    vm1.subnet_id,
                    vm2.subnet_id,
                ],
                "metadata": {
                    "ip": vm1.private_ip,
                    "vm_ids": [vm1.vm_id, vm2.vm_id],
                    "subnet_ids": [vm1.subnet_id, vm2.subnet_id],
                    "subnet_cidrs": [vm1.subnet.cidr, vm2.subnet.cidr],
                },
                "confidence": "HIGH",
            })

    return conflicts