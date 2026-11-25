# Cynbit Presales Copilot

An AI-powered requirements analysis, cloud architecture recommendation, effort estimation and technical roadmap generation assistant. It turns a customer document (RFP, brief, email or notes) into a structured **draft** for a human solution architect.

> **Important.** Output is an AI-generated draft that must be reviewed by a qualified architect. Estimates are preliminary, assumption-based and not calibrated against any company's delivery history. This is not a quotation. The included sample RFP is **synthetic demonstration data**, not a real customer document.

This is an internship assessment proof of concept. See `reports/` for the AI Opportunity Report, the Technical Approach Report and the evaluation results.

## What it does

Customer document, then requirements extraction, clarification questions, project classification, risks and assumptions, effort estimate, AWS or Azure architecture with diagram, technical roadmap, and a 16-section proposal draft (Markdown download).

Key design points:

- The AI reads and drafts. **Plain Python does the effort arithmetic.**
- Every model output is validated against a schema. Bad output never crashes the app.
- Every requirement carries its source excerpt. Quotes that cannot be found in the document are flagged.
- A clearly labeled **demo mode** works without an API key, **for the built-in sample RFP only**.

## Requirements

- Windows with PowerShell (other systems should work, but commands below are for Windows)
- Python 3.11 or newer (developed on 3.14.6)
- A Gemini API key from Google AI Studio (free tier is enough). Optional: demo mode needs no key.

## Setup

```powershell
cd cynbit-presales-copilot
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, run once: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

Open `.env` in an editor and set your key. **Never put the key in code or commit `.env`.**

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
LLM_MODEL=gemini-3.5-flash
LLM_FALLBACK_MODELS=gemini-3.6-flash,gemini-3.5-flash-lite
LLM_TIMEOUT_SECONDS=60
MAX_UPLOAD_MB=10
```

Model names change over time. If you see a "model not found" error, pick a current Flash model in Google AI Studio and update `LLM_MODEL`.

## Run the app

```powershell
streamlit run app.py
```

Then open http://localhost:8501.

1. **Upload Requirements** > "Use the built-in sample RFP" > **Load sample RFP**.
2. Tick **Demo mode** to run without an AI call, or leave it off to use the live model (a full analysis takes about four minutes on the free tier).
3. Click **Run analysis**.
4. Visit **Requirement Analysis**, **Architecture Recommendation**, **Effort Estimation**, **Technical Roadmap** and **Proposal Generator**.
5. Download the proposal as Markdown.

Notes:

- Refreshing the browser clears the results (they are kept in memory only).
- If a run stops because of a rate limit or overload, click **Continue (keep finished stages)**.
- The Architecture diagram has a Mermaid view (needs internet access for the Mermaid library) and a Graphviz backup view that always renders.

## Run the tests

```powershell
python -m pytest tests -v
```

Expected: 73 tests pass (about one second). These tests need no API key.

## Run the evaluation

```powershell
python run_evaluation.py            # unit tests + 15 reliability tests, no API calls
python run_evaluation.py --ai 3     # also 3 real AI runs and a prompt-injection test
```

Results are written to `reports/evaluation_results.md`, and a scoring sheet for the human architecture review to `reports/architecture_review_template.csv`. If the prompt-injection test reports "not run" because the AI service was busy, wait a few minutes and run only that test:

```powershell
python -c "import run_evaluation as r; print(r.run_injection_test())"
```

## Project structure

```
app.py                    page routing
config.py                 settings from .env
schemas.py                data shapes for every stage
llm_client.py             model calls: retries, fallbacks, JSON validation
modules/                  one module per stage + parser, pipeline, proposal
prompts/                  one prompt file per AI stage
views/                    Streamlit pages
data/sample_rfp.txt       synthetic healthcare RFP (demo data)
reports/                  reports and evaluation results
tests/                    73 tests
run_evaluation.py         evaluation harness
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `404 NOT_FOUND ... model ... no longer available` | Update `LLM_MODEL` in `.env` to a current model |
| `503 UNAVAILABLE ... high demand` | Temporary. Wait, or rely on the fallback models and use **Continue** |
| `429` or quota errors | Free-tier limit. Wait a minute and use **Continue** |
| Settings seem ignored | A terminal variable such as `LLM_MODEL` may override `.env` (the project loads `.env` with priority, but check `$env:LLM_MODEL`) |
| `ModuleNotFoundError` | The virtual environment is not active. Run `.\venv\Scripts\Activate.ps1` |
| Mermaid diagram blank | Check internet access, or use the Graphviz view or paste the Mermaid source into https://mermaid.live |
| "No readable text" for a PDF | The PDF is a scan. OCR is not supported. Use a text PDF or paste the text |

## Limitations

Tested on one synthetic document. Effort rules are generic assumptions. No OCR, RAG, DOCX export, accounts or saved history. Documents are sent to an external model API, so use only non-confidential documents unless the provider's terms have been approved. See section 18 of the Technical Approach Report.

## Security

- `.env` is excluded by `.gitignore`. Only `.env.example` (placeholders) belongs in version control.
- Results live in memory only. Nothing is saved unless you click "Save copy to outputs folder".
