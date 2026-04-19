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
                "message": f"Invalid IP format: {vm.private_ip}",
                "related_resources": [vm.vm_id]
            })
            continue

        if vm.subnet_id:
            subnet_ip_map[(vm.subnet_id, ip)].append(vm.vm_id)

        if vm.vpc_id:
            vpc_ip_map[(vm.vpc_id, ip)].append(vm.vm_id)

    # DUPLICATE SUBNET
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
                "message": f"Duplicate IP {ip} in same subnet {subnet_id}",
                "ip": ip,
                "related_resources": vm_ids + [subnet_id]
            })

    # DUPLICATE VPC
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
            "message": f"Duplicate IP {ip} across VPC {vpc_id}",
            "related_resources": vm_ids
        })

    # 🔥 DUPLICATE OVERLAP (IMPORTANT)
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
        except:
            continue

        if net1.overlaps(net2) and vm1.subnet_id != vm2.subnet_id:

            conflicts.append({
                "category": "NETWORK",
                "subcategory": "IP",
                "type": "DUPLICATE_PRIVATE_IP_OVERLAP",
                "severity": "CRITICAL",
                "resource": "VM",
                "resource_id": vm1.vm_id,
                "message": f"Same IP {vm1.private_ip} used in overlapping subnets",
                "ip": vm1.private_ip,
                "related_resources": [
                    vm1.vm_id,
                    vm2.vm_id,
                    vm1.subnet_id,
                    vm2.subnet_id
                ]
            })

    return conflicts