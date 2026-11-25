import re

import pytest

from modules.architecture_generator import build_dot, build_mermaid
from modules.demo_data import demo_architecture, demo_classification, demo_effort_inputs, demo_extraction
from modules.effort_estimator import apply_guardrails
from modules.roadmap_generator import DATE_PATTERN
from schemas import EffortInputs


def test_guardrails_correct_underrated_inputs_and_explain_each_change():
    weak = EffortInputs(size="Small", integration_count=0, security_level="Standard",
                        requirement_clarity="Partial", ai_complexity="None", rationale=["model said so"])
    fixed = apply_guardrails(weak, demo_extraction(), demo_classification())
    assert fixed.size == "Medium"
    assert fixed.integration_count == 1
    assert fixed.security_level == "High"
    assert fixed.ai_complexity == "Low"
    assert sum("Rule-based correction" in r for r in fixed.rationale) == 4


def test_guardrails_leave_adequate_inputs_unchanged():
    good = demo_effort_inputs()
    before = good.model_dump()
    after = apply_guardrails(good, demo_extraction(), demo_classification())
    assert after.model_dump() == before


def test_guardrails_never_lower_a_value():
    high = EffortInputs(size="Large", integration_count=3, security_level="High",
                        requirement_clarity="Clear", ai_complexity="High")
    out = apply_guardrails(high, demo_extraction(), demo_classification())
    assert (out.size, out.integration_count, out.security_level, out.ai_complexity) == ("Large", 3, "High", "High")


@pytest.mark.parametrize("text", [
    "The solution must follow the DPDP Act 2023",
    "About 3 to 4 weeks (depends on team size)",
    "Based on 192-354 person-days over 36-39 weeks",
])
def test_bare_years_and_numbers_are_not_flagged_as_dates(text):
    assert not DATE_PATTERN.search(text)


@pytest.mark.parametrize("text", [
    "Starts 1 March 2027", "Go live on Mar 15", "Release by 2027-03-01", "Complete in Q3 2027",
])
def test_real_dates_are_flagged(text):
    assert DATE_PATTERN.search(text)


def test_mermaid_labels_keep_parentheses_and_have_no_stray_quotes():
    diagram = build_mermaid(demo_architecture("AWS").components)
    assert "(Multi-AZ)" in diagram
    for line in diagram.splitlines():
        if re.match(r"^\s+N\d+\[", line):
            assert line.count('"') == 2


def test_dot_graph_has_a_node_per_component_and_marks_optional_ones():
    components = demo_architecture("Azure").components
    dot = build_dot(components)
    assert dot.startswith("digraph")
    assert len(re.findall(r"^\s+N\d+ \[label=", dot, flags=re.MULTILINE)) == len(components)
    assert "dashed" in dot

def test_note_is_added_when_every_component_is_recommended():
    from modules.architecture_generator import postprocess_architecture
    arch = demo_architecture("AWS")
    for c in arch.components:
        c.status = "Recommended"
    ids = {r.requirement_id for r in demo_extraction().requirements}
    out = postprocess_architecture(arch, ids, "AWS")
    assert any("marked Recommended" in a for a in out.assumptions)


def test_no_note_when_optional_components_exist():
    from modules.architecture_generator import postprocess_architecture
    ids = {r.requirement_id for r in demo_extraction().requirements}
    out = postprocess_architecture(demo_architecture("AWS"), ids, "AWS")
    assert not any("marked Recommended" in a for a in out.assumptions)    