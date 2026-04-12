from app.models.vm import VM

def detect_security_conflicts(db):
    conflicts = []

    vms = db.query(VM).all()

    for vm in vms:
        if vm.elastic_ip_id:  # VM exposée via Elastic IP
            conflicts.append({
                "type": "EXPOSED_VM",
                "severity": "MEDIUM",
                "resource": "VM",
                "resource_id": vm.vm_id,
                "message": f"VM {vm.name} exposed to internet (Elastic IP attached)",
                "related_resources": [vm.elastic_ip_id]
            })

    return conflicts