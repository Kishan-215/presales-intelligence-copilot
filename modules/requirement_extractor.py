"""Stage: extract structured requirements from the customer document."""
import re

from modules.common import StageResult, load_prompt, run_stage
from modules.demo_data import demo_extraction
from schemas import NOT_SPECIFIED, ExtractionResult

SYSTEM_PROMPT = (
    "You are a careful presales analyst. You only report what the document states. "
    "You never invent requirements. You answer with valid JSON only."
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def postprocess_extraction(result: ExtractionResult, document_text: str) -> ExtractionResult:
    """Deterministic clean-up: unique IDs, and flag excerpts that are not found in the document."""
    ids = [r.requirement_id.strip() for r in result.requirements]
    if len(set(ids)) != len(ids) or any(not i for i in ids):
        for n, req in enumerate(result.requirements, start=1):
            req.requirement_id = f"REQ-{n:03d}"

    doc_norm = _normalize(document_text)
    for req in result.requirements:
        excerpt = req.source_excerpt.strip()
        if excerpt and excerpt != NOT_SPECIFIED and _normalize(excerpt) not in doc_norm:
            req.confidence = min(req.confidence, 0.4)
            flag = "Source excerpt not found word-for-word in the document - verify manually."
            req.notes = f"{req.notes} {flag}".strip()
    return result


def extract_requirements(document_text: str, use_demo: bool = False) -> StageResult[ExtractionResult]:
    """Main entry point used by the app."""
    prompt = load_prompt("requirement_prompt.txt").replace("{document_text}", document_text)
    stage = run_stage(
        prompt=prompt,
        model_cls=ExtractionResult,
        demo_factory=demo_extraction,
        document_text=document_text,
        use_demo=use_demo,
        system=SYSTEM_PROMPT,
    )
    stage.data = postprocess_extraction(stage.data, document_text)
    return stage