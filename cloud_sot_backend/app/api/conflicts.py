from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.conflict_detection.engine import detect_all_conflicts
from app.services.conflict_detection.network_conflicts import detect_network_conflicts
from app.services.conflict_detection.ip_conflicts import detect_ip_conflicts
from app.services.conflict_detection.security_conflicts import detect_security_conflicts

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])


# =========================
# 🔴 CACHE GLOBAL (ALL CONFLICTS)
# =========================
def get_all_conflicts_data(db: Session = Depends(get_db)):
    return detect_all_conflicts(db)


# =========================
# 🔴 SECURITY DATA
# =========================
def get_security_data(db: Session = Depends(get_db)):
    return detect_security_conflicts(db)


# =========================
# 🔴 GLOBAL
# =========================
@router.get("")
def get_all_conflicts(conflicts=Depends(get_all_conflicts_data)):
    return conflicts


# =========================
# 🔴 CORRELATED ONLY
# =========================
@router.get("/correlated")
def get_correlated_conflicts(conflicts=Depends(get_all_conflicts_data)):
    return [
        c for c in conflicts
        if c.get("category") == "CORRELATED"
    ]


# =========================
# 🔴 CORRELATED BY TYPE
# =========================

@router.get("/correlated/network-ip")
def get_network_ip_conflicts(conflicts = Depends(get_all_conflicts_data)):
    return [
        c for c in conflicts
        if c.get("type") == "CRITICAL_NETWORK_IP_CONFLICT"
    ]


@router.get("/correlated/routing")
def get_routing_conflicts(conflicts = Depends(get_all_conflicts_data)):
    return [
        c for c in conflicts
        if c.get("type") == "SUBNET_ROUTING_CONFLICT"
    ]


@router.get("/correlated/exposed-misconfig")
def get_exposed_misconfig(conflicts = Depends(get_all_conflicts_data)):
    return [
        c for c in conflicts
        if c.get("type") == "EXPOSED_MISCONFIGURED_VM"
    ]


@router.get("/correlated/exposed-duplicate")
def get_exposed_duplicate(conflicts = Depends(get_all_conflicts_data)):
    return [
        c for c in conflicts
        if c.get("type") == "CRITICAL_EXPOSED_DUPLICATE_VM"
    ]


@router.get("/correlated/vpc")
def get_vpc_conflicts(conflicts = Depends(get_all_conflicts_data)):
    return [
        c for c in conflicts
        if c.get("type") == "VPC_BOUNDARY_CONFLICT"
    ]


# =========================
# 🔴 NETWORK
# =========================
@router.get("/network")
def get_network_conflicts(db: Session = Depends(get_db)):
    return detect_network_conflicts(db)


@router.get("/network/cidr")
def get_cidr_conflicts(db: Session = Depends(get_db)):
    conflicts = detect_network_conflicts(db)
    return [c for c in conflicts if c["type"] == "INVALID_CIDR"]


@router.get("/network/overlap")
def get_overlap_conflicts(db: Session = Depends(get_db)):
    conflicts = detect_network_conflicts(db)
    return [c for c in conflicts if c["type"] == "CIDR_OVERLAP"]


@router.get("/network/subnet")
def get_subnet_conflicts(db: Session = Depends(get_db)):
    conflicts = detect_network_conflicts(db)
    return [
        c for c in conflicts
        if c["type"] in ["SUBNET_OUTSIDE_VPC", "SUBNET_OVERLAP"]
    ]


@router.get("/network/vm")
def get_vm_network_conflicts(db: Session = Depends(get_db)):
    conflicts = detect_network_conflicts(db)
    return [
        c for c in conflicts
        if c["type"] == "VM_OUTSIDE_SUBNET"
    ]


# =========================
# 🔴 IP
# =========================
@router.get("/ip")
def get_ip_conflicts(db: Session = Depends(get_db)):
    return detect_ip_conflicts(db)


@router.get("/ip/invalid")
def get_invalid_ip_conflicts(db: Session = Depends(get_db)):
    conflicts = detect_ip_conflicts(db)
    return [c for c in conflicts if c["type"] == "INVALID_IP"]


@router.get("/ip/duplicate")
def get_duplicate_ip_conflicts(db: Session = Depends(get_db)):
    conflicts = detect_ip_conflicts(db)
    return [
        c for c in conflicts
        if c["type"] in [
            "DUPLICATE_PRIVATE_IP_SUBNET",
            "DUPLICATE_PRIVATE_IP_VPC"
        ]
    ]


# =========================
# 🔴 SECURITY
# =========================
@router.get("/security")
def get_security_conflicts(conflicts=Depends(get_security_data)):
    return conflicts


@router.get("/security/public")
def get_public_vm_conflicts(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["type"] in [
            "EXPOSED_VM",
            "CRITICAL_EXPOSED_VM",
            "PUBLIC_WITHOUT_PROTECTION",
            "FULLY_EXPOSED_VM"
        ]
    ]


@router.get("/security/critical")
def get_critical_security_conflicts(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["severity"] == "CRITICAL"
    ]


@router.get("/security/sg")
def get_sg_conflicts(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["type"] == "OVER_PERMISSIVE_SG"
    ]


@router.get("/security/misconfig")
def get_misconfig_security(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["type"] == "NO_SECURITY_GROUP"
    ]

# =========================
# 🔴 ACL ROUTES (FINAL CLEAN)
# =========================

# ALL ACL
@router.get("/security/acl")
def get_acl_conflicts(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["subcategory"] == "ACL"
    ]


# CRITICAL ONLY
@router.get("/security/acl/critical")
def get_acl_critical(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["subcategory"] == "ACL"
        and c["severity"] == "CRITICAL"
    ]


# EXPOSED (internet)
@router.get("/security/acl/exposed")
def get_acl_exposed(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["subcategory"] == "ACL"
        and c["type"] in [
            "ACL_ALLOW_ALL_INBOUND",
            "ACL_DANGEROUS_PORT_OPEN"
        ]
    ]


# CONFLICT RULES
@router.get("/security/acl/conflicts")
def get_acl_conflict_rules(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["subcategory"] == "ACL"
        and c["type"] == "ACL_CONFLICT_RULE"
    ]


# SHADOW RULES
@router.get("/security/acl/shadow")
def get_acl_shadow(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["subcategory"] == "ACL"
        and c["type"] == "ACL_SHADOW_RULE"
    ]


# BLOCK ALL
@router.get("/security/acl/block")
def get_acl_block_all(conflicts=Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["subcategory"] == "ACL"
        and c["type"] == "ACL_DENY_ALL_INBOUND"
    ]