from app.models.vm import VM
from app.models.security_group import SecurityGroup
from app.models.acl import ACL

from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ConflictDetectionError(Exception):
    pass


DANGEROUS_PORTS = {22, 3389}


def detect_security_conflicts(db):
    conflicts = []

    # =========================
    # 🔴 LOAD DATA
    # =========================
    try:
        vms = db.query(VM).all()
        sgs = db.query(SecurityGroup).all()
        acls = db.query(ACL).all()
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
    # 🔴 VM + SG DETECTION
    # =========================
    for vm in vms:

        is_public = vm.elastic_ip_id is not None
        rules = sg_map.get(vm.vm_id, [])
        inbound_rules = [r for r in rules if r.direction == "inbound"]

        if not rules:
            if is_public:
                conflicts.append({
                    "category": "SECURITY",
                    "subcategory": "VM",
                    "type": "PUBLIC_WITHOUT_PROTECTION",
                    "severity": "CRITICAL",
                    "resource": "VM",
                    "resource_id": vm.vm_id,
                    "message": f"Public VM {vm.name} has no security group",
                    "related_resources": [vm.elastic_ip_id]
                })
            else:
                conflicts.append({
                    "category": "SECURITY",
                    "subcategory": "VM",
                    "type": "NO_SECURITY_GROUP",
                    "severity": "HIGH",
                    "resource": "VM",
                    "resource_id": vm.vm_id,
                    "message": f"Private VM {vm.name} has no security group",
                    "related_resources": []
                })
            continue

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

        dangerous_ports = set()
        open_to_world = False

        for r in inbound_rules:
            if r.port in DANGEROUS_PORTS:
                dangerous_ports.add(r.port)

            if r.source == "0.0.0.0/0":
                open_to_world = True

        if is_public and dangerous_ports and open_to_world:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "FULLY_EXPOSED_VM",
                "severity": "CRITICAL",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "subnet_id": vm.subnet_id,
                "message": f"Public VM {vm.name} fully exposed",
                "related_resources": [vm.elastic_ip_id]
            })
            continue

        if is_public and dangerous_ports:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "CRITICAL_EXPOSED_VM",
                "severity": "CRITICAL",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "subnet_id": vm.subnet_id,
                "message": f"Public VM {vm.name} exposes dangerous ports {list(dangerous_ports)}",
                "related_resources": [vm.elastic_ip_id]
            })
            continue

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

        if is_public:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "EXPOSED_VM",
                "severity": "MEDIUM",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "subnet_id": vm.subnet_id,
                "message": f"VM {vm.name} exposed to internet",
                "related_resources": [vm.elastic_ip_id]
            })

    # =========================
    # 🔴 ACL DETECTION (FIX FINAL)
    # =========================
    acl_map = defaultdict(list)
    for acl in acls:
        acl_map[acl.subnet_id].append(acl)

    for subnet_id, rules in acl_map.items():

        dangerous_acl_ids = set()
        shadow_acl_ids = set()
        conflict_acl_ids = set()

        # 🔴 DANGEROUS
        for r in rules:
            if (
                r.direction == "in"
                and r.source_ip == "0.0.0.0/0"
                and r.action == "allow"
                and (
                    r.destination_port is None
                    or r.destination_port in DANGEROUS_PORTS
                )
            ):
                dangerous_acl_ids.add(r.acl_id)

                conflicts.append({
                    "category": "SECURITY",
                    "subcategory": "ACL",
                    "type": "ACL_DANGEROUS_PORT_OPEN",
                    "severity": "CRITICAL",
                    "resource": "Subnet",
                    "resource_id": subnet_id,
                    "message": f"Dangerous port {r.destination_port or 'ALL'} open to internet",
                    "related_resources": [r.acl_id]
                })

        # 🔴 COMPARISON
        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):

                r1 = rules[i]
                r2 = rules[j]

                if (
                    r1.direction == r2.direction
                    and r1.source_ip == r2.source_ip
                    and r1.destination_port == r2.destination_port
                    and r1.action != r2.action
                ):
                    conflict_acl_ids.update([r1.acl_id, r2.acl_id])

                    conflicts.append({
                        "category": "SECURITY",
                        "subcategory": "ACL",
                        "type": "ACL_CONFLICT_RULE",
                        "severity": "CRITICAL",
                        "resource": "Subnet",
                        "resource_id": subnet_id,
                        "message": "Conflicting ACL rules",
                        "related_resources": [r1.acl_id, r2.acl_id]
                    })

                if (
                    r1.direction == "in"
                    and r2.direction == "in"
                    and r1.source_ip == "0.0.0.0/0"
                    and r2.source_ip != "0.0.0.0/0"
                    and (
                        r1.destination_port is None
                        or r1.destination_port == r2.destination_port
                    )
                    and r1.action == "allow"
                    and r2.action == "block"
                ):
                    shadow_acl_ids.update([r1.acl_id, r2.acl_id])

                    conflicts.append({
                        "category": "SECURITY",
                        "subcategory": "ACL",
                        "type": "ACL_SHADOW_RULE",
                        "severity": "HIGH",
                        "resource": "Subnet",
                        "resource_id": subnet_id,
                        "message": "Specific rule shadowed by global allow",
                        "related_resources": [r1.acl_id, r2.acl_id]
                    })

        # 🔴 ALLOW ALL
        for r in rules:
            if (
                r.direction == "in"
                and r.source_ip == "0.0.0.0/0"
                and r.action == "allow"
                and r.acl_id not in dangerous_acl_ids
                and r.acl_id not in shadow_acl_ids
                and r.acl_id not in conflict_acl_ids
            ):
                conflicts.append({
                    "category": "SECURITY",
                    "subcategory": "ACL",
                    "type": "ACL_ALLOW_ALL_INBOUND",
                    "severity": "HIGH",
                    "resource": "Subnet",
                    "resource_id": subnet_id,
                    "message": "Subnet allows all inbound traffic",
                    "related_resources": [r.acl_id]
                })

        # 🔴 DENY ALL
        inbound = [r for r in rules if r.direction == "in"]

        if inbound and all(r.action == "block" for r in inbound):
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "ACL",
                "type": "ACL_DENY_ALL_INBOUND",
                "severity": "HIGH",
                "resource": "Subnet",
                "resource_id": subnet_id,
                "message": "All inbound traffic is blocked",
                "related_resources": [r.acl_id for r in inbound]
            })

    return conflicts