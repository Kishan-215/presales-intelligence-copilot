"""Stage: detect information gaps (rule-based) and generate clarification questions (LLM)."""
import re
from typing import List, Tuple

from modules.common import StageResult, load_prompt, run_stage
from modules.demo_data import demo_clarifications
from schemas import NOT_SPECIFIED, ClarificationResult, ExtractionResult, ProjectOverview

SYSTEM_PROMPT = (
    "You are an experienced solution architect. You ask precise, gap-based questions only. "
    "You answer with valid JSON only."
)

# (key, human-readable gap, regex that would show the document already covers it)
GAP_CHECKS: List[Tuple[str, str, str]] = [
    ("concurrent_users", "Expected number of concurrent users / usage volume",
     r"concurrent|simultaneous|peak (?:load|users)|\b\d[\d,]*\s+(?:active |named )?users\b"),
    ("cloud_provider", "Preferred or mandated cloud provider",
     r"\baws\b|amazon web services|\bazure\b|google cloud|\bgcp\b"),
    ("existing_database", "Existing database or data model details",
     r"\bdatabase\b|\boracle\b|sql server|postgres|mysql|mongodb"),
    ("data_retention", "Data retention requirements",
     r"retention|retain|retained|years of (?:data|records)|\bpurge"),
    ("recovery_objectives", "Recovery objectives (RTO/RPO), backup and disaster recovery",
     r"\brto\b|\brpo\b|recovery time|recovery point|disaster recovery|\bbackup"),
    ("authentication_method", "Authentication mechanism (SSO, MFA, directory)",
     r"single sign-on|\bsso\b|\bmfa\b|multi-factor|two-factor|\bldap\b|active directory|oauth|\bsaml\b|openid"),
    ("data_residency", "Data residency / hosting location constraints",
     r"residency|in-country|within (?:the )?(?:country|india)|stored in india|data locali[sz]ation"),
    ("integration_specs", "Technical specification of the integration API",
     r"openapi|swagger|\bhl7\b|\bfhir\b|api documentation|api specification|rest api|\bsoap\b"),
    ("document_volume", "File types, size limits or document volumes",
     r"file size|\bmb\b|per day|per month|documents per|volume of documents"),
]

PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def _is_unspecified(value: str) -> bool:
    return not value or value.strip().lower() == NOT_SPECIFIED.lower()


def detect_gaps(document_text: str, overview: ProjectOverview) -> List[Tuple[str, str]]:
    """Return (key, label) for each standard piece of information the document does not mention."""
    gaps = [
        (key, label)
        for key, label, pattern in GAP_CHECKS
        if not re.search(pattern, document_text, flags=re.IGNORECASE)
    ]
    if _is_unspecified(overview.budget_information):
        gaps.append(("budget", "Budget range or funding constraints"))
    if _is_unspecified(overview.timeline_information):
        gaps.append(("launch_timeline", "Target launch date and key milestones"))
    return gaps


def postprocess_questions(result: ClarificationResult) -> ClarificationResult:
    """Remove duplicate questions, rank by priority, keep at most 10."""
    seen, unique = set(), []
    for q in result.questions:
        key = re.sub(r"\W+", " ", q.question.lower()).strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(q)
    unique.sort(key=lambda q: PRIORITY_ORDER[q.priority])  # stable sort keeps original order within a level
    result.questions = unique[:10]
    return result


def generate_clarifications(
    document_text: str, extraction: ExtractionResult, use_demo: bool = False
) -> StageResult[ClarificationResult]:
    gaps = detect_gaps(document_text, extraction.overview)
    gap_text = "\n".join(f"- {label}" for _, label in gaps) or (
        "- No standard gaps detected. Ask only about gaps visible in the requirements."
    )
    prompt = (
        load_prompt("clarification_prompt.txt")
        .replace("{requirements_json}", extraction.model_dump_json())
        .replace("{detected_gaps}", gap_text)
    )
    stage = run_stage(
        prompt=prompt,
        model_cls=ClarificationResult,
        demo_factory=demo_clarifications,
        document_text=document_text,
        use_demo=use_demo,
        system=SYSTEM_PROMPT,
    )
    stage.data = postprocess_questions(stage.data)
    return stage