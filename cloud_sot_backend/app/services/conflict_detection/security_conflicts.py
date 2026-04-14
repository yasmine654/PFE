from app.models.vm import VM
import logging

logger = logging.getLogger(__name__)


class ConflictDetectionError(Exception):
    pass


def detect_security_conflicts(db):
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
    # 🔴 1. EXPOSED VM
    # =========================
    for vm in vms:

        if vm.elastic_ip_id:  # VM exposée internet

            logger.warning(f"Exposed VM detected (VM {vm.vm_id})")

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