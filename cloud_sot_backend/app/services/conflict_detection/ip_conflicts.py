from app.models.vm import VM
from collections import defaultdict
import ipaddress
import logging

logger = logging.getLogger(__name__)


class ConflictDetectionError(Exception):
    pass


def detect_ip_conflicts(db):
    conflicts = []

    # =========================
    # LOAD DATA + ERROR HANDLING
    # =========================
    try:
        vms = db.query(VM).all()
    except Exception as e:
        logger.error(f"Database error while fetching VMs: {e}")
        raise ConflictDetectionError("DB unavailable") from e

    # =========================
    # 🔴 MAPS
    # =========================
    subnet_ip_map = defaultdict(list)
    vpc_ip_map = defaultdict(list)

    # =========================
    # 🔴 1. VALIDATION + GROUPING
    # =========================
    for vm in vms:

        if not vm.private_ip:
            continue

        try:
            ip = ipaddress.ip_address(vm.private_ip)
        except ValueError:
            logger.warning(f"Invalid IP detected (VM {vm.vm_id}): {vm.private_ip}")
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
            continue  # ✅ CORRECT

        if vm.subnet_id:
            subnet_id = vm.subnet_id
            subnet_ip_map[(subnet_id, ip)].append(vm.vm_id)

        if vm.vpc_id:
            vpc_ip_map[(vm.vpc_id, ip)].append(vm.vm_id)

    # =========================
    # 🔴 2. DUPLICATE IP (SUBNET - CRITICAL)
    # =========================
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
                "related_resources": vm_ids
            })

    # =========================
    # 🔴 3. DUPLICATE IP (VPC - HIGH)
    # =========================
    for (vpc_id, ip), vm_ids in vpc_ip_map.items():

        if len(vm_ids) <= 1:
            continue

        key = (frozenset(vm_ids), ip)

        # 🔥 éviter doublon avec subnet
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

    logger.info(f"{len(conflicts)} IP conflicts detected")

    return conflicts