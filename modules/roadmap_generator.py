"""Stage: phased technical roadmap."""
import re
from typing import List

from modules.common import StageResult, load_prompt, run_stage
from modules.demo_data import demo_roadmap
from schemas import ClassificationResult, EstimateResult, ExtractionResult, RoadmapResult

SYSTEM_PROMPT = (
    "You are an experienced delivery lead. You give duration ranges in weeks, never calendar dates. "
    "You answer with valid JSON only."
)

# Major phases every roadmap should cover, with keywords that identify them in a phase name.
EXPECTED_PHASES = {
    "Discovery and requirements": ["discovery", "requirement"],
    "Architecture and design": ["architecture", "design"],
    "Development": ["mvp", "development", "build"],
    "Integrations": ["integration"],
    "Testing and security": ["testing", "security", "validation"],
    "Deployment and handover": ["deployment", "handover"],
}

# DATE_PATTERN = re.compile(
#     r"\b(?:19|20)\d{2}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}\b",
#     re.IGNORECASE,
# )
_MONTH = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?"
    r"|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
DATE_PATTERN = re.compile(
    "|".join(
        [
            r"\b" + _MONTH + r"\.?\s+(?:\d{1,2}(?:st|nd|rd|th)?,?\s+)?(?:19|20)\d{2}\b",  # March 2027
            r"\b" + _MONTH + r"\.?\s+\d{1,2}(?:st|nd|rd|th)?\b",  # March 5
            r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b",  # 2027-03-05
            r"\bQ[1-4]\s*(?:19|20)\d{2}\b",  # Q3 2027
        ]
    ),
    re.IGNORECASE,
)
DATE_WARNING = "Warning: the roadmap text contains what looks like a calendar date. Dates cannot be promised without a team size and working calendar."


def missing_phases(result: RoadmapResult) -> List[str]:
    """Which major phases are not covered by any phase name (used as a completeness check)."""
    names = [p.phase_name.lower() for p in result.phases]
    return [
        label for label, keywords in EXPECTED_PHASES.items()
        if not any(any(k in name for k in keywords) for name in names)
    ]


def postprocess_roadmap(result: RoadmapResult) -> RoadmapResult:
    result.phases = [p for p in result.phases if p.phase_name.strip()]
    text = " ".join(
        [p.estimated_duration for p in result.phases]
        + [a for p in result.phases for a in p.activities + p.deliverables + p.completion_criteria]
    )
    if DATE_PATTERN.search(text) and DATE_WARNING not in result.notes:
        result.notes = f"{result.notes} {DATE_WARNING}".strip()
    return result


def _effort_summary(estimate: EstimateResult) -> str:
    lines = [f"- {p.phase}: {p.min_days}-{p.max_days} person-days" for p in estimate.phases]
    lines.append(f"- Overall with contingency: {estimate.overall_min}-{estimate.overall_max} person-days")
    return "\n".join(lines)


def generate_roadmap(
    document_text: str,
    extraction: ExtractionResult,
    classification: ClassificationResult,
    estimate: EstimateResult,
    use_demo: bool = False,
) -> StageResult[RoadmapResult]:
    prompt = (
        load_prompt("roadmap_prompt.txt")
        .replace("{classification_json}", classification.model_dump_json())
        .replace("{effort_summary}", _effort_summary(estimate))
        .replace("{requirements_json}", extraction.model_dump_json())
    )
    stage = run_stage(
        prompt=prompt, model_cls=RoadmapResult, demo_factory=demo_roadmap,
        document_text=document_text, use_demo=use_demo, system=SYSTEM_PROMPT,
    )
    stage.data = postprocess_roadmap(stage.data)
    return stage