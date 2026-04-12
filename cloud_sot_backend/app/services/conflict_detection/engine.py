# app/services/conflict_detection/engine.py

from app.services.conflict_detection.ip_conflicts import detect_ip_conflicts
from app.services.conflict_detection.network_conflicts import detect_network_conflicts
from app.services.conflict_detection.security_conflicts import detect_security_conflicts

def detect_all_conflicts(db):
    conflicts = []

    conflicts.extend(detect_ip_conflicts(db))
    conflicts.extend(detect_network_conflicts(db))
    conflicts.extend(detect_security_conflicts(db))

    return conflicts