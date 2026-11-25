"""Stage: preliminary effort estimate.

The LLM only suggests complexity inputs (EffortInputs). All person-day maths is plain Python,
so every number can be traced back to a visible rule.
"""
from typing import Dict, List, Tuple

from modules.common import StageResult, load_prompt, run_stage
from modules.demo_data import demo_effort_inputs
from schemas import ClassificationResult, EffortInputs, EstimateResult, ExtractionResult, PhaseEstimate

SYSTEM_PROMPT = (
    "You are an experienced presales estimator. You only choose complexity labels from the requirements. "
    "You never calculate effort. You answer with valid JSON only."
)

PHASE_ORDER = [
    "Discovery and planning", "UI/UX design", "Frontend development", "Backend development",
    "Database development", "API and integrations", "AI/ML implementation", "Testing and QA",
    "Deployment", "Documentation and handover",
]

# Baseline person-days (min, max) for a MEDIUM project before adjustments.
BASE_DAYS: Dict[str, Tuple[int, int]] = {
    "Discovery and planning": (8, 12),
    "UI/UX design": (10, 15),
    "Frontend development": (25, 35),
    "Backend development": (30, 45),
    "Database development": (8, 12),
    "API and integrations": (5, 8),
    "Deployment": (8, 12),
    "Documentation and handover": (5, 8),
}
AI_DAYS = {"Low": (10, 15), "Medium": (20, 30), "High": (35, 55)}
SIZE_FACTOR = {"Small": 0.6, "Medium": 1.0, "Large": 1.6}
SIZE_SCOPED = {
    "Discovery and planning", "UI/UX design", "Frontend development", "Backend development",
    "Database development", "Documentation and handover",
}
DEV_PHASES = [
    "Frontend development", "Backend development", "Database development",
    "API and integrations", "AI/ML implementation",
]
QA_MIN_SHARE, QA_MAX_SHARE = 0.20, 0.30
CLARITY_FACTOR = {"Clear": (1.0, 1.0), "Partial": (1.0, 1.15), "Unclear": (0.9, 1.35)}  # (min x, max x)
CONTINGENCY_BASE = {"Clear": 10, "Partial": 15, "Unclear": 20}
CONTINGENCY_CAP = 30
INTEGRATION_DAYS = (10, 18)  # extra person-days per external integration
MAX_INTEGRATIONS = 15

PHASE_INFO = {
    "Discovery and planning": {
        "role": "Business Analyst / Solution Architect",
        "tasks": ["Requirement workshops with stakeholders", "Resolve open clarification questions", "Backlog and delivery plan"],
        "dependencies": ["Customer stakeholders available for workshops"],
        "assumptions": ["Customer answers clarification questions within the first two weeks"],
    },
    "UI/UX design": {
        "role": "UI/UX Designer",
        "tasks": ["User flows and wireframes", "Visual design and component library", "Usability review with staff"],
        "dependencies": ["Discovery and planning"],
        "assumptions": ["Two design review rounds with the customer"],
    },
    "Frontend development": {
        "role": "Frontend Developer",
        "tasks": ["Build screens for each user role", "Connect screens to backend APIs", "Accessibility and browser checks"],
        "dependencies": ["UI/UX design approved", "API contracts defined"],
        "assumptions": ["Reusable component library is used"],
    },
    "Backend development": {
        "role": "Backend Developer",
        "tasks": ["Business logic and services", "Authentication and role-based access", "Audit and error handling"],
        "dependencies": ["Architecture and data model agreed"],
        "assumptions": ["Standard framework and managed cloud services are used"],
    },
    "Database development": {
        "role": "Database Engineer / Backend Developer",
        "tasks": ["Data model and migrations", "Indexes and query tuning", "Backup and retention configuration"],
        "dependencies": ["Requirements finalised"],
        "assumptions": ["No migration of existing data unless the customer states otherwise"],
    },
    "API and integrations": {
        "role": "Integration Engineer",
        "tasks": ["Design the application API", "Build and test each external integration", "Error handling and retry logic"],
        "dependencies": ["External API documentation and test access"],
        "assumptions": [],
    },
    "AI/ML implementation": {
        "role": "ML Engineer",
        "tasks": ["Select and configure the AI service or model", "Prepare evaluation data", "Measure accuracy and tune", "Human review workflow"],
        "dependencies": ["Sample documents and agreed accuracy targets"],
        "assumptions": [],
    },
    "Testing and QA": {
        "role": "QA Engineer",
        "tasks": ["Test plan and automated tests", "Security and role-permission testing", "User acceptance testing support"],
        "dependencies": ["Features complete in a test environment"],
        "assumptions": [],
    },
    "Deployment": {
        "role": "DevOps Engineer",
        "tasks": ["Environment setup", "CI/CD pipeline", "Monitoring and alerting", "Production release"],
        "dependencies": ["Architecture approved", "Testing complete"],
        "assumptions": ["Customer approves cloud account and access in time"],
    },
    "Documentation and handover": {
        "role": "Technical Writer / Project Manager",
        "tasks": ["User and admin guides", "Technical documentation", "Training session and handover"],
        "dependencies": ["Deployment complete"],
        "assumptions": ["One handover training session"],
    },
}

DISCLAIMERS = [
    "Preliminary estimate for discussion only. It is not a quotation and not a fixed price.",
    "The baseline values are generic assumptions and are not calibrated against any company's historical delivery data.",
    "Effort is in person-days, not calendar time. Duration depends on team size, working calendar and scope.",
    "A solution architect must review the inputs, rules and results before use.",
]


def _round_days(value: float) -> int:
    return max(1, int(value + 0.5))


def calculate_estimate(inputs: EffortInputs) -> EstimateResult:
    """Deterministic estimate: same inputs always give the same result."""
    n_int = min(inputs.integration_count, MAX_INTEGRATIONS)
    high_security = inputs.security_level == "High"
    size_factor = SIZE_FACTOR[inputs.size]
    clarity_lo, clarity_hi = CLARITY_FACTOR[inputs.requirement_clarity]

    drivers: List[str] = [
        f"Project size '{inputs.size}': scope-driven phases (discovery, design, frontend, backend, database, documentation) are multiplied by {size_factor}."
    ]
    raw: Dict[str, List[float]] = {}

    for name in PHASE_ORDER:
        if name == "Testing and QA":
            continue  # calculated after the development phases
        if name == "AI/ML implementation":
            if inputs.ai_complexity == "None":
                continue
            lo, hi = AI_DAYS[inputs.ai_complexity]
        else:
            lo, hi = BASE_DAYS[name]
            if name in SIZE_SCOPED:
                lo, hi = lo * size_factor, hi * size_factor
        if name == "Frontend development" and inputs.has_mobile_app:
            lo, hi = lo + 20, hi + 30
        if name == "Backend development" and high_security:
            lo, hi = lo * 1.15, hi * 1.15
        if name == "Database development" and high_security:
            lo, hi = lo * 1.10, hi * 1.10
        if name == "API and integrations":
            lo, hi = lo + n_int * INTEGRATION_DAYS[0], hi + n_int * INTEGRATION_DAYS[1]
        if name == "Deployment" and high_security:
            lo, hi = lo + 4, hi + 6
        raw[name] = [lo, hi]

    dev_lo = sum(raw[p][0] for p in DEV_PHASES if p in raw)
    dev_hi = sum(raw[p][1] for p in DEV_PHASES if p in raw)
    raw["Testing and QA"] = [dev_lo * QA_MIN_SHARE, dev_hi * QA_MAX_SHARE]

    if inputs.has_mobile_app:
        drivers.append("Mobile app requested: frontend effort increased by 20 to 30 person-days.")
    if high_security:
        drivers.append("High security level: backend x1.15, database x1.10, deployment +4 to +6 person-days.")
    drivers.append(f"{n_int} external integration(s): +{INTEGRATION_DAYS[0]} to +{INTEGRATION_DAYS[1]} person-days each on top of the base API work.")
    if inputs.ai_complexity == "None":
        drivers.append("No AI feature: AI/ML phase excluded.")
    else:
        drivers.append(f"AI complexity '{inputs.ai_complexity}': AI/ML phase set to {AI_DAYS[inputs.ai_complexity][0]} to {AI_DAYS[inputs.ai_complexity][1]} person-days.")
    drivers.append("Testing and QA = 20% (minimum) to 30% (maximum) of development effort (frontend, backend, database, integrations, AI/ML).")
    drivers.append(f"Requirement clarity '{inputs.requirement_clarity}': every phase minimum x{clarity_lo} and maximum x{clarity_hi} (unclear requirements widen the range).")

    for name in raw:
        raw[name][0] *= clarity_lo
        raw[name][1] *= clarity_hi

    extras = {
        "API and integrations": [f"Assumes {n_int} external integration(s) with documented, stable APIs."],
        "AI/ML implementation": [f"AI complexity assessed as '{inputs.ai_complexity}'."],
        "Frontend development": ["Native mobile app included."] if inputs.has_mobile_app else ["Desktop web interface only; no native mobile app."],
        "Testing and QA": ["Calculated as 20% to 30% of development effort."],
        "Deployment": ["Security hardening included (high security level)."] if high_security else [],
    }

    phases: List[PhaseEstimate] = []
    for name in PHASE_ORDER:
        if name not in raw:
            continue
        lo_days = _round_days(raw[name][0])
        hi_days = max(lo_days, _round_days(raw[name][1]))
        info = PHASE_INFO[name]
        phases.append(
            PhaseEstimate(
                phase=name, role=info["role"], tasks=list(info["tasks"]),
                min_days=lo_days, max_days=hi_days,
                dependencies=list(info["dependencies"]),
                assumptions=list(info["assumptions"]) + extras.get(name, []),
            )
        )

    total_min = sum(p.min_days for p in phases)
    total_max = sum(p.max_days for p in phases)

    pct = CONTINGENCY_BASE[inputs.requirement_clarity]
    if inputs.ai_complexity in ("Medium", "High"):
        pct += 5
    if n_int >= 3:
        pct += 5
    pct = min(pct, CONTINGENCY_CAP)
    cont_min = int(total_min * pct / 100 + 0.5)
    cont_max = int(total_max * pct / 100 + 0.5)
    drivers.append(
        f"Contingency {pct}%: base by clarity ({CONTINGENCY_BASE[inputs.requirement_clarity]}%), +5% for medium/high AI, +5% for 3 or more integrations, capped at {CONTINGENCY_CAP}%."
    )

    return EstimateResult(
        phases=phases, total_min=total_min, total_max=total_max,
        contingency_percent=pct, contingency_min=cont_min, contingency_max=cont_max,
        overall_min=total_min + cont_min, overall_max=total_max + cont_max,
        drivers=drivers, disclaimers=list(DISCLAIMERS), inputs=inputs,
    )

SIZE_ORDER = {"Small": 0, "Medium": 1, "Large": 2}


def apply_guardrails(
    inputs: EffortInputs, extraction: ExtractionResult, classification: ClassificationResult
) -> EffortInputs:
    """Rule-based sanity checks. They only RAISE under-rated complexity, and every change is written into the rationale."""
    notes: List[str] = []
    overview, reqs = extraction.overview, extraction.requirements

    listed = len([i for i in overview.required_integrations if i.strip()])
    if inputs.integration_count < listed:
        notes.append(
            f"Rule-based correction: integration count raised from {inputs.integration_count} to {listed} "
            f"because the requirements list {listed} required integration(s)."
        )
        inputs.integration_count = listed

    if (overview.compliance_requirements or any(r.category == "Compliance" for r in reqs)) and inputs.security_level != "High":
        notes.append("Rule-based correction: security level raised to High because compliance requirements are stated.")
        inputs.security_level = "High"

    has_ai = any(r.category == "AI/ML" for r in reqs) or any(
        c.category == "AI/ML implementation" for c in classification.classifications
    )
    if has_ai and inputs.ai_complexity == "None":
        notes.append("Rule-based correction: AI complexity raised from None to Low because an AI/ML requirement exists.")
        inputs.ai_complexity = "Low"

    minimum_size = "Large" if len(reqs) > 25 else "Medium" if len(reqs) >= 9 else "Small"
    if SIZE_ORDER[inputs.size] < SIZE_ORDER[minimum_size]:
        notes.append(
            f"Rule-based correction: size raised from {inputs.size} to {minimum_size} because {len(reqs)} requirements were extracted."
        )
        inputs.size = minimum_size

    inputs.rationale = list(inputs.rationale) + notes
    return inputs

def suggest_effort_inputs(
    document_text: str,
    extraction: ExtractionResult,
    classification: ClassificationResult,
    use_demo: bool = False,
) -> StageResult[EffortInputs]:
    """Ask the LLM only for complexity labels. The maths happens in calculate_estimate()."""
    prompt = (
        load_prompt("effort_prompt.txt")
        .replace("{classification_json}", classification.model_dump_json())
        .replace("{requirements_json}", extraction.model_dump_json())
    )
    stage = run_stage(
        prompt=prompt,
        model_cls=EffortInputs,
        demo_factory=demo_effort_inputs,
        document_text=document_text,
        use_demo=use_demo,
        system=SYSTEM_PROMPT,
    )
    stage.data.integration_count = min(stage.data.integration_count, MAX_INTEGRATIONS)
    return stage