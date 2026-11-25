"""Runs the full analysis chain, stage by stage. Finished stages are kept if a later stage fails."""
from typing import Callable, Dict, Optional

from modules.architecture_generator import generate_architecture
from modules.clarification_generator import generate_clarifications
from modules.effort_estimator import calculate_estimate, suggest_effort_inputs
from modules.project_classifier import classify_project
from modules.requirement_extractor import extract_requirements
from modules.risk_analyzer import generate_risks
from modules.roadmap_generator import generate_roadmap

FULL_KEYS = (
    "extraction", "clarification", "classification", "risks",
    "effort_inputs", "estimate", "architecture", "roadmap",
)


def run_full_analysis(
    document_text: str,
    use_demo: bool = False,
    provider: str = "AWS",
    on_step: Optional[Callable[[str], None]] = None,
    results: Optional[Dict] = None,
) -> Dict:
    """Fill `results` stage by stage. Stages that already have a value are skipped (resume)."""
    results = results if results is not None else {}

    def note(message: str) -> None:
        if on_step:
            on_step(message)

    def todo(key: str) -> bool:
        return results.get(key) is None

    if todo("extraction"):
        note("1/7 Extracting requirements...")
        results["extraction"] = extract_requirements(document_text, use_demo=use_demo)
    extraction = results["extraction"].data

    if todo("clarification"):
        note("2/7 Generating clarification questions...")
        results["clarification"] = generate_clarifications(document_text, extraction, use_demo=use_demo)

    if todo("classification"):
        note("3/7 Classifying the project...")
        results["classification"] = classify_project(document_text, extraction, use_demo=use_demo)
    classification = results["classification"].data

    if todo("risks"):
        note("4/7 Identifying risks and assumptions...")
        results["risks"] = generate_risks(document_text, extraction, classification, use_demo=use_demo)

    if todo("effort_inputs"):
        note("5/7 Choosing estimate inputs...")
        results["effort_inputs"] = suggest_effort_inputs(document_text, extraction, classification, use_demo=use_demo)
    if todo("estimate"):
        results["estimate"] = calculate_estimate(results["effort_inputs"].data)  # plain Python, no LLM

    if todo("architecture"):
        note(f"6/7 Recommending a {provider} architecture...")
        results["architecture"] = generate_architecture(
            document_text, extraction, classification, provider, use_demo=use_demo
        )

    if todo("roadmap"):
        note("7/7 Building the technical roadmap...")
        results["roadmap"] = generate_roadmap(
            document_text, extraction, classification, results["estimate"], use_demo=use_demo
        )
    return results