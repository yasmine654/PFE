import ipaddress
from app.models.vpc import VPC
from app.models.subnet import Subnet


def detect_network_conflicts(db):
    conflicts = []

    # =========================
    # 🔴 1. VPC CIDR OVERLAP
    # =========================
    vpcs = db.query(VPC).all()

    for i in range(len(vpcs)):
        for j in range(i + 1, len(vpcs)):

            vpc1 = vpcs[i]
            vpc2 = vpcs[j]

            # même région seulement
            if vpc1.region_id != vpc2.region_id:
                continue

            if vpc1.tenant_id != vpc2.tenant_id:
                continue

            if vpc1.account_id != vpc2.account_id:
                continue

            try:
                net1 = ipaddress.ip_network(vpc1.cidr, strict=False)
                net2 = ipaddress.ip_network(vpc2.cidr, strict=False)
            except ValueError:
                continue

            if net1.overlaps(net2):
                conflicts.append({
                    "type": "CIDR_OVERLAP",
                    "severity": "HIGH",
                    "resource": "VPC",
                    "resource_id": vpc1.vpc_id,
                    "message": f"CIDR overlap between {vpc1.cidr} and {vpc2.cidr}",
                    "related_resources": [vpc1.vpc_id, vpc2.vpc_id]
                })

                conflicts.append({
                    "type": "CIDR_OVERLAP",
                    "severity": "HIGH",
                    "resource": "VPC",
                    "resource_id": vpc2.vpc_id,
                    "message": f"CIDR overlap between {vpc1.cidr} and {vpc2.cidr}",
                    "related_resources": [vpc1.vpc_id, vpc2.vpc_id]
                })

    # =========================
    # 🔴 2. SUBNET OUTSIDE VPC
    # =========================
    subnets = db.query(Subnet).all()

    vpc_map = {v.vpc_id: v for v in vpcs}  # optimisation (évite requêtes répétées)

    for subnet in subnets:
        if not subnet.vpc_id:
            continue

        vpc = vpc_map.get(subnet.vpc_id)

        if not vpc:
            continue

        try:
            subnet_net = ipaddress.ip_network(subnet.cidr, strict=False)
            vpc_net = ipaddress.ip_network(vpc.cidr, strict=False)
        except ValueError:
            continue

        if not subnet_net.subnet_of(vpc_net):
            conflicts.append({
                "type": "SUBNET_OUTSIDE_VPC",
                "severity": "HIGH",
                "resource": "Subnet",
                "resource_id": subnet.subnet_id,
                "message": f"Subnet {subnet.cidr} not inside VPC {vpc.cidr}",
                "related_resources": [vpc.vpc_id]
            })

    # =========================
    # 🔴 3. SUBNET OVERLAP
    # =========================
    for i in range(len(subnets)):
        for j in range(i + 1, len(subnets)):

            s1 = subnets[i]
            s2 = subnets[j]

            # même VPC seulement
            if s1.vpc_id != s2.vpc_id:
                continue

            try:
                net1 = ipaddress.ip_network(s1.cidr, strict=False)
                net2 = ipaddress.ip_network(s2.cidr, strict=False)
            except ValueError:
                continue

            if net1.overlaps(net2):
                conflicts.append({
                    "type": "SUBNET_OVERLAP",
                    "severity": "HIGH",
                    "resource": "Subnet",
                    "resource_id": s1.subnet_id,
                    "message": f"Overlap between {s1.cidr} and {s2.cidr}",
                    "related_resources": [s1.subnet_id, s2.subnet_id]
                })

                conflicts.append({
                    "type": "SUBNET_OVERLAP",
                    "severity": "HIGH",
                    "resource": "Subnet",
                    "resource_id": s2.subnet_id,
                    "message": f"Overlap between {s1.cidr} and {s2.cidr}",
                    "related_resources": [s1.subnet_id, s2.subnet_id]
                })

    return conflicts