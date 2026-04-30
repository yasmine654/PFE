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

    try:
        vms = db.query(VM).all()
        sgs = db.query(SecurityGroup).all()
        acls = db.query(ACL).all()
    except Exception as e:
        logger.error(f"Database error while fetching security data: {e}")
        raise ConflictDetectionError("DB unavailable") from e

    sg_map = defaultdict(list)
    for sg in sgs:
        sg_map[sg.vm_id].append(sg)

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
                    "primary_resource": {"type": "VM", "id": vm.vm_id},
                    "title": "Public VM without security group",
                    "message": f"Public VM {vm.name} has no security group",
                    "technical_summary": (
                        f"VM {vm.vm_id} ({vm.name}) has an Elastic IP but no security group rules."
                    ),
                    "impact": "security",
                    "recommendation": (
                        "Attach a security group with explicit inbound rules. Remove the public IP if public access is not required."
                    ),
                    "related_resources": [vm.elastic_ip_id],
                    "metadata": {
                        "vm_id": vm.vm_id,
                        "vm_name": vm.name,
                        "elastic_ip_id": vm.elastic_ip_id,
                        "subnet_id": vm.subnet_id,
                        "vpc_id": vm.vpc_id,
                    },
                    "confidence": "HIGH",
                })
            else:
                conflicts.append({
                    "category": "SECURITY",
                    "subcategory": "VM",
                    "type": "NO_SECURITY_GROUP",
                    "severity": "HIGH",
                    "resource": "VM",
                    "resource_id": vm.vm_id,
                    "primary_resource": {"type": "VM", "id": vm.vm_id},
                    "title": "VM without security group",
                    "message": f"Private VM {vm.name} has no security group",
                    "technical_summary": (
                        f"VM {vm.vm_id} ({vm.name}) has no security group associated."
                    ),
                    "impact": "security",
                    "recommendation": (
                        "Attach a baseline security group to enforce explicit inbound and outbound filtering."
                    ),
                    "related_resources": [],
                    "metadata": {
                        "vm_id": vm.vm_id,
                        "vm_name": vm.name,
                        "subnet_id": vm.subnet_id,
                        "vpc_id": vm.vpc_id,
                    },
                    "confidence": "HIGH",
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
                "primary_resource": {"type": "VM", "id": vm.vm_id},
                "title": "Public VM without inbound filtering",
                "message": f"Public VM {vm.name} has no inbound rules",
                "technical_summary": (
                    f"VM {vm.vm_id} ({vm.name}) has an Elastic IP but no inbound security group rules."
                ),
                "impact": "security",
                "recommendation": (
                    "Define explicit inbound rules or remove the public exposure if the VM should not be reachable externally."
                ),
                "related_resources": [vm.elastic_ip_id] if vm.elastic_ip_id else [],
                "metadata": {
                    "vm_id": vm.vm_id,
                    "vm_name": vm.name,
                    "elastic_ip_id": vm.elastic_ip_id,
                    "subnet_id": vm.subnet_id,
                    "vpc_id": vm.vpc_id,
                },
                "confidence": "HIGH",
            })
            continue

        dangerous_ports = set()
        open_to_world = False
        inbound_rule_ids = []

        for r in inbound_rules:
            inbound_rule_ids.append(r.sg_id)
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
                "primary_resource": {"type": "VM", "id": vm.vm_id},
                "title": "Public VM exposed to the Internet on dangerous port",
                "message": f"Public VM {vm.name} fully exposed",
                "technical_summary": (
                    f"VM {vm.vm_id} ({vm.name}) is public and allows inbound access from "
                    f"0.0.0.0/0 on dangerous ports {sorted(dangerous_ports)}."
                ),
                "impact": "security",
                "recommendation": (
                    "Restrict inbound sources, close SSH/RDP from the Internet, and use VPN, bastion, or private access."
                ),
                "subnet_id": vm.subnet_id,
                "related_resources": [vm.elastic_ip_id],
                "metadata": {
                    "vm_id": vm.vm_id,
                    "vm_name": vm.name,
                    "elastic_ip_id": vm.elastic_ip_id,
                    "subnet_id": vm.subnet_id,
                    "vpc_id": vm.vpc_id,
                    "dangerous_ports": sorted(dangerous_ports),
                    "source": "0.0.0.0/0",
                    "security_group_rule_ids": inbound_rule_ids,
                },
                "confidence": "HIGH",
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
                "primary_resource": {"type": "VM", "id": vm.vm_id},
                "title": "Public VM exposes dangerous port",
                "message": f"Public VM {vm.name} exposes dangerous ports {list(dangerous_ports)}",
                "technical_summary": (
                    f"VM {vm.vm_id} ({vm.name}) is public and exposes dangerous ports "
                    f"{sorted(dangerous_ports)}."
                ),
                "impact": "security",
                "recommendation": (
                    "Restrict access to trusted IP ranges or move administrative access behind VPN/bastion."
                ),
                "subnet_id": vm.subnet_id,
                "related_resources": [vm.elastic_ip_id],
                "metadata": {
                    "vm_id": vm.vm_id,
                    "vm_name": vm.name,
                    "elastic_ip_id": vm.elastic_ip_id,
                    "subnet_id": vm.subnet_id,
                    "vpc_id": vm.vpc_id,
                    "dangerous_ports": sorted(dangerous_ports),
                    "security_group_rule_ids": inbound_rule_ids,
                },
                "confidence": "HIGH",
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
                "primary_resource": {"type": "VM", "id": vm.vm_id},
                "title": "Over-permissive security group",
                "message": f"VM {vm.name} allows access from 0.0.0.0/0",
                "technical_summary": (
                    f"VM {vm.vm_id} ({vm.name}) is not public, but its inbound rules allow traffic from 0.0.0.0/0."
                ),
                "impact": "security",
                "recommendation": (
                    "Restrict inbound sources to required CIDR ranges even if the VM is currently private."
                ),
                "related_resources": inbound_rule_ids,
                "metadata": {
                    "vm_id": vm.vm_id,
                    "vm_name": vm.name,
                    "subnet_id": vm.subnet_id,
                    "vpc_id": vm.vpc_id,
                    "source": "0.0.0.0/0",
                    "security_group_rule_ids": inbound_rule_ids,
                },
                "confidence": "HIGH",
            })

        if is_public:
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "VM",
                "type": "EXPOSED_VM",
                "severity": "MEDIUM",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "primary_resource": {"type": "VM", "id": vm.vm_id},
                "title": "Publicly exposed VM",
                "message": f"VM {vm.name} exposed to internet",
                "technical_summary": (
                    f"VM {vm.vm_id} ({vm.name}) has public exposure through Elastic IP {vm.elastic_ip_id}."
                ),
                "impact": "security",
                "recommendation": (
                    "Validate that Internet exposure is intended. If yes, ensure least-privilege security group and ACL rules."
                ),
                "subnet_id": vm.subnet_id,
                "related_resources": [vm.elastic_ip_id],
                "metadata": {
                    "vm_id": vm.vm_id,
                    "vm_name": vm.name,
                    "elastic_ip_id": vm.elastic_ip_id,
                    "subnet_id": vm.subnet_id,
                    "vpc_id": vm.vpc_id,
                },
                "confidence": "MEDIUM",
            })

    acl_map = defaultdict(list)
    for acl in acls:
        acl_map[acl.subnet_id].append(acl)

    for subnet_id, rules in acl_map.items():
        dangerous_acl_ids = set()
        shadow_acl_ids = set()
        conflict_acl_ids = set()

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
                    "primary_resource": {"type": "Subnet", "id": subnet_id},
                    "title": "ACL allows Internet access to dangerous port",
                    "message": f"Dangerous port {r.destination_port or 'ALL'} open to internet",
                    "technical_summary": (
                        f"Subnet {subnet_id} has ACL {r.acl_id} allowing inbound traffic from "
                        f"0.0.0.0/0 to destination port {r.destination_port or 'ALL'}."
                    ),
                    "impact": "security",
                    "recommendation": (
                        "Restrict inbound ACL source CIDR and avoid exposing SSH/RDP or all ports to the Internet."
                    ),
                    "related_resources": [r.acl_id],
                    "metadata": {
                        "subnet_id": subnet_id,
                        "acl_id": r.acl_id,
                        "direction": r.direction,
                        "source_ip": r.source_ip,
                        "destination_ip": r.destination_ip,
                        "source_port": r.source_port,
                        "destination_port": r.destination_port,
                        "action": r.action,
                    },
                    "confidence": "HIGH",
                })

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
                        "primary_resource": {"type": "Subnet", "id": subnet_id},
                        "title": "Conflicting ACL rules",
                        "message": "Conflicting ACL rules",
                        "technical_summary": (
                            f"Subnet {subnet_id} has ACL rules {r1.acl_id} and {r2.acl_id} "
                            f"with same direction/source/port but opposite actions."
                        ),
                        "impact": "security",
                        "recommendation": (
                            "Remove or reorder the conflicting ACL rules so the intended policy is unambiguous."
                        ),
                        "related_resources": [r1.acl_id, r2.acl_id],
                        "metadata": {
                            "subnet_id": subnet_id,
                            "acl_1_id": r1.acl_id,
                            "acl_2_id": r2.acl_id,
                            "direction": r1.direction,
                            "source_ip": r1.source_ip,
                            "destination_port": r1.destination_port,
                            "actions": [r1.action, r2.action],
                        },
                        "confidence": "HIGH",
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
                        "primary_resource": {"type": "Subnet", "id": subnet_id},
                        "title": "ACL shadow rule",
                        "message": "Specific rule shadowed by global allow",
                        "technical_summary": (
                            f"Subnet {subnet_id} has global allow ACL {r1.acl_id} that can shadow "
                            f"the more specific block ACL {r2.acl_id}."
                        ),
                        "impact": "security",
                        "recommendation": (
                            "Review ACL order and specificity. Ensure deny rules are not bypassed by broader allow rules."
                        ),
                        "related_resources": [r1.acl_id, r2.acl_id],
                        "metadata": {
                            "subnet_id": subnet_id,
                            "global_allow_acl_id": r1.acl_id,
                            "specific_block_acl_id": r2.acl_id,
                            "global_source": r1.source_ip,
                            "specific_source": r2.source_ip,
                            "destination_port": r1.destination_port,
                        },
                        "confidence": "MEDIUM",
                    })

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
                    "primary_resource": {"type": "Subnet", "id": subnet_id},
                    "title": "ACL allows inbound traffic from Internet",
                    "message": "Subnet allows all inbound traffic",
                    "technical_summary": (
                        f"Subnet {subnet_id} has ACL {r.acl_id} allowing inbound traffic from 0.0.0.0/0."
                    ),
                    "impact": "security",
                    "recommendation": (
                        "Limit inbound ACL source ranges to trusted networks and required ports only."
                    ),
                    "related_resources": [r.acl_id],
                    "metadata": {
                        "subnet_id": subnet_id,
                        "acl_id": r.acl_id,
                        "direction": r.direction,
                        "source_ip": r.source_ip,
                        "destination_port": r.destination_port,
                        "action": r.action,
                    },
                    "confidence": "HIGH",
                })

        inbound = [r for r in rules if r.direction == "in"]

        if inbound and all(r.action == "block" for r in inbound):
            conflicts.append({
                "category": "SECURITY",
                "subcategory": "ACL",
                "type": "ACL_DENY_ALL_INBOUND",
                "severity": "HIGH",
                "resource": "Subnet",
                "resource_id": subnet_id,
                "primary_resource": {"type": "Subnet", "id": subnet_id},
                "title": "ACL blocks all inbound traffic",
                "message": "All inbound traffic is blocked",
                "technical_summary": (
                    f"All inbound ACL rules for subnet {subnet_id} are blocking traffic."
                ),
                "impact": "availability",
                "recommendation": (
                    "Confirm this subnet is intentionally isolated. If services must be reachable, add explicit allow rules."
                ),
                "related_resources": [r.acl_id for r in inbound],
                "metadata": {
                    "subnet_id": subnet_id,
                    "acl_ids": [r.acl_id for r in inbound],
                    "rule_count": len(inbound),
                },
                "confidence": "HIGH",
            })

    return conflicts