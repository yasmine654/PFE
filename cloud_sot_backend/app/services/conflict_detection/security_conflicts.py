from app.models.vm import VM
from app.models.security_group import SecurityGroup
from collections import defaultdict
import logging


logger = logging.getLogger(__name__)


class ConflictDetectionError(Exception):
    pass


DANGEROUS_PORTS = {22, 3389}


def detect_security_conflicts(db):
    conflicts = []

    # =========================
    # 🔴 LOAD DATA + ERROR HANDLING
    # =========================
    try:
        vms = db.query(VM).all()
        sgs = db.query(SecurityGroup).all()
    except Exception as e:
        logger.error(f"Database error while fetching security data: {e}")
        raise ConflictDetectionError("DB unavailable") from e

    # =========================
    # 🔴 BUILD SG MAP
    # =========================
    sg_map = defaultdict(list)

    for sg in sgs:
        sg_map[sg.vm_id].append(sg)

    # =========================
    # 🔴 DETECTION
    # =========================
    for vm in vms:

        is_public = vm.elastic_ip_id is not None

        inbound_rules = [
            sg for sg in sg_map.get(vm.vm_id, [])
            if sg.direction == "inbound"
        ]

        open_ports = {sg.port for sg in inbound_rules}

        # =========================
        # 🔥 1. PUBLIC WITHOUT PROTECTION
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

        # =========================
        # 🔥 2. CRITICAL EXPOSED VM
        # =========================
        dangerous_open = open_ports.intersection(DANGEROUS_PORTS)

        if is_public and dangerous_open:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "CRITICAL_EXPOSED_VM",
                "severity": "CRITICAL",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"Public VM {vm.name} exposes dangerous ports {list(dangerous_open)}",
                "related_resources": [vm.elastic_ip_id] if vm.elastic_ip_id else []
            })
            continue

        # =========================
        # 🔴 3. EXPOSED VM
        # =========================
        if is_public:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "EXPOSED_VM",
                "severity": "MEDIUM",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"VM {vm.name} exposed to internet (Elastic IP attached)",
                "related_resources": [vm.elastic_ip_id]
            })

    logger.info(f"{len(conflicts)} security conflicts detected")

    return conflicts