from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.conflict_detection.engine import detect_all_conflicts
from app.services.conflict_detection.network_conflicts import detect_network_conflicts
from app.services.conflict_detection.ip_conflicts import detect_ip_conflicts
from app.services.conflict_detection.security_conflicts import detect_security_conflicts

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])


# =========================
# 🔴 SECURITY DATA (DEPENDENCY)
# =========================
def get_security_data(db: Session = Depends(get_db)):
    return detect_security_conflicts(db)


# =========================
# 🔴 GLOBAL
# =========================
@router.get("")
def get_all_conflicts(db: Session = Depends(get_db)):
    return detect_all_conflicts(db)


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
def get_security_conflicts(conflicts = Depends(get_security_data)):
    return conflicts


@router.get("/security/public")
def get_public_vm_conflicts(conflicts = Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["type"] in [
            "EXPOSED_VM",
            "CRITICAL_EXPOSED_VM",
            "PUBLIC_WITHOUT_PROTECTION"
        ]
    ]


@router.get("/security/critical")
def get_critical_security_conflicts(conflicts = Depends(get_security_data)):
    return [
        c for c in conflicts
        if c["severity"] == "CRITICAL"
    ]