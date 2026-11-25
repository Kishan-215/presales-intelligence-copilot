import itertools
import re

import pytest

from modules.architecture_generator import build_mermaid, postprocess_architecture
from modules.common import DemoUnavailableError
from modules.demo_data import demo_architecture, demo_classification, demo_effort_inputs, demo_extraction
from modules.effort_estimator import calculate_estimate, suggest_effort_inputs
from schemas import EffortInputs


def inputs(**overrides) -> EffortInputs:
    base = dict(size="Medium", integration_count=0, security_level="Standard",
                requirement_clarity="Clear", ai_complexity="None", has_mobile_app=False)
    base.update(overrides)
    return EffortInputs(**base)


def assert_consistent(est):
    assert est.total_min == sum(p.min_days for p in est.phases)
    assert est.total_max == sum(p.max_days for p in est.phases)
    assert all(1 <= p.min_days <= p.max_days for p in est.phases)
    assert est.overall_min == est.total_min + est.contingency_min
    assert est.overall_max == est.total_max + est.contingency_max
    assert est.overall_min <= est.overall_max
    assert 10 <= est.contingency_percent <= 30
    assert est.disclaimers


def test_hand_calculated_baseline_case():
    est = calculate_estimate(inputs())
    assert (est.total_min, est.total_max) == (113, 177)
    assert est.contingency_percent == 10
    assert (est.overall_min, est.overall_max) == (124, 195)


def test_totals_are_consistent_for_every_input_combination():
    for size, clarity, ai, integ, sec in itertools.product(
        ["Small", "Medium", "Large"], ["Clear", "Partial", "Unclear"],
        ["None", "Low", "Medium", "High"], [0, 3], ["Standard", "High"],
    ):
        est = calculate_estimate(inputs(size=size, requirement_clarity=clarity, ai_complexity=ai,
                                        integration_count=integ, security_level=sec))
        assert_consistent(est)


def test_calculation_is_deterministic():
    a = calculate_estimate(inputs(size="Large", ai_complexity="High", integration_count=2))
    b = calculate_estimate(inputs(size="Large", ai_complexity="High", integration_count=2))
    assert a.model_dump() == b.model_dump()


def test_bigger_projects_cost_more():
    small = calculate_estimate(inputs(size="Small")).total_max
    medium = calculate_estimate(inputs(size="Medium")).total_max
    large = calculate_estimate(inputs(size="Large")).total_max
    assert small < medium < large


def test_more_integrations_increase_effort():
    assert calculate_estimate(inputs(integration_count=3)).total_min > calculate_estimate(inputs(integration_count=0)).total_min


def test_high_security_increases_effort():
    assert calculate_estimate(inputs(security_level="High")).total_max > calculate_estimate(inputs()).total_max


def test_unclear_requirements_widen_the_range_and_raise_contingency():
    clear = calculate_estimate(inputs(requirement_clarity="Clear"))
    unclear = calculate_estimate(inputs(requirement_clarity="Unclear"))
    assert (unclear.total_max - unclear.total_min) > (clear.total_max - clear.total_min)
    assert unclear.contingency_percent > clear.contingency_percent


def test_ai_phase_only_exists_when_ai_is_needed():
    assert "AI/ML implementation" not in [p.phase for p in calculate_estimate(inputs()).phases]
    assert "AI/ML implementation" in [p.phase for p in calculate_estimate(inputs(ai_complexity="Medium")).phases]


def test_contingency_is_capped():
    est = calculate_estimate(inputs(requirement_clarity="Unclear", ai_complexity="High", integration_count=15))
    assert est.contingency_percent == 30


def test_every_phase_lists_role_tasks_and_dependencies():
    for p in calculate_estimate(inputs(ai_complexity="Low")).phases:
        assert p.role and p.tasks and p.dependencies


def test_demo_effort_inputs_produce_a_valid_estimate():
    est = calculate_estimate(demo_effort_inputs())
    assert_consistent(est)
    assert est.overall_min > 0


def test_demo_effort_refuses_other_documents():
    other = "A retailer wants a mobile app for delivery tracking with live maps and push notifications."
    with pytest.raises(DemoUnavailableError):
        suggest_effort_inputs(other, demo_extraction(), demo_classification(), use_demo=True)


@pytest.mark.parametrize("provider", ["AWS", "Azure"])
def test_demo_architecture_is_valid_for_both_providers(provider):
    arch = demo_architecture(provider)
    ids = {r.requirement_id for r in demo_extraction().requirements}
    assert arch.cloud_provider == provider
    assert len(arch.components) >= 10
    assert {"Recommended", "Optional"} <= {c.status for c in arch.components}
    assert arch.assumptions and arch.trade_offs and arch.security_considerations
    for c in arch.components:
        assert c.reason and c.suggested_service
        assert set(c.requirement_ids) <= ids


def test_aws_and_azure_designs_use_different_services():
    aws = {c.suggested_service for c in demo_architecture("AWS").components}
    azure = {c.suggested_service for c in demo_architecture("Azure").components}
    assert not (aws & azure)


def test_postprocess_removes_invented_requirement_ids_and_draws_diagram():
    arch = demo_architecture("AWS")
    arch.components[0].requirement_ids = ["REQ-999", "REQ-001"]
    cleaned = postprocess_architecture(arch, {"REQ-001"}, "AWS")
    assert cleaned.components[0].requirement_ids == ["REQ-001"]
    assert cleaned.mermaid_diagram.startswith("flowchart")


def test_mermaid_has_one_node_per_component_and_marks_optional_ones():
    components = demo_architecture("Azure").components
    diagram = build_mermaid(components)
    assert len(re.findall(r"^\s+N\d+\[", diagram, flags=re.MULTILINE)) == len(components)
    assert "classDef optional" in diagram