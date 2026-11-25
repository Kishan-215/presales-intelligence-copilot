import pytest

import config
from modules import demo_data
from modules.common import DemoUnavailableError, StageResult
from modules.demo_data import demo_extraction, demo_risks, demo_roadmap
from modules.pipeline import FULL_KEYS, run_full_analysis
from modules.proposal_generator import SECTION_TITLES, generate_proposal, summarize_roles
from modules.requirement_extractor import postprocess_extraction
from modules.risk_analyzer import postprocess_risks
from modules.clarification_generator import detect_gaps
from modules.roadmap_generator import DATE_WARNING, missing_phases, postprocess_roadmap
from schemas import RiskResult, RoadmapResult

SAMPLE_TEXT = demo_data.SAMPLE_RFP_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def demo_results():
    return run_full_analysis(SAMPLE_TEXT, use_demo=True)


# ---------- risks ----------
def test_demo_risks_are_valid_and_grounded():
    ids = {r.requirement_id for r in demo_extraction().requirements}
    result = demo_risks()
    assert len(result.risks) >= 6
    for risk in result.risks:
        assert risk.suggested_mitigation and risk.potential_impact
        for token in risk.related_requirement.replace(" ", "").split(","):
            assert token in ids
    assert result.confirmed_facts and result.assumptions


def test_risk_postprocess_sorts_renumbers_cleans_ids_and_adds_unknowns():
    raw = RiskResult.model_validate({"risks": [
        {"risk_id": "X", "description": "low one", "severity": "low", "related_requirement": "REQ-001"},
        {"risk_id": "X", "description": "high one", "severity": "HIGH", "related_requirement": "REQ-001, REQ-999"},
        {"risk_id": "X", "description": "invented", "severity": "Medium", "related_requirement": "REQ-888"},
    ]})
    gaps = detect_gaps(SAMPLE_TEXT, demo_extraction().overview)
    cleaned = postprocess_risks(raw, {"REQ-001"}, gaps)
    assert [r.risk_id for r in cleaned.risks] == ["RISK-001", "RISK-002", "RISK-003"]
    assert cleaned.risks[0].severity == "High"
    assert cleaned.risks[0].related_requirement == "REQ-001"
    assert cleaned.risks[1].related_requirement == "Not specified"
    assert any("budget" in u.lower() for u in cleaned.unknowns)


# ---------- roadmap ----------
def test_demo_roadmap_is_complete():
    roadmap = demo_roadmap()
    assert len(roadmap.phases) == 6
    assert missing_phases(roadmap) == []
    for p in roadmap.phases:
        assert p.activities and p.deliverables and p.completion_criteria and p.estimated_duration


def test_incomplete_roadmap_is_detected():
    short = RoadmapResult.model_validate({"phases": [{"phase_name": "Build everything"}]})
    missing = missing_phases(short)
    assert "Testing and security" in missing and "Deployment and handover" in missing


def test_demo_roadmap_contains_no_calendar_dates():
    cleaned = postprocess_roadmap(demo_roadmap())
    assert DATE_WARNING not in cleaned.notes


def test_calendar_dates_in_roadmap_trigger_a_warning():
    bad = RoadmapResult.model_validate({"phases": [{"phase_name": "Phase 1", "estimated_duration": "Starts 1 March 2027"}]})
    assert DATE_WARNING in postprocess_roadmap(bad).notes


# ---------- full pipeline (demo mode, end to end) ----------
def test_full_pipeline_runs_end_to_end_in_demo_mode(demo_results):
    for key in FULL_KEYS:
        assert demo_results[key] is not None, key
    for key in FULL_KEYS:
        if key != "estimate":
            assert isinstance(demo_results[key], StageResult)
            assert demo_results[key].mode == "DEMO"


def test_pipeline_resume_does_not_redo_finished_stages():
    finished = run_full_analysis(SAMPLE_TEXT, use_demo=True)
    again = run_full_analysis(SAMPLE_TEXT, use_demo=True, results=dict(finished))
    assert again["extraction"] is finished["extraction"]
    assert again["roadmap"] is finished["roadmap"]


def test_pipeline_demo_refuses_other_documents():
    with pytest.raises(DemoUnavailableError):
        run_full_analysis("A retailer wants a mobile app for delivery tracking with live maps.", use_demo=True)


def test_pipeline_reports_progress_steps():
    steps = []
    run_full_analysis(SAMPLE_TEXT, use_demo=True, on_step=steps.append)
    assert len(steps) == 7


# ---------- proposal ----------
def test_proposal_contains_all_sixteen_sections(demo_results):
    md = generate_proposal(demo_results)
    for number, title in enumerate(SECTION_TITLES, start=1):
        assert f"## {number}. {title}" in md


def test_proposal_is_labeled_as_a_draft_and_as_demo_output(demo_results):
    md = generate_proposal(demo_results)
    assert "DRAFT" in md
    assert "DEMO MODE" in md
    assert "not a quotation" in md.lower()
    assert "```mermaid" in md


def test_proposal_numbers_match_the_calculated_estimate(demo_results):
    est = demo_results["estimate"]
    md = generate_proposal(demo_results)
    assert f"{est.overall_min} - {est.overall_max} person-days" in md


def test_proposal_never_contains_the_api_key(demo_results):
    md = generate_proposal(demo_results)
    if config.GEMINI_API_KEY:
        assert config.GEMINI_API_KEY not in md


def test_proposal_still_builds_when_stages_are_missing(demo_results):
    partial = {"extraction": demo_results["extraction"]}
    md = generate_proposal(partial)
    assert "Not generated yet" in md
    for number, title in enumerate(SECTION_TITLES, start=1):
        assert f"## {number}. {title}" in md


def test_role_summary_adds_up_to_the_estimate_totals(demo_results):
    est = demo_results["estimate"]
    rows = summarize_roles(est)
    assert sum(r[2] for r in rows) == est.total_min
    assert sum(r[3] for r in rows) == est.total_max