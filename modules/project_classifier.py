"""Stage: classify the project into one or more delivery categories."""
from modules.common import StageResult, load_prompt, run_stage
from modules.demo_data import demo_classification
from schemas import PROJECT_CATEGORIES, ClassificationResult, ExtractionResult

SYSTEM_PROMPT = (
    "You are an experienced solution architect. You classify only with evidence from the requirements. "
    "You answer with valid JSON only."
)


def postprocess_classification(result: ClassificationResult) -> ClassificationResult:
    """Keep each category once (first explanation wins)."""
    seen, unique = set(), []
    for item in result.classifications:
        if item.category not in seen:
            seen.add(item.category)
            unique.append(item)
    result.classifications = unique
    return result


def classify_project(
    document_text: str, extraction: ExtractionResult, use_demo: bool = False
) -> StageResult[ClassificationResult]:
    prompt = (
        load_prompt("classification_prompt.txt")
        .replace("{categories}", "\n".join(f"- {c}" for c in PROJECT_CATEGORIES))
        .replace("{requirements_json}", extraction.model_dump_json())
    )
    stage = run_stage(
        prompt=prompt,
        model_cls=ClassificationResult,
        demo_factory=demo_classification,
        document_text=document_text,
        use_demo=use_demo,
        system=SYSTEM_PROMPT,
    )
    stage.data = postprocess_classification(stage.data)
    return stage