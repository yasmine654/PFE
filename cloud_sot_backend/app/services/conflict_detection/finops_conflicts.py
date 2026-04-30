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

    for volume in volumes:
        if volume.vm_id is None and volume.iops and volume.iops > 1000:
            conflicts.append({
                "category": "FINOPS",
                "subcategory": "VOLUME",
                "type": "WASTED_HIGH_IOPS_VOLUME",
                "severity": "HIGH",
                "resource": "Volume",
                "resource_id": volume.volume_id,
                "primary_resource": {"type": "Volume", "id": volume.volume_id},
                "title": "Unattached high-IOPS volume",
                "message": f"Unattached high IOPS volume {volume.volume_id} wastes resources",
                "technical_summary": (
                    f"Volume {volume.volume_id} is not attached to any VM while using "
                    f"a high IOPS configuration ({volume.iops})."
                ),
                "impact": "cost",
                "recommendation": (
                    "Verify whether this volume is still required. If not, delete it or downgrade "
                    "its performance tier before deletion/archive."
                ),
                "related_resources": [],
                "metadata": {
                    "volume_id": volume.volume_id,
                    "vm_id": volume.vm_id,
                    "volume_type": getattr(volume, "type", None),
                    "size": getattr(volume, "size", None),
                    "iops": volume.iops,
                    "encrypted": getattr(volume, "encrypted", None),
                },
                "confidence": "HIGH",
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
                "primary_resource": {"type": "Volume", "id": volume.volume_id},
                "title": "Unattached volume",
                "message": f"Volume {volume.volume_id} is not attached to any VM",
                "technical_summary": (
                    f"Volume {volume.volume_id} exists without an attached VM."
                ),
                "impact": "cost",
                "recommendation": (
                    "Confirm whether the volume contains useful data. If not needed, delete it. "
                    "If it must be retained, tag it and document the retention reason."
                ),
                "related_resources": [],
                "metadata": {
                    "volume_id": volume.volume_id,
                    "vm_id": volume.vm_id,
                    "volume_type": getattr(volume, "type", None),
                    "size": getattr(volume, "size", None),
                    "iops": getattr(volume, "iops", None),
                    "encrypted": getattr(volume, "encrypted", None),
                },
                "confidence": "HIGH",
            })

    for eip in elastic_ips:
        if not eip.vm and not eip.vpn_gateway and not eip.waf:
            conflicts.append({
                "category": "FINOPS",
                "subcategory": "ELASTIC_IP",
                "type": "UNATTACHED_ELASTIC_IP",
                "severity": "MEDIUM",
                "resource": "ElasticIP",
                "resource_id": eip.elastic_ip_id,
                "primary_resource": {"type": "ElasticIP", "id": eip.elastic_ip_id},
                "title": "Unused Elastic IP",
                "message": f"Elastic IP {eip.ip} is not attached to any resource",
                "technical_summary": (
                    f"Elastic IP {eip.ip} is allocated but not attached to a VM, VPN gateway, or WAF."
                ),
                "impact": "cost",
                "recommendation": (
                    "Release the Elastic IP if it is not reserved for a planned service. "
                    "Otherwise, document the reservation."
                ),
                "related_resources": [],
                "metadata": {
                    "elastic_ip_id": eip.elastic_ip_id,
                    "ip": eip.ip,
                    "attached_to_vm": getattr(eip.vm, "vm_id", None) if eip.vm else None,
                    "attached_to_vpn": getattr(eip.vpn_gateway, "vpn_id", None) if eip.vpn_gateway else None,
                    "attached_to_waf": getattr(eip.waf, "waf_id", None) if eip.waf else None,
                },
                "confidence": "HIGH",
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
                "primary_resource": {"type": "ElasticIP", "id": eip.elastic_ip_id},
                "title": "Elastic IP attached to stopped VM",
                "message": f"Elastic IP {eip.ip} is attached to stopped VM {eip.vm.name}",
                "technical_summary": (
                    f"Elastic IP {eip.ip} remains attached to stopped VM {eip.vm.name} "
                    f"(VM ID {eip.vm.vm_id})."
                ),
                "impact": "cost",
                "recommendation": (
                    "Check whether the stopped VM must keep its public IP. If not, detach or release "
                    "the Elastic IP."
                ),
                "related_resources": [eip.vm.vm_id],
                "metadata": {
                    "elastic_ip_id": eip.elastic_ip_id,
                    "ip": eip.ip,
                    "vm_id": eip.vm.vm_id,
                    "vm_name": eip.vm.name,
                    "vm_state": eip.vm.state,
                },
                "confidence": "HIGH",
            })

    logger.info(f"{len(conflicts)} FinOps conflicts detected")
    return conflicts