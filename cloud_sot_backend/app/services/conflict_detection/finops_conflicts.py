from app.models.volume import Volume
from app.models.elastic_ip import ElasticIP
import logging

logger = logging.getLogger(__name__)


class ConflictDetectionError(Exception):
    pass


def detect_finops_conflicts(db):
    conflicts = []

    try:
        volumes = db.query(Volume).all()
        elastic_ips = db.query(ElasticIP).all()
    except Exception as e:
        logger.error(f"Database error while fetching FinOps data: {e}")
        raise ConflictDetectionError("DB unavailable") from e

    # =========================
    # 🟡 FINOPS — VOLUME
    # =========================
    for volume in volumes:

        if volume.vm_id is None and volume.iops and volume.iops > 1000:
            conflicts.append({
                "category": "FINOPS",
                "subcategory": "VOLUME",
                "type": "WASTED_HIGH_IOPS_VOLUME",
                "severity": "HIGH",
                "resource": "Volume",
                "resource_id": volume.volume_id,
                "message": f"Unattached high IOPS volume {volume.volume_id} wastes resources",
                "related_resources": []
            })
            continue

        if volume.vm_id is None:
            conflicts.append({
                "category": "FINOPS",
                "subcategory": "VOLUME",
                "type": "UNATTACHED_VOLUME",
                "severity": "HIGH",
                "resource": "Volume",
                "resource_id": volume.volume_id,
                "message": f"Volume {volume.volume_id} is not attached to any VM",
                "related_resources": []
            })

    # =========================
    # 🟡 FINOPS — ELASTIC IP
    # =========================
    for eip in elastic_ips:

        if not eip.vm and not eip.vpn_gateway and not eip.waf:
            conflicts.append({
                "category": "FINOPS",
                "subcategory": "ELASTIC_IP",
                "type": "UNATTACHED_ELASTIC_IP",
                "severity": "MEDIUM",
                "resource": "ElasticIP",
                "resource_id": eip.elastic_ip_id,
                "message": f"Elastic IP {eip.ip} is not attached to any resource",
                "related_resources": []
            })
            continue

        if eip.vm and eip.vm.state == "stopped":
            conflicts.append({
                "category": "FINOPS",
                "subcategory": "ELASTIC_IP",
                "type": "ELASTIC_IP_STOPPED_VM",
                "severity": "LOW",
                "resource": "ElasticIP",
                "resource_id": eip.elastic_ip_id,
                "message": f"Elastic IP {eip.ip} is attached to stopped VM {eip.vm.name}",
                "related_resources": [eip.vm.vm_id]
            })

    logger.info(f"{len(conflicts)} FinOps conflicts detected")
    return conflicts