from app.services.conflict_detection.network_conflicts import detect_network_conflicts
from app.services.conflict_detection.ip_conflicts import detect_ip_conflicts
from app.services.conflict_detection.security_conflicts import detect_security_conflicts
from app.services.conflict_detection.finops_conflicts import detect_finops_conflicts
from app.services.conflict_detection.correlation import correlate_conflicts


def detect_all_conflicts(db):
    network = detect_network_conflicts(db)
    ip = detect_ip_conflicts(db)
    security = detect_security_conflicts(db)
    finops = detect_finops_conflicts(db)

    all_conflicts = network + ip + security + finops

    correlated = correlate_conflicts(all_conflicts)

    return all_conflicts + correlated