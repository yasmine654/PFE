# app/services/conflict_detection/ip_conflicts.py

from app.models.vm import VM
from collections import defaultdict

def detect_ip_conflicts(db):
    conflicts = []
    
    vms = db.query(VM).all()
    
    ip_map = defaultdict(list)

    for vm in vms:
        if vm.private_ip:
            ip_map[vm.private_ip].append(vm.vm_id)

    for ip, vm_ids in ip_map.items():
        if len(vm_ids) > 1:
            for vm_id in vm_ids:
                conflicts.append({
                    "type": "DUPLICATE_PRIVATE_IP",
                    "severity": "HIGH",
                    "resource": "VM",
                    "resource_id": vm_id,
                    "message": f"Duplicate private IP {ip}",
                    "related_resources": vm_ids
                })

    return conflicts