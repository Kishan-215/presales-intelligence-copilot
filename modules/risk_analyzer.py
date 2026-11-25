"""Stage: risks, assumptions and unknowns."""
import re
from typing import List, Set, Tuple

from modules.clarification_generator import detect_gaps
from modules.common import StageResult, load_prompt, run_stage
from modules.demo_data import demo_risks
from schemas import NOT_SPECIFIED, ClassificationResult, ExtractionResult, RiskResult

SYSTEM_PROMPT = (
    "You are an experienced presales risk analyst. You only report risks supported by the input. "
    "You answer with valid JSON only."
)
SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def postprocess_risks(result: RiskResult, valid_ids: Set[str], gaps: List[Tuple[str, str]]) -> RiskResult:
    """Sort by severity, renumber, drop invented requirement IDs, add rule-based unknowns."""
    result.risks.sort(key=lambda r: SEVERITY_ORDER[r.severity])  # stable sort
    for n, risk in enumerate(result.risks, start=1):
        risk.risk_id = f"RISK-{n:03d}"
        found = re.findall(r"REQ-\d+", risk.related_requirement)
        if found:
            kept = [i for i in found if i in valid_ids]
            risk.related_requirement = ", ".join(kept) if kept else NOT_SPECIFIED
    for _, label in gaps:
        entry = f"Not stated in the document: {label}"
        if entry not in result.unknowns:
            result.unknowns.append(entry)
    return result


def generate_risks(
    document_text: str, extraction: ExtractionResult, classification: ClassificationResult, use_demo: bool = False
) -> StageResult[RiskResult]:
    gaps = detect_gaps(document_text, extraction.overview)
    gap_text = "\n".join(f"- {label}" for _, label in gaps) or "- No standard gaps detected."
    prompt = (
        load_prompt("risk_prompt.txt")
        .replace("{classification_json}", classification.model_dump_json())
        .replace("{detected_gaps}", gap_text)
        .replace("{requirements_json}", extraction.model_dump_json())
    )
    stage = run_stage(
        prompt=prompt, model_cls=RiskResult, demo_factory=demo_risks,
        document_text=document_text, use_demo=use_demo, system=SYSTEM_PROMPT,
    )
    valid_ids = {r.requirement_id for r in extraction.requirements}
    stage.data = postprocess_risks(stage.data, valid_ids, gaps)
    return stage