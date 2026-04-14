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

    # =========================
    # LOAD DATA + ERROR HANDLING
    # =========================
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

    # =========================
    # 1. INVALID CIDR
    # =========================
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
                "message": f"Invalid CIDR: {vpc.cidr}",
                "related_resources": [vpc.vpc_id]
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
                "message": f"Invalid CIDR: {subnet.cidr}",
                "related_resources": [subnet.subnet_id]
            })

    # =========================
    # 2. VPC OVERLAP (O(n²))
    # =========================
    for i in range(len(vpcs)):
        for j in range(i + 1, len(vpcs)):

            vpc1 = vpcs[i]
            vpc2 = vpcs[j]

            if vpc1.region_id != vpc2.region_id:
                continue
            if vpc1.tenant_id != vpc2.tenant_id:
                continue
            if vpc1.account_id != vpc2.account_id:
                continue

            logger.debug(f"Checking VPC {vpc1.vpc_id} vs {vpc2.vpc_id}")

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
                    "message": f"CIDR overlap between {vpc1.cidr} and {vpc2.cidr}",
                    "related_resources": [vpc1.vpc_id, vpc2.vpc_id]
                })

    # =========================
    # 3. SUBNET OUTSIDE VPC
    # =========================
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
                "message": f"Subnet {subnet.cidr} not inside VPC {vpc.cidr}",
                "related_resources": [subnet.subnet_id, vpc.vpc_id]
            })

    # =========================
    # 4. SUBNET OVERLAP (O(n²))
    # =========================
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
                    "message": f"Overlap between {s1.cidr} and {s2.cidr}",
                    "related_resources": [s1.subnet_id, s2.subnet_id]
                })

    # =========================
    # 5. VM OUTSIDE SUBNET
    # =========================
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
            continue  # 🔥 CORRECTION : on ignore ici

        if subnet_net and ip not in subnet_net:
            conflicts.append({
                "category": "NETWORK",
                "subcategory": "VM",
                "type": "VM_OUTSIDE_SUBNET",
                "severity": "HIGH",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"VM IP {vm.private_ip} not in subnet {subnet.cidr}",
                "related_resources": [vm.vm_id, subnet.subnet_id]
            })

    logger.info(f"{len(conflicts)} conflicts detected")

    return conflicts