from app.models.vm import VM
from app.models.security_group import SecurityGroup
from collections import defaultdict
import logging


logger = logging.getLogger(__name__)


class ConflictDetectionError(Exception):
    pass


DANGEROUS_PORTS = {22, 3389}  # SSH / RDP


def detect_security_conflicts(db):
    conflicts = []

    # =========================
    # 🔴 LOAD DATA
    # =========================
    try:
        vms = db.query(VM).all()
        sgs = db.query(SecurityGroup).all()
    except Exception as e:
        logger.error(f"Database error while fetching security data: {e}")
        raise ConflictDetectionError("DB unavailable") from e

    # =========================
    # 🔴 BUILD MAP
    # =========================
    sg_map = defaultdict(list)

    for sg in sgs:
        sg_map[sg.vm_id].append(sg)

    # =========================
    # 🔴 DETECTION
    # =========================
    for vm in vms:

        is_public = vm.elastic_ip_id is not None
        rules = sg_map.get(vm.vm_id, [])

        inbound_rules = [r for r in rules if r.direction == "inbound"]

        # =========================
        # 🔥 1. NO SECURITY GROUP
        # =========================
        if not rules:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "NO_SECURITY_GROUP",
                "severity": "HIGH",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"VM {vm.name} has no security group",
                "related_resources": []
            })
            continue

        # =========================
        # 🔥 2. PUBLIC WITHOUT PROTECTION
        # =========================
        if is_public and not inbound_rules:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "PUBLIC_WITHOUT_PROTECTION",
                "severity": "CRITICAL",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"Public VM {vm.name} has no inbound rules",
                "related_resources": [vm.elastic_ip_id] if vm.elastic_ip_id else []
            })
            continue

        open_ports = set()
        dangerous_ports = set()
        open_to_world = False

        for r in inbound_rules:

            open_ports.add(r.port)

            if r.port in DANGEROUS_PORTS:
                dangerous_ports.add(r.port)

            if r.source == "0.0.0.0/0":
                open_to_world = True

        # =========================
        # 🔥 3. FULLY EXPOSED VM
        # =========================
        if is_public and dangerous_ports and open_to_world:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "FULLY_EXPOSED_VM",
                "severity": "CRITICAL",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"Public VM {vm.name} fully exposed (dangerous ports + open to world)",
                "related_resources": [vm.elastic_ip_id]
            })
            continue

        # =========================
        # 🔥 4. CRITICAL EXPOSED VM
        # =========================
        if is_public and dangerous_ports:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "CRITICAL_EXPOSED_VM",
                "severity": "CRITICAL",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"Public VM {vm.name} exposes dangerous ports {list(dangerous_ports)}",
                "related_resources": [vm.elastic_ip_id]
            })
            continue

        # =========================
        # 🔥 5. OVER PERMISSIVE SG (ONLY INTERNAL)
        # =========================
        if open_to_world and not is_public:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "SG",
                "type": "OVER_PERMISSIVE_SG",
                "severity": "HIGH",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"VM {vm.name} allows access from 0.0.0.0/0",
                "related_resources": []
            })

        # =========================
        # 🔴 6. EXPOSED VM
        # =========================
        if is_public:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "EXPOSED_VM",
                "severity": "MEDIUM",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"VM {vm.name} exposed to internet",
                "related_resources": [vm.elastic_ip_id]
            })

    logger.info(f"{len(conflicts)} security conflicts detected")

    return conflicts