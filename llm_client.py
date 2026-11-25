"""All LLM calls go through this file: retries, fallbacks, JSON validation."""
import json
import re
import time
from typing import Optional, Type, TypeVar

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

import config

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """Base class for all LLM problems."""


class LLMUnavailableError(LLMError):
    """No key, or every model/retry failed. The app can fall back to demo mode."""


class LLMOutputError(LLMError):
    """The model answered but the output was empty or not valid for our schema."""


_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if not config.has_api_key():
        raise LLMUnavailableError("No API key configured. Add GEMINI_API_KEY to your .env file.")
    if _client is None:
        _client = genai.Client(
            api_key=config.GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=config.LLM_TIMEOUT_SECONDS * 1000),  # milliseconds
        )
    return _client


def generate_text(
    prompt: str,
    system: Optional[str] = None,
    json_mode: bool = False,
    temperature: float = 0.2,
    retries_per_model: int = 2,
) -> str:
    """Call the LLM. Retries temporary errors, then tries the next fallback model."""
    client = _get_client()
    gen_config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        max_output_tokens=config.LLM_MAX_OUTPUT_TOKENS,
        response_mime_type="application/json" if json_mode else None,
    )
    problems = []

    for model in config.LLM_MODELS:
        for attempt in range(1, retries_per_model + 1):
            try:
                response = client.models.generate_content(model=model, contents=prompt, config=gen_config)
                if not response.text:
                    raise LLMOutputError("The model returned an empty response (it may have been blocked).")
                return response.text
            except errors.ServerError as e:  # 5xx: busy/overloaded, worth retrying
                problems.append(f"{model}: server error {e.code}")
                time.sleep(3 * attempt)
            except errors.ClientError as e:
                problems.append(f"{model}: client error {e.code}")
                if e.code == 429:  # rate limit: wait a little, retry
                    time.sleep(5 * attempt)
                elif e.code in (400, 401, 403):  # bad request/key: no model will fix this
                    raise LLMError(f"API rejected the request ({e.code}): {e.message}") from e
                else:  # e.g. 404 model retired: skip to next model
                    break
            except LLMOutputError:
                raise
            except Exception as e:  # network down, timeout, etc.
                problems.append(f"{model}: {type(e).__name__}")
                time.sleep(2 * attempt)

    raise LLMUnavailableError("All models failed. Details: " + "; ".join(problems))


def _parse_json(text: str) -> dict:
    """Parse JSON, tolerating ```json fences the model sometimes adds."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    return json.loads(cleaned)


def generate_json(prompt: str, model_cls: Type[T], system: Optional[str] = None) -> T:
    """Ask for JSON and validate it against a Pydantic model. One repair retry on bad output."""
    last_error = ""
    for attempt in range(2):
        full_prompt = prompt
        if attempt == 1:
            full_prompt += (
                f"\n\nYour previous answer was invalid ({last_error}). "
                "Return ONLY valid JSON that matches the requested structure."
            )
        text = generate_text(full_prompt, system=system, json_mode=True)
        try:
            return model_cls.model_validate(_parse_json(text))
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)[:300]
    raise LLMOutputError(f"The model returned invalid JSON twice. Last problem: {last_error}")