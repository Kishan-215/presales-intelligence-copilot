"""Stage: recommend a cloud architecture (AWS or Azure) and draw it as Mermaid and Graphviz."""
import re
import textwrap
from typing import List, Set, Tuple

from modules.common import StageResult, load_prompt, run_stage
from modules.demo_data import demo_architecture
from schemas import ArchitectureComponent, ArchitectureResult, ClassificationResult, ExtractionResult

SYSTEM_PROMPT = (
    "You are an experienced cloud solution architect. You justify every component with the requirements, "
    "you never give prices, and you answer with valid JSON only."
)
PROVIDERS = ("AWS", "Azure")


def _kind(layer: str) -> str:
    low = layer.lower()
    if "front" in low:
        return "frontend"
    if "backend" in low or "application" in low:
        return "backend"
    if "api" in low:
        return "api"
    if "database" in low or "storage" in low or "file" in low:
        return "data"
    if "auth" in low or "identity" in low:
        return "auth"
    if re.search(r"\bai\b|\bml\b|ai/ml", low):
        return "ai"
    if "integration" in low:
        return "integration"
    return "ops"  # security, logging, monitoring, deployment, resilience...


def _structure(components: List[ArchitectureComponent]):
    """Layout shared by both diagram formats: node ids, kinds and edges (from, to, dashed)."""
    kinds = [_kind(c.layer) for c in components]
    ids = [f"N{i}" for i in range(len(components))]

    def first(kind: str):
        return next((ids[i] for i in range(len(ids)) if kinds[i] == kind), None)

    frontend, api, backend = first("frontend"), first("api"), first("backend")
    hub = backend or api or frontend or (ids[0] if ids else None)
    edges: List[Tuple[str, str, bool]] = []
    if hub is None:
        return ids, kinds, edges
    edges.append(("U", frontend or hub, False))
    if frontend and api:
        edges.append((frontend, api, False))
        if backend:
            edges.append((api, backend, False))
    elif frontend and backend:
        edges.append((frontend, backend, False))
    for i, nid in enumerate(ids):
        if nid == hub or nid in (frontend, api, backend):
            continue
        edges.append((hub, nid, kinds[i] == "ops"))  # supporting services get dashed arrows
    return ids, kinds, edges


def _mm(text: str) -> str:
    """Make text safe inside a double-quoted Mermaid label (parentheses are fine in quotes)."""
    return re.sub(r"[<>`]", "", text).replace('"', "'").replace("&", "and").strip()


def build_mermaid(components: List[ArchitectureComponent]) -> str:
    """Draw the architecture from the validated components (always valid Mermaid)."""
    if not components:
        return 'flowchart LR\n    U["No components"]'
    ids, _, edges = _structure(components)
    lines = ["flowchart LR", '    U(["Hospital staff - web browser"])']
    optional = []
    for nid, comp in zip(ids, components):
        lines.append(f'    {nid}["{_mm(comp.component_name)}<br/>{_mm(comp.suggested_service)}"]')
        if comp.status == "Optional":
            optional.append(nid)
    for src, dst, dashed in edges:
        lines.append(f"    {src} {'-.->' if dashed else '-->'} {dst}")
    if optional:
        lines.append("    classDef optional stroke-dasharray: 5 5")
        lines.append(f"    class {','.join(optional)} optional")
    return "\n".join(lines)


def _dot_text(text: str, width: int = 30) -> str:
    clean = text.replace('"', "'").replace("\\", "/")
    return "\\n".join(textwrap.wrap(clean, width=width)) or "-"


def build_dot(components: List[ArchitectureComponent]) -> str:
    """Same diagram as Graphviz DOT. Streamlit renders it without any external library."""
    if not components:
        return 'digraph G { U [label="No components"]; }'
    ids, _, edges = _structure(components)
    lines = [
        "digraph G {",
        '  bgcolor="white"; pad=0.3; rankdir=LR;',
        '  node [shape=box, style="rounded,filled", fillcolor="#eaf1fb", color="#555555", fontname="Helvetica", fontsize=10];',
        '  edge [color="#555555"];',
        '  U [label="Hospital staff\\nweb browser", shape=oval, fillcolor="#ffffff"];',
    ]
    for nid, comp in zip(ids, components):
        style = "rounded,filled,dashed" if comp.status == "Optional" else "rounded,filled"
        label = f"{_dot_text(comp.component_name)}\\n{_dot_text(comp.suggested_service)}"
        lines.append(f'  {nid} [label="{label}", style="{style}"];')
    for src, dst, dashed in edges:
        lines.append(f"  {src} -> {dst}" + (" [style=dashed];" if dashed else ";"))
    lines.append("}")
    return "\n".join(lines)


def postprocess_architecture(result: ArchitectureResult, valid_ids: Set[str], provider: str) -> ArchitectureResult:
    """Drop invented requirement IDs, check the provider label, and draw the diagram."""
    for comp in result.components:
        comp.requirement_ids = [r for r in comp.requirement_ids if r in valid_ids]
    if result.cloud_provider != provider:
        result.assumptions.append(
            f"The model labelled this design '{result.cloud_provider}' although {provider} was requested. Verify the service names."
        )
        result.cloud_provider = provider
    if result.components and all(c.status == "Recommended" for c in result.components):
        note = (
            "All components were marked Recommended by the model. The architect should decide which of them "
            "are optional (for example an API gateway or extra resilience)."
        )
        if note not in result.assumptions:
            result.assumptions.append(note)
    result.mermaid_diagram = build_mermaid(result.components)
    return result


def generate_architecture(
    document_text: str,
    extraction: ExtractionResult,
    classification: ClassificationResult,
    provider: str,
    use_demo: bool = False,
) -> StageResult[ArchitectureResult]:
    if provider not in PROVIDERS:
        raise ValueError(f"Provider must be one of {PROVIDERS}")
    prompt = (
        load_prompt("architecture_prompt.txt")
        .replace("{cloud_provider}", provider)
        .replace("{classification_json}", classification.model_dump_json())
        .replace("{requirements_json}", extraction.model_dump_json())
    )
    stage = run_stage(
        prompt=prompt,
        model_cls=ArchitectureResult,
        demo_factory=lambda: demo_architecture(provider),
        document_text=document_text,
        use_demo=use_demo,
        system=SYSTEM_PROMPT,
    )
    valid_ids = {r.requirement_id for r in extraction.requirements}
    stage.data = postprocess_architecture(stage.data, valid_ids, provider)
    return stage