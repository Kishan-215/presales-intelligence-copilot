# Demo Script, Presentation Outline and Q&A Preparation

## Before the demo (5 minutes)

- Activate the environment and start the app: `streamlit run app.py`. Open http://localhost:8501.
- **Do not refresh the browser** during the demo, because results live in memory.
- Decide the mode in advance:
  - **Safe path (recommended for a live demo): Demo mode.** Fast, no AI call, clearly labeled.
  - **Live path:** untick Demo mode. A full analysis takes about four minutes on the free tier, so start it first and talk while it runs, or have screenshots ready.
- Have these open in tabs: the app, `data/sample_rfp.txt`, `reports/evaluation_results.md`.
- Optional but strong: run the live analysis once before the meeting so that you can say "this is a real model run" and keep the screen results ready.

## 5-minute demo script

**0:00 Problem (30 seconds)**
"Presales engineers turn messy customer documents into technical proposals by hand. It is repetitive, inconsistent, and gaps get missed. I built a copilot that produces a structured first draft for the architect to review. It never replaces the architect."

**0:30 Upload (30 seconds)**
Open **Upload Requirements**, choose the built-in sample, click **Load sample RFP**. Point at the file card and preview.
"This is a synthetic healthcare RFP, labeled as demonstration data. I deliberately left out user numbers, the cloud provider, retention, recovery targets, API specifications and budget, to see whether the tool notices."

**1:00 Run analysis (30 seconds)**
Tick Demo mode (or untick for live) and click **Run analysis**. Show the seven progress steps.
"Seven stages run in sequence. If one fails, finished stages are kept and I can continue. Demo mode is always labeled and only works for this sample."

**1:30 Requirement Analysis (60 seconds)**
Open **Requirement Analysis**.
- Requirements tab: filter by priority, select a requirement and show the **source excerpt**.
"Every requirement points to the sentence it came from. If the model quotes something that is not in the document, it is flagged and its confidence is capped."
- Clarification tab: show the questions and the **rule-based gap check** expander.
"Python finds the gaps first, then the model writes specific questions about them."
- Risks tab: show confirmed facts, assumptions and unknowns side by side.

**2:30 Architecture (45 seconds)**
Open **Architecture Recommendation**, generate AWS (and Azure if time allows). Show the component table (Recommended vs Optional), then the diagram.
"Every component has a reason and linked requirements. The diagram is drawn by code from the validated components, so it cannot contain broken syntax. No cost figures, because costs need workload data."

**3:15 Effort (60 seconds)**
Open **Effort Estimation**. Show the range, contingency and phase table. Open the what-if panel and change "Requirement clarity" to Unclear.
"The model only picks labels such as size and security level. All the arithmetic is plain Python, so the same inputs always give the same answer. Watch the range widen and the contingency rise when requirements are unclear. It is labeled preliminary and uncalibrated."

**4:15 Roadmap and proposal (30 seconds)**
Show **Technical Roadmap** (six phases, week ranges, no dates), then **Proposal Generator** and click **Download proposal**.
"Sixteen sections, assembled by code from the validated results, ending with a human review notice."

**4:45 Evidence (15 seconds)**
"71 unit tests, 15 reliability tests, and a measured evaluation. In three real runs the extraction matched between 79% and 100% of my reference list, and I report that variation rather than hide it."

## Presentation outline (8 slides)

1. **Title and problem.** Presales is manual, inconsistent and gaps get missed.
2. **Opportunity.** An AI-assisted first draft with human review (link to the AI Opportunity Report; mark public facts versus assumptions).
3. **Solution overview.** Workflow diagram: document, extract, clarify, classify, risks, estimate, architecture, roadmap, proposal.
4. **How it stays trustworthy.** Schema validation, source excerpts, deterministic estimates, guardrails, labeled demo mode, human review.
5. **Live demo.** (Use the script above.)
6. **Evaluation.** Table of measured results and what they do and do not show (section 16 of the Technical Approach Report).
7. **Limitations and lessons.** Variation between runs, uncalibrated estimates, keyword-based metrics, retired model and overload errors during development, architecture marked everything Recommended.
8. **Next steps.** RAG over Cynbit's proposals, calibration with delivery data, OCR, DOCX, accounts, larger evaluation.

## Likely questions and honest answers

**Why does the model not calculate the effort?**
Language models are unreliable at consistent arithmetic and the estimate must be explainable. The model chooses six labels, then fixed rules compute person-days. A test checks a hand-calculated case (113 to 177 days, 10% contingency, 124 to 195).

**How do you stop hallucinations?**
Required source excerpts, a check that each excerpt exists in the document (flagged and confidence capped otherwise), "Not specified" for anything missing, strict schemas, removal of invented requirement IDs, and human review. This reduces the risk. It does not remove it.

**How accurate is it?**
On my one synthetic document, recall was 100%, 79% and 79% in three runs, precision 90% to 100%. That is a small demonstration, not a statistical claim. Runs 2 and 3 missed the same four constraint and timeline items, and my metric only looks at the requirements list, so it may understate the result.

**Is the estimate reliable?**
No claim is made. It is a preliminary, assumption-based range, not calibrated to any company's history. The next step would be to calibrate with real delivery data.

**What happens if the AI is down?**
Retries, fallback models, then a clear error. For the sample RFP only, a clearly labeled demo fallback. For any other document it refuses to show demo data.

**Why no RAG or agents?**
A fixed sequence of stages is easier to test and explain, and there is no knowledge base yet. RAG becomes worthwhile once Cynbit's past proposals are available.

**What would you change first?**
Calibrate estimates with real data, evaluate on real anonymised enquiries with several reviewers, and make the architecture stage mark optional components properly (in my evaluation all 12 components were Recommended).

**What did you learn that surprised you?**
Models and APIs change under you. The first model name I chose was retired for new users, another was overloaded, and my first date check flagged "DPDP Act 2023" as a calendar date. Each of these led to a specific fix and a test.

**Is customer data safe?**
Documents are sent to an external model API. I did not review the free tier's data terms, so I would not use confidential documents with it. A real deployment would need an approved provider or a private model.

**Did you use Cynbit's internal data?**
No. The sample RFP is synthetic and Cynbit's internal processes are not public, so the Opportunity Report labels those parts as assumptions.
