import re

from modules import demo_data
from modules.document_parser import parse_uploaded_file
from modules.requirement_extractor import postprocess_extraction
from schemas import ExtractionResult, Requirement

SAMPLE_TEXT = demo_data.SAMPLE_RFP_PATH.read_text(encoding="utf-8")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def test_sample_rfp_is_recognised_and_parses():
    assert demo_data.is_sample_document(SAMPLE_TEXT)
    parsed = parse_uploaded_file("sample_rfp.txt", SAMPLE_TEXT.encode("utf-8"))
    assert parsed.char_count > 1000


def test_other_text_is_not_treated_as_sample():
    assert not demo_data.is_sample_document("Some other customer wants a mobile app for deliveries.")


def test_demo_extraction_is_valid_and_grounded_in_the_sample_rfp():
    result = demo_data.demo_extraction()
    assert len(result.requirements) >= 15
    doc = _normalize(SAMPLE_TEXT)
    for req in result.requirements:
        assert _normalize(req.source_excerpt) in doc, f"{req.requirement_id} excerpt not found in RFP"


def test_demo_budget_is_not_specified():
    assert demo_data.demo_extraction().overview.budget_information == "Not specified"


def test_schema_normalises_priority_and_clamps_confidence():
    req = Requirement.model_validate(
        {"requirement_id": "REQ-001", "description": "x", "category": "Functional", "priority": "high", "confidence": 7}
    )
    assert req.priority == "High"
    assert req.confidence == 1.0


def test_schema_fills_defaults_for_missing_fields():
    result = ExtractionResult.model_validate({"overview": {}, "requirements": []})
    assert result.overview.project_name == "Not specified"
    assert result.overview.business_objectives == []


def test_duplicate_ids_are_renumbered():
    reqs = [
        {"requirement_id": "REQ-001", "description": "a", "category": "Functional"},
        {"requirement_id": "REQ-001", "description": "b", "category": "Functional"},
    ]
    result = postprocess_extraction(ExtractionResult.model_validate({"overview": {}, "requirements": reqs}), SAMPLE_TEXT)
    assert [r.requirement_id for r in result.requirements] == ["REQ-001", "REQ-002"]


def test_fabricated_excerpt_is_flagged():
    reqs = [{
        "requirement_id": "REQ-001", "description": "Support blockchain payments", "category": "Functional",
        "source_excerpt": "The system must support blockchain payments.", "confidence": 0.95,
    }]
    result = postprocess_extraction(ExtractionResult.model_validate({"overview": {}, "requirements": reqs}), SAMPLE_TEXT)
    assert result.requirements[0].confidence <= 0.4
    assert "verify manually" in result.requirements[0].notes