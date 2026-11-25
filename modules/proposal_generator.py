"""Assemble the proposal draft (Markdown) from the stage results. Deterministic: no LLM call."""
import datetime
from collections import OrderedDict
from typing import Dict, List, Optional

import config

SECTION_TITLES = [
    "Project overview", "Customer business problem", "Proposed solution", "Requirements summary",
    "Recommended architecture", "Architecture diagram", "Implementation approach", "Work breakdown structure",
    "Preliminary effort estimate", "Team roles", "Technical roadmap", "Assumptions", "Risks",
    "Exclusions", "Open clarification questions", "Human review notice",
]
NOT_GENERATED = "_Not generated yet. Run the analysis to complete this section._"
_STAGE_KEYS = ("extraction", "clarification", "classification", "risks", "effort_inputs", "architecture", "roadmap")

STANDARD_EXCLUSIONS = [
    "A fixed price, contractual quotation or delivery commitment.",
    "Cloud hosting, licence and third-party service charges (these need workload data and current provider pricing).",
    "Hardware and end-user devices.",
    "Migration of existing data, unless stated in the customer document.",
    "Post go-live support and maintenance, unless agreed separately.",
    "Third-party penetration testing and formal compliance certification, unless agreed separately.",
    "Changes to systems owned by other vendors (for example the existing HMS).",
]


def _cell(text) -> str:
    return str(text).replace("|", "/").replace("\n", " ").strip() or "-"


def _table(headers: List[str], rows: List[List]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(_cell(c) for c in row) + " |")
    return "\n".join(lines)


def _bullets(items) -> str:
    return "\n".join(f"- {i}" for i in items) if items else "_Not specified_"


def _data(results: Dict, key: str):
    stage = results.get(key)
    return stage.data if stage is not None else None


def summarize_roles(estimate) -> List[tuple]:
    """(role, phases, min days, max days) with every phase counted once under its role."""
    roles: "OrderedDict[str, list]" = OrderedDict()
    for p in estimate.phases:
        entry = roles.setdefault(p.role, [[], 0, 0])
        entry[0].append(p.phase)
        entry[1] += p.min_days
        entry[2] += p.max_days
    return [(role, ", ".join(v[0]), v[1], v[2]) for role, v in roles.items()]


def _source_label(results: Dict) -> str:
    modes = {results[k].mode for k in _STAGE_KEYS if results.get(k) is not None}
    if modes == {"AI"}:
        return f"AI model ({config.LLM_MODEL})"
    if modes == {"DEMO"}:
        return "DEMO MODE - built-in sample data, not a live AI model"
    if modes:
        return "Mixed - some sections use built-in DEMO sample data"
    return "Unknown"


def _exclusions(extraction) -> List[str]:
    stated = []
    for r in extraction.requirements:
        text = f"{r.description} {r.source_excerpt}".lower()
        if any(k in text for k in ("out of scope", "outside the scope", "not in scope", "excluded")):
            stated.append(r.description)
    return stated


def generate_proposal(results: Dict) -> str:
    ext = _data(results, "extraction")
    if ext is None:
        raise ValueError("Requirement extraction is needed to build a proposal.")
    cls = _data(results, "classification")
    clar = _data(results, "clarification")
    risks = _data(results, "risks")
    arch = _data(results, "architecture")
    road = _data(results, "roadmap")
    est = results.get("estimate")
    ov = ext.overview
    n_high = sum(1 for r in ext.requirements if r.priority == "High")

    sections: List[str] = []

    def add(number: int, body: str) -> None:
        sections.append(f"## {number}. {SECTION_TITLES[number - 1]}\n\n{body}")

    categories = ", ".join(c.category for c in cls.classifications) if cls else "Not classified"
    add(1, "\n".join([
        f"- **Project:** {ov.project_name}",
        f"- **Client industry:** {ov.client_industry}",
        f"- **Project type(s):** {categories}",
        f"- **Target users:** {', '.join(ov.target_users) or 'Not specified'}",
        f"- **Cloud preference stated:** {ov.cloud_preferences}",
        f"- **Timeline stated:** {ov.timeline_information}",
        f"- **Budget stated:** {ov.budget_information}",
    ]))

    add(2, f"{ov.business_problem}\n\n**Business objectives**\n\n{_bullets(ov.business_objectives)}")

    capabilities = [r.description for r in ext.requirements if r.category in ("Functional", "AI/ML", "Integration")][:8]
    solution = (
        f"This draft addresses {len(ext.requirements)} requirements extracted from the customer document "
        f"({n_high} of high priority). Core capabilities:\n\n{_bullets(capabilities)}"
    )
    if arch:
        solution += f"\n\nThe recommended design uses managed {arch.cloud_provider} services (see sections 5 and 6)."
    add(3, solution)

    add(4, _table(
        ["ID", "Requirement", "Category", "Priority", "Missing information"],
        [[r.requirement_id, r.description, r.category, r.priority, r.missing_information] for r in ext.requirements],
    ))

    if arch:
        add(5, "\n\n".join([
            f"**Cloud provider (assumption):** {arch.cloud_provider}",
            "**Architecture assumptions**\n\n" + _bullets(arch.assumptions),
            _table(["Layer", "Component", "Suggested service", "Status", "Requirements", "Why"],
                   [[c.layer, c.component_name, c.suggested_service, c.status,
                     ", ".join(c.requirement_ids), c.reason] for c in arch.components]),
            "_Recommended = justified by the requirements. Optional = useful but not required by them._",
            "**How the components communicate**\n\n" + arch.communication_flow,
            "**Key trade-offs**\n\n" + _bullets(arch.trade_offs),
            "**Security considerations**\n\n" + _bullets(arch.security_considerations),
            "**Scalability considerations**\n\n" + _bullets(arch.scalability_considerations),
            "_No cloud cost estimate is given: costs need workload data and current provider pricing._",
        ]))
        add(6, f"```mermaid\n{arch.mermaid_diagram}\n```\n\n_Paste the code above into https://mermaid.live to view the diagram. Dashed boxes are optional._")
    else:
        add(5, NOT_GENERATED)
        add(6, NOT_GENERATED)

    if road:
        approach = [f"**{p.phase_name}** - {'; '.join(p.activities[:2])}" for p in road.phases]
        add(7, _bullets(approach) + (f"\n\n{road.notes}" if road.notes else ""))
    else:
        add(7, NOT_GENERATED)

    if est:
        wbs = []
        for p in est.phases:
            wbs.append(f"- **{p.phase}** ({p.role})")
            wbs.extend(f"  - {t}" for t in p.tasks)
        add(8, "\n".join(wbs))
        add(9, "\n\n".join([
            _table(["Phase", "Role", "Min person-days", "Max person-days"],
                   [[p.phase, p.role, p.min_days, p.max_days] for p in est.phases]),
            f"- Subtotal: {est.total_min} - {est.total_max} person-days\n"
            f"- Suggested contingency: {est.contingency_percent}% ({est.contingency_min} - {est.contingency_max} person-days)\n"
            f"- **Overall estimated range (with contingency): {est.overall_min} - {est.overall_max} person-days**",
            "**How the estimate was calculated**\n\n" + _bullets(est.drivers),
            "_" + " ".join(est.disclaimers) + "_",
        ]))
        add(10, _table(["Role", "Phases", "Min person-days", "Max person-days"],
                       [list(row) for row in summarize_roles(est)]))
    else:
        add(8, NOT_GENERATED)
        add(9, NOT_GENERATED)
        add(10, NOT_GENERATED)

    if road:
        parts = []
        for p in road.phases:
            parts.append(
                f"### {p.phase_name}\n\n**Estimated duration:** {p.estimated_duration}\n\n"
                f"**Activities**\n\n{_bullets(p.activities)}\n\n**Deliverables**\n\n{_bullets(p.deliverables)}\n\n"
                f"**Dependencies**\n\n{_bullets(p.dependencies)}\n\n**Completion criteria**\n\n{_bullets(p.completion_criteria)}"
            )
        parts.append("_Durations are indicative. No delivery dates are promised without a team size, working calendar and agreed scope._")
        add(11, "\n\n".join(parts))
    else:
        add(11, NOT_GENERATED)

    assumption_parts = []
    if risks:
        assumption_parts += [
            "### Confirmed facts (stated in the customer document)\n\n" + _bullets(risks.confirmed_facts),
            "### Assumptions (made by this draft, not stated by the customer)\n\n" + _bullets(risks.assumptions),
            "### Unknowns (information still missing)\n\n" + _bullets(risks.unknowns),
        ]
    if arch:
        assumption_parts.append("_Architecture assumptions (cloud provider, region, database engine) are listed in section 5._")
    add(12, "\n\n".join(assumption_parts) if assumption_parts else NOT_GENERATED)

    if risks:
        add(13, _table(["ID", "Severity", "Risk", "Potential impact", "Suggested mitigation", "Related requirement"],
                       [[r.risk_id, r.severity, r.description, r.potential_impact,
                         r.suggested_mitigation, r.related_requirement] for r in risks.risks]))
    else:
        add(13, NOT_GENERATED)

    stated = _exclusions(ext)
    add(14, "**Stated in the customer document**\n\n" + _bullets(stated)
        + "\n\n**Standard exclusions proposed by this draft (assumed)**\n\n" + _bullets(STANDARD_EXCLUSIONS))

    if clar and clar.questions:
        lines = []
        for i, q in enumerate(clar.questions, start=1):
            related = ", ".join(q.related_requirement_ids) or "whole project"
            lines.append(f"{i}. **[{q.priority}]** {q.question}  \n   _Why it matters:_ {q.reason} (related: {related})")
        add(15, "\n".join(lines))
    else:
        add(15, NOT_GENERATED)

    add(16, (
        "This document is an AI-assisted draft. A qualified solution architect must review and correct the "
        "requirements, architecture, estimate, risks and roadmap before it is shared with a customer or used for a decision. "
        "The effort figures are preliminary, assumption-based and not calibrated against any delivery history. "
        "It is not a quotation, a fixed price or a contractual commitment."
    ))

    header = (
        f"# Technical Proposal Draft: {ov.project_name}\n\n"
        "> **DRAFT - AI-generated. Requires human solution-architect review. Not a quotation or contractual commitment.**  \n"
        f"> Generated on {datetime.date.today().isoformat()}. Source of analysis: {_source_label(results)}."
    )
    return header + "\n\n" + "\n\n".join(sections) + "\n"