import httpx
import json
import logging
import os
import re

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def _call_ollama(prompt: str, timeout: float = 120.0) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "top_p": 0.3,
        },
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            return _clean_llm_text(resp.json().get("response", "").strip())
    except httpx.HTTPError as e:
        logger.error(f"Ollama error: {e}")
        raise RuntimeError("LLM unavailable") from e


def _clean_llm_text(text: str) -> str:
    text = text.replace("**", "")
    text = text.replace("*", "")
    text = text.replace("Here is the output in the required format:", "")
    text = text.replace("Here is the response in the required format:", "")
    text = text.replace("Here is the output:", "")
    text = text.replace("Response:", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _compact_for_ask(c: dict) -> dict:
    return {
        "category": c.get("category"),
        "type": c.get("type"),
        "severity": c.get("severity"),
        "title": c.get("title"),
        "message": c.get("message"),
        "impact": c.get("impact"),
        "recommendation": c.get("recommendation"),
        "resource": c.get("resource"),
        "resource_id": c.get("resource_id"),
        "metadata": c.get("metadata"),
    }


def _compact_conflict(c: dict) -> dict:
    return {
        "category": c.get("category"),
        "subcategory": c.get("subcategory"),
        "type": c.get("type"),
        "severity": c.get("severity"),
        "confidence": c.get("confidence"),
        "title": c.get("title"),
        "message": c.get("message"),
        "technical_summary": c.get("technical_summary"),
        "impact": c.get("impact"),
        "recommendation": c.get("recommendation"),
        "resource": c.get("resource"),
        "resource_id": c.get("resource_id"),
        "primary_resource": c.get("primary_resource"),
        "related_resources": c.get("related_resources"),
        "metadata": c.get("metadata"),
        "caused_by": [
            {
                "category": x.get("category"),
                "subcategory": x.get("subcategory"),
                "type": x.get("type"),
                "severity": x.get("severity"),
                "confidence": x.get("confidence"),
                "title": x.get("title"),
                "message": x.get("message"),
                "technical_summary": x.get("technical_summary"),
                "impact": x.get("impact"),
                "recommendation": x.get("recommendation"),
                "resource": x.get("resource"),
                "resource_id": x.get("resource_id"),
                "metadata": x.get("metadata"),
            }
            for x in c.get("caused_by", [])
        ] or None,
    }


def _dedup(conflicts: list[dict]) -> list[dict]:
    seen = set()
    result = []

    for c in conflicts:
        key = (
            c.get("category"),
            c.get("type"),
            c.get("resource"),
            c.get("resource_id"),
            c.get("message"),
        )

        if key not in seen:
            seen.add(key)
            result.append(c)

    return result


def _priority_score(c: dict) -> int:
    type_rank = {
        "INTERNET_EXPOSED_DANGEROUS_PORT": 1000,
        "CRITICAL_EXPOSED_DUPLICATE_VM": 950,
        "EXPOSED_MISCONFIGURED_VM": 900,
        "CRITICAL_NETWORK_IP_CONFLICT": 850,
        "ACL_CONFLICT_RULE": 800,
        "FULLY_EXPOSED_VM": 750,
        "CRITICAL_EXPOSED_VM": 700,
        "PUBLIC_WITHOUT_PROTECTION": 650,
        "EXPOSED_VM": 630,
        "DUPLICATE_PRIVATE_IP_OVERLAP": 600,
        "DUPLICATE_PRIVATE_IP_SUBNET": 550,
        "DUPLICATE_PRIVATE_IP_VPC": 530,
        "SUBNET_ROUTING_CONFLICT": 500,
        "VPC_BOUNDARY_CONFLICT": 450,
        "ACL_DANGEROUS_PORT_OPEN": 430,
        "ACL_ALLOW_ALL_INBOUND": 400,
        "ACL_SHADOW_RULE": 380,
        "ACL_DENY_ALL_INBOUND": 360,
        "SUBNET_OVERLAP": 350,
        "CIDR_OVERLAP": 300,
        "INVALID_CIDR": 280,
        "VM_OUTSIDE_SUBNET": 250,
        "NO_SECURITY_GROUP": 230,
        "OVER_PERMISSIVE_SG": 210,
        "INVALID_IP": 190,
        "WASTED_HIGH_IOPS_VOLUME": 120,
        "UNATTACHED_VOLUME": 100,
        "UNATTACHED_ELASTIC_IP": 80,
        "ELASTIC_IP_STOPPED_VM": 50,
    }

    severity_rank = {
        "CRITICAL": 300,
        "HIGH": 200,
        "MEDIUM": 100,
        "LOW": 20,
    }

    impact_rank = {
        "security": 80,
        "network": 70,
        "availability": 60,
        "cost": 30,
        "governance": 20,
    }

    correlated_bonus = 500 if c.get("category") == "CORRELATED" else 0

    return (
        correlated_bonus
        + type_rank.get(c.get("type"), 0)
        + severity_rank.get(c.get("severity"), 0)
        + impact_rank.get(c.get("impact"), 0)
    )


def _rank_conflicts(conflicts: list[dict]) -> list[dict]:
    return sorted(
        _dedup(conflicts),
        key=_priority_score,
        reverse=True,
    )


def _counts_by(conflicts: list[dict], field: str) -> dict:
    result = {}

    for c in conflicts:
        key = c.get(field, "UNKNOWN")
        result[key] = result.get(key, 0) + 1

    return result


def _root_cause_sentence(conflict: dict) -> str:
    caused_by = conflict.get("caused_by") or []

    if not caused_by:
        return "not available"

    parts = []

    for item in caused_by:
        parts.append(
            f"{item.get('type')} on {item.get('resource')} {item.get('resource_id')}: "
            f"{item.get('message')}"
        )

    return "This correlated conflict is caused by: " + " | ".join(parts)


def _summary_item(c: dict) -> dict:
    return {
        "type": c.get("type"),
        "severity": c.get("severity"),
        "confidence": c.get("confidence"),
        "impact": c.get("impact"),
        "resource": c.get("resource"),
        "resource_id": c.get("resource_id"),
        "title": c.get("title"),
        "short_reason": c.get("technical_summary") or c.get("message"),
        "action": c.get("recommendation"),
        "root_cause": _root_cause_sentence(c),
        "conflict_ref": {
            "type": c.get("type"),
            "resource_id": c.get("resource_id"),
        },
    }


def _extract_section(text: str, header: str, next_headers: list[str]) -> str:
    stop_pattern = "|".join(rf"\n{re.escape(h)}\s*:?\s*\n" for h in next_headers)
    pattern = rf"{re.escape(header)}\s*:?\s*\n(.+?)(?={stop_pattern}|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def explain_conflict(conflict: dict) -> str:
    compact = _compact_conflict(conflict)

    conflict_type = conflict.get("type", "")
    conflict_message = conflict.get("message", "")
    conflict_resource = conflict.get("resource", "")
    conflict_resource_id = conflict.get("resource_id", "")
    root_cause = _root_cause_sentence(conflict)

    prompt = f"""
You are a cloud infrastructure assistant for engineers.

Analyze the conflict described in the JSON below.
Use the JSON as the only source of truth.

STRICT RULES:
- Answer only in English.
- Plain text only.
- No markdown.
- No asterisks.
- Do NOT reference any cloud provider such as AWS, Azure, or GCP.
- Do NOT invent resources.
- Do NOT invent relationships.
- Do NOT detect new conflicts.
- Do NOT modify IDs, IPs, ports, subnet IDs, VM IDs, VPC IDs, or ACL IDs.
- Do NOT repeat the same information using different wording.
- Provide useful engineering insight when possible.

Conflict JSON:
{json.dumps(compact, ensure_ascii=False, indent=2)}

Write exactly three sections with these exact headers:

Engineering analysis:
<technical explanation for a cloud engineer, based only on the JSON above>

Potential impact:
<concrete operational impact>

Recommended action:
<ordered remediation steps>

"""

    llm_output = _call_ollama(prompt, timeout=120.0)

    engineering = _extract_section(llm_output, "Engineering analysis", ["Potential impact", "Recommended action"])
    impact = _extract_section(llm_output, "Potential impact", ["Recommended action", "Engineering analysis"])
    action = _extract_section(llm_output, "Recommended action", ["Engineering analysis", "Potential impact"])

    if not engineering:
        engineering = llm_output.strip()
    if not impact:
        impact = "not available"
    if not action:
        action = "not available"

    return (
        f"Detected conflict:\n{conflict_type} — {conflict_message}\n\n"
        f"Main resource:\n{conflict_resource} {conflict_resource_id}\n\n"
        f"Engineering analysis:\n{engineering}\n\n"
        f"Root cause:\n{root_cause}\n\n"
        f"Potential impact:\n{impact}\n\n"
        f"Recommended action:\n{action}"
    )


def summarize_conflicts(conflicts: list[dict]) -> dict:
    ranked = _rank_conflicts(conflicts)

    top3 = ranked[:3]
    important = ranked[3:8]

    counts = {
        "total": len(conflicts),
        "by_severity": _counts_by(conflicts, "severity"),
        "by_category": _counts_by(conflicts, "category"),
        "by_impact": _counts_by(conflicts, "impact"),
    }

    if not top3:
        return {
            "statistics": counts,
            "top_priorities": [],
            "important_conflicts": [],
            "ai_diagnostic": "No conflicts detected.",
        }

    deterministic_top_priorities = [_summary_item(c) for c in top3]

    top_types = ", ".join(c.get("type", "") for c in top3)
    top_severities = ", ".join(c.get("severity", "") for c in top3)
    top_impacts = ", ".join(c.get("impact", "") for c in top3)
    top_categories = ", ".join(set(c.get("category", "") for c in top3))

    prompt = f"""
You are a cloud infrastructure assistant for engineers.

Write a global diagnostic based on the following summary of the top priority conflicts detected in the infrastructure.

Do NOT mention specific resource IDs, IP addresses, ports, subnet IDs, or VM names.
Do NOT reference any cloud provider such as AWS, Azure, or GCP.
Do NOT invent consequences that are not derivable from the conflict types.
Answer only in English.
Plain text only.
No markdown.
No asterisks.
Be concise and technical.
Maximum 4 sentences total.

Top conflict types: {top_types}
Severities: {top_severities}
Impact domains: {top_impacts}
Categories: {top_categories}
Total conflicts in infrastructure: {counts["total"]}
Critical count: {counts["by_severity"].get("CRITICAL", 0)}
High count: {counts["by_severity"].get("HIGH", 0)}

Write exactly:

Global diagnostic:
<2 sentences on the overall security and infrastructure posture based on the conflict types and severities above>

Key issues:
<1 sentence naming the main categories of risk present (security exposure, network inconsistencies, FinOps waste, etc.) without citing specific resources>

"""

    ai_text = _call_ollama(prompt, timeout=120.0)

    return {
        "statistics": counts,
        "top_priorities": deterministic_top_priorities,
        "important_conflicts": [_summary_item(c) for c in important],
        "ai_diagnostic": ai_text,
    }


def _select_conflicts_for_question(question: str, conflicts: list[dict]) -> list[dict]:
    q = question.lower()

    finops_kw = {"cost", "money", "saving", "waste", "unattach", "unused", "billing", "budget", "expensive", "iops", "elastic ip", "volume"}
    security_kw = {"security", "exposed", "vulnerable", "risk", "attack", "internet", "port", "firewall", "acl", "protect", "ssh", "rdp", "dangerous"}

    is_finops = any(kw in q for kw in finops_kw)
    is_security = any(kw in q for kw in security_kw)

    ranked = _rank_conflicts(conflicts)

    if is_finops and not is_security:
        finops = [c for c in conflicts if c.get("category") == "FINOPS"]
        return finops[:8]

    if is_security and not is_finops:
        security = [c for c in ranked if c.get("category") in ("SECURITY", "CORRELATED")]
        return security[:8]

    top_priority = ranked[:5]
    finops = [c for c in conflicts if c.get("category") == "FINOPS"]
    seen = {(c.get("type"), c.get("resource_id")) for c in top_priority}
    finops_extra = [c for c in finops[:3] if (c.get("type"), c.get("resource_id")) not in seen]
    return top_priority + finops_extra


def ask_question(question: str, conflicts: list[dict]) -> str:
    selected = _select_conflicts_for_question(question, conflicts)
    compact = [_compact_for_ask(c) for c in selected]

    prompt = f"""
You are a cloud infrastructure assistant for engineers.

Answer the user's question using only the detected conflicts provided below.
The conflicts are ordered by priority: index 0 is the most critical, last index is the least critical.

STRICT RULES:
- Answer only in English.
- Plain text only.
- No markdown.
- No asterisks.
- NEVER mention any cloud provider name such as AWS, Azure, or GCP.
- Do NOT invent resources, VM names, IDs, IPs, or conflict types not present in the JSON.
- Do NOT invent numerical values, prices, cost estimates, or savings figures.
- Do NOT detect new conflicts beyond what is listed.
- Use ONLY the provided JSON as source of truth.
- Use the "category" field to distinguish: SECURITY and NETWORK are infrastructure risks, FINOPS is cost waste, CORRELATED is multi-signal risk.
- Correlations: ONLY mention a relationship if it is explicitly listed inside "caused_by". If "caused_by" is absent or empty, do NOT infer any relationship between conflicts.
- VM names: use ONLY the "resource" and "resource_id" fields or names explicitly present in the JSON. Do NOT use conflict type names as VM names.
- Priority: when asked what to fix first, start from index 0 (first conflict listed). Do NOT reorder by your own judgment.
- If information needed to answer is not in the JSON, write "not available".

Detected conflicts (ordered by priority, FinOps appended last):
{json.dumps(compact, ensure_ascii=False, indent=2)}

User question:
{question}

"""

    return _call_ollama(prompt, timeout=120.0)