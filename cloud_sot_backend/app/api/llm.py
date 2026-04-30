from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.conflict_detection.engine import detect_all_conflicts
from app.services.llm_service import (
    explain_conflict,
    summarize_conflicts,
    ask_question,
)

router = APIRouter(prefix="/llm", tags=["LLM"])


class AskRequest(BaseModel):
    question: str


def get_conflicts(db: Session = Depends(get_db)):
    return detect_all_conflicts(db)


@router.get("/summary")
def global_summary(conflicts=Depends(get_conflicts)):
    try:
        return {
            "total": len(conflicts),
            "summary": summarize_conflicts(conflicts),
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/explain")
def explain_one(
    type: str = Query(..., description="Example: FULLY_EXPOSED_VM"),
    resource_id: int = Query(..., description="Resource ID affected by the conflict"),
    conflicts=Depends(get_conflicts),
):
    conflict = next(
        (
            c for c in conflicts
            if c.get("type") == type
            and c.get("resource_id") == resource_id
        ),
        None,
    )

    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")

    try:
        return {
            "analysis": explain_conflict(conflict),
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/ask")
def ask_free(body: AskRequest, conflicts=Depends(get_conflicts)):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    try:
        return {
            "question": body.question,
            "answer": ask_question(body.question, conflicts),
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/test-sample")
def test_sample(conflicts=Depends(get_conflicts)):
    target_types = [
        "PUBLIC_WITHOUT_PROTECTION",
        "FULLY_EXPOSED_VM",
        "ACL_CONFLICT_RULE",
        "ACL_DANGEROUS_PORT_OPEN",
        "ACL_ALLOW_ALL_INBOUND",
        "ACL_SHADOW_RULE",
        "NO_SECURITY_GROUP",
        "OVER_PERMISSIVE_SG",
        "INVALID_CIDR",
        "CIDR_OVERLAP",
        "SUBNET_OVERLAP",
        "SUBNET_OUTSIDE_VPC",
        "VM_OUTSIDE_SUBNET",
        "DUPLICATE_PRIVATE_IP_SUBNET",
        "DUPLICATE_PRIVATE_IP_VPC",
        "DUPLICATE_PRIVATE_IP_OVERLAP",
        "INVALID_IP",
        "WASTED_HIGH_IOPS_VOLUME",
        "UNATTACHED_VOLUME",
        "UNATTACHED_ELASTIC_IP",
        "ELASTIC_IP_STOPPED_VM",
        "INTERNET_EXPOSED_DANGEROUS_PORT",
        "CRITICAL_EXPOSED_DUPLICATE_VM",
        "EXPOSED_MISCONFIGURED_VM",
        "CRITICAL_NETWORK_IP_CONFLICT",
        "SUBNET_ROUTING_CONFLICT",
        "VPC_BOUNDARY_CONFLICT",
    ]

    sample = {}
    for t in target_types:
        c = next((x for x in conflicts if x.get("type") == t), None)
        if c:
            sample[t] = c

    results = []
    for t, c in sample.items():
        try:
            results.append({
                "category": c.get("category"),
                "type": t,
                "resource_id": c.get("resource_id"),
                "analysis": explain_conflict(c),
            })
        except RuntimeError as e:
            results.append({
                "category": c.get("category"),
                "type": t,
                "resource_id": c.get("resource_id"),
                "error": str(e),
            })

    return {"tested": len(results), "found_types": list(sample.keys()), "results": results}
    

