"""General IDP tools: knowledge search and workflow discovery."""

from __future__ import annotations

from typing import Any

from retrieval.retrieval import search_knowledge


def search_idp_knowledge(query: str, top_k: int = 5) -> str:
    """Search the IDP knowledge base for relevant policies, templates, or examples."""
    results = search_knowledge(query, top_k=top_k)
    if not results:
        return "No relevant documents found."
    lines = []
    for r in results:
        lines.append(f"**{r['title']}** ({r['type']})")
        lines.append(r.get("content", "")[:500])
        lines.append("")
    return "\n".join(lines)


def find_self_service_workflow(task_description: str) -> dict[str, Any]:
    """Recommend the best self-service workflow for a developer request."""
    keywords = {
        "k8s": "K8s Namespace Onboarding",
        "namespace": "K8s Namespace Onboarding",
        "kubernetes": "K8s Namespace Onboarding",
        "repo": "Git Repository Provisioning",
        "repository": "Git Repository Provisioning",
        "github": "Git Repository Provisioning",
        "ad group": "AD Group Management",
        "active directory": "AD Group Management",
        "cloud": "Public Cloud Onboarding",
        "aws": "Public Cloud Onboarding",
        "azure": "Azure Legacy Promotion",
        "vault": "Vault Namespace Onboarding",
        "secret": "Vault Namespace Onboarding",
        "jenkins": "Jenkins Folder Provisioning",
    }
    desc_lower = task_description.lower()
    matched = []
    for kw, workflow in keywords.items():
        if kw in desc_lower:
            matched.append(workflow)
    if not matched:
        return {"workflow": "General Self-Service Request", "confidence": "low"}
    return {"workflow": matched[0], "alternatives": matched[1:3], "confidence": "high"}
