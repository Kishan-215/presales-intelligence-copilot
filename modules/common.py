"""Shared helpers used by every AI stage module."""
from dataclasses import dataclass
from typing import Callable, Generic, Optional, Type, TypeVar

from pydantic import BaseModel

import config
import llm_client
from modules import demo_data

T = TypeVar("T", bound=BaseModel)

DEMO_NOTICE = "DEMO MODE: this output comes from built-in sample data, not from a live AI model."


class DemoUnavailableError(Exception):
    """Demo data exists only for the built-in sample RFP."""


@dataclass
class StageResult(Generic[T]):
    data: T
    mode: str  # "AI" or "DEMO"
    notice: str = ""


def load_prompt(filename: str) -> str:
    """Read a prompt template from the prompts folder."""
    path = config.BASE_DIR / "prompts" / filename
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        raise FileNotFoundError(f"Prompt file not found: {path}") from e


def _demo_result(demo_factory: Callable[[], T], document_text: str, notice: str) -> StageResult[T]:
    if not demo_data.is_sample_document(document_text):
        raise DemoUnavailableError(
            "Demo mode only works with the built-in sample RFP (data/sample_rfp.txt). "
            "For other documents a working API key is required."
        )
    return StageResult(data=demo_factory(), mode="DEMO", notice=notice)


def run_stage(
    prompt: str,
    model_cls: Type[T],
    demo_factory: Callable[[], T],
    document_text: str,
    use_demo: bool = False,
    system: Optional[str] = None,
    fallback_to_demo: bool = True,
) -> StageResult[T]:
    """Run one AI stage. Never silently returns demo data: the result always says which mode it used."""
    if use_demo:
        return _demo_result(demo_factory, document_text, DEMO_NOTICE)
    try:
        data = llm_client.generate_json(prompt, model_cls, system=system)
        return StageResult(data=data, mode="AI")
    except llm_client.LLMError as e:
        if not fallback_to_demo or not demo_data.is_sample_document(document_text):
            raise
        return _demo_result(
            demo_factory,
            document_text,
            f"The AI service was unavailable ({str(e)[:200]}). {DEMO_NOTICE}",
        )