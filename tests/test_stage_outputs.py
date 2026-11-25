import pytest
from pydantic import ValidationError

from modules import demo_data
from modules.clarification_generator import detect_gaps, generate_clarifications, postprocess_questions
from modules.common import DemoUnavailableError
from modules.demo_data import demo_classification, demo_clarifications, demo_extraction
from modules.project_classifier import classify_project, postprocess_classification
from schemas import PROJECT_CATEGORIES, ClarificationResult, ClassificationResult

SAMPLE_TEXT = demo_data.SAMPLE_RFP_PATH.read_text(encoding="utf-8")


def test_sample_rfp_gaps_match_the_intentionally_missing_information():
    keys = {key for key, _ in detect_gaps(SAMPLE_TEXT, demo_extraction().overview)}
    expected = {
        "concurrent_users", "cloud_provider", "existing_database", "data_retention",
        "recovery_objectives", "authentication_method", "data_residency", "integration_specs", "budget",
    }
    assert expected <= keys


def test_gap_is_not_reported_when_document_covers_it():
    text = SAMPLE_TEXT + "\nThe solution will be hosted on AWS and must support 200 concurrent users."
    keys = {key for key, _ in detect_gaps(text, demo_extraction().overview)}
    assert "cloud_provider" not in keys
    assert "concurrent_users" not in keys


def test_demo_clarifications_are_between_5_and_10_and_grounded():
    result = demo_clarifications()
    ids = {r.requirement_id for r in demo_extraction().requirements}
    assert 5 <= len(result.questions) <= 10
    for q in result.questions:
        assert q.reason
        assert set(q.related_requirement_ids) <= ids


def test_questions_are_deduplicated_and_capped_at_10():
    base = {"question": "What is the budget?", "reason": "r", "priority": "Low"}
    many = [{"question": f"Unique question number {i}?", "reason": "r", "priority": "Medium"} for i in range(14)]
    result = ClarificationResult.model_validate({"questions": [base, dict(base)] + many})
    cleaned = postprocess_questions(result)
    assert len(cleaned.questions) == 10
    assert sum(q.question == "What is the budget?" for q in cleaned.questions) <= 1


def test_questions_are_sorted_high_priority_first():
    qs = [
        {"question": "Low one?", "reason": "r", "priority": "Low"},
        {"question": "High one?", "reason": "r", "priority": "High"},
    ]
    cleaned = postprocess_questions(ClarificationResult.model_validate({"questions": qs}))
    assert cleaned.questions[0].priority == "High"


def test_demo_classification_uses_only_allowed_categories():
    result = demo_classification()
    assert result.classifications
    for item in result.classifications:
        assert item.category in PROJECT_CATEGORIES
        assert item.reasoning


def test_invalid_category_from_model_is_rejected():
    with pytest.raises(ValidationError):
        ClassificationResult.model_validate(
            {"classifications": [{"category": "Quantum computing", "reasoning": "x"}]}
        )


def test_duplicate_categories_are_merged():
    result = ClassificationResult.model_validate({"classifications": [
        {"category": "API development", "reasoning": "first"},
        {"category": "API development", "reasoning": "second"},
    ]})
    cleaned = postprocess_classification(result)
    assert len(cleaned.classifications) == 1
    assert cleaned.classifications[0].reasoning == "first"


def test_demo_mode_refuses_documents_other_than_the_sample():
    other = "A retailer wants a mobile app for delivery tracking with live maps and push notifications."
    with pytest.raises(DemoUnavailableError):
        generate_clarifications(other, demo_extraction(), use_demo=True)
    with pytest.raises(DemoUnavailableError):
        classify_project(other, demo_extraction(), use_demo=True)