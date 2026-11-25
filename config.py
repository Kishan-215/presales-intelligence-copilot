"""Central configuration. Every other file imports settings from here."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)  # .env values win over leftover terminal variables

APP_NAME = "Cynbit Presales Copilot"
APP_SUBTITLE = "AI-powered requirements analysis, architecture, estimation and roadmap drafts"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite").strip().replace("models/", "")
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
LLM_MAX_OUTPUT_TOKENS = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "8192"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "60000"))  # long-document limit

# Models tried in order: main model first, then fallbacks (comma-separated in .env)
_fallbacks = [
    m.strip().replace("models/", "")
    for m in os.getenv("LLM_FALLBACK_MODELS", "").split(",")
    if m.strip()
]
LLM_MODELS = [LLM_MODEL] + [m for m in _fallbacks if m != LLM_MODEL]


def has_api_key() -> bool:
    """True only if a real-looking key is configured (not the placeholder)."""
    return bool(GEMINI_API_KEY) and not GEMINI_API_KEY.startswith("your_")