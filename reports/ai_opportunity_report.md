# AI Opportunity Report: Cynbit Presales Copilot

**Prepared by:** Kishan C
**Date:** 25 November 2026 (research accessed 24 November 2026)
**Status:** Final submission – Proof of Concept assessment. Evaluation figures are in `reports/evaluation_results.md`.

---

## How to read this report

Every statement is labeled so that facts, assumptions and proposals are never mixed.

| Label | Meaning |
|---|---|
| **[Public]** | Stated on a public web page listed in the Sources section. Company claims are marked as claims and were not independently verified. |
| **[Assumption]** | My reasoned guess about how presales work is commonly organised. It needs validation with Cynbit. |
| **[Proposed]** | A design or plan I am proposing. It is not a description of anything Cynbit does today. |
| **[Observed]** | Something I observed while building the proof of concept. |

**What this report does not claim.** I have no access to Cynbit's internal processes, tools, customer data, pricing or delivery history, and I do not describe them. I give no revenue figures, customer numbers or performance improvements for Cynbit. The benefits in section 8 are *expected* benefits, with a way to measure each, and none has been measured at Cynbit.

---

## 1. Company and business context

**[Public]** Cynbit Technologies is a technology company based in Jaipur, Rajasthan, India [S3, S2]. Its website describes work in AI automation, software engineering, and cloud infrastructure [S1, S7]. According to its own story page, the company was officially launched in 2024, alongside its BitElevate and TenantEase initiatives [S3]. A third-party listing shows it as a privately held company with 11 to 50 employees [S6], and the company's own site claims a team of 15+ people and 100+ delivered projects [S5] (company claims, not verified).

**[Public]** It serves clients across India and abroad, and invites prospects to start a project through an enquiry form on its website [S4, S5].

**Why this matters for the opportunity:** a small, multi-skilled engineering studio that sells across AI, software and cloud receives enquiries that need judgement in several domains at once. That makes the step from "customer request" to "scoped technical proposal" a natural place to look for AI help. This is my reasoning from the public profile, not a statement about Cynbit's internal situation.

## 2. Cynbit's relevant service areas

**[Public]** The service areas below come from Cynbit's own pages and the company's GitHub profile.

| Service area | What Cynbit says publicly | Source |
|---|---|---|
| AI automation | Custom AI agents, LLM integrations and automated business workflows; examples listed include lead replies, document extraction, support triage and voice agents | [S4, S5] |
| Software engineering | Web and mobile platforms, SaaS products, APIs, custom software and backends | [S1, S5, S7] |
| Cloud and infrastructure | Deployment across AWS and Azure with zero-trust security; migration to AWS or Azure; modernising legacy systems; Docker, Kubernetes, Terraform and CI/CD in its listed stack | [S2, S5, S7] |
| Technical SEO and growth | Search growth services (not relevant to this project) | [S1] |

**Fit with the Copilot [Proposed]:** the Copilot's ten project categories (web application, mobile, AI/ML, process automation, cloud migration, data engineering, enterprise integration, SaaS, API, legacy modernisation) and its AWS and Azure architecture options were chosen to line up with these public service areas.

## 3. Current presales workflow

**[Public]** The only publicly visible part of Cynbit's sales process is that prospects can describe a project through an enquiry form on the website [S4]. Cynbit's internal presales workflow, tools and templates are not public, and **I do not claim to know them.**

**[Assumption]** In software services firms generally, presales work after an enquiry tends to follow steps like these. This list is a hypothesis to validate in a short interview with Cynbit's presales or delivery leads:

1. Read the customer's document (RFP, brief, email, call notes).
2. Extract functional and non-functional requirements.
3. Identify integrations, constraints and dependencies.
4. List missing information and ask the customer.
5. Choose a technical approach and cloud architecture.
6. Estimate effort.
7. Note risks and assumptions.
8. Outline a phased plan.
9. Write the proposal.

## 4. Identified business problem

**[Assumption]** Converting a customer document into a scoped technical proposal is:

- **Manual and repetitive.** Steps 1 to 9 are repeated for every enquiry, mostly by senior people whose time is also needed for delivery.
- **Inconsistent.** Two people can read the same document and extract different requirements, ask different questions and estimate with different habits.
- **Easy to get wrong silently.** A requirement that is overlooked at this stage becomes a risk during delivery. Missing information (user numbers, integration details, retention rules, budget) may never be asked about.
- **Hard to audit.** Without a record linking each requirement to the sentence it came from, it is difficult to check later why something was or was not included.

These are problems I expect, based on how the work is structured. I have not measured how much time Cynbit spends on them.

## 5. Proposed AI opportunity

**[Proposed]** An AI-assisted presales assistant, **Cynbit Presales Copilot**, that turns a customer document into a structured **first draft** for a human solution architect to review. It does the repetitive reading and structuring, and leaves decisions to people.

The design principle is: *the AI reads and drafts, rules and checks keep it honest, and a human decides.*

| Task | Done by |
|---|---|
| Read the document and extract requirements, with the source sentence for each | LLM, then checked by code |
| Find missing information and write clarification questions | Rule-based gap check plus LLM |
| Classify the project, propose an AWS or Azure architecture, identify risks, outline a roadmap | LLM, validated against a strict schema |
| Calculate effort ranges, totals and contingency | **Plain Python rules** (not the LLM) |
| Assemble the proposal draft | Python template |
| Approve architecture, estimate and proposal | **Human architect** |

## 6. Why this opportunity matters

- **It fits Cynbit's stated direction [Public].** Cynbit presents itself as a builder of AI agents and LLM workflows, including document extraction [S4, S5]. Applying the same capability to its own presales process is consistent with that positioning.
- **Consistency and coverage [Proposed].** A fixed pipeline asks the same questions of every document and shows which requirements were found and which information is missing.
- **Traceability [Proposed].** Each requirement is stored with its source excerpt, and excerpts that cannot be found in the document are flagged.
- **A reusable record [Proposed].** Structured output (JSON and a Markdown proposal) can feed later reporting, templates and calibration.
- **Realistic scope.** It needs no private training data to start, only documents and a model API.

## 7. Proposed product functionality

**Implemented in the proof of concept [Observed: tested]:**

1. Upload a PDF or TXT file, or paste text, with validation (empty, unsupported, corrupt, scanned, oversize and very long files are handled with clear messages).
2. Requirement extraction into structured fields (ID, description, category, priority, source excerpt, confidence, missing information, notes), with "Not specified" for anything the document does not state.
3. Clarification questions based on detected gaps.
4. Project classification with reasons.
5. AWS or Azure architecture recommendation (component, service, purpose, reason, related requirements, status "Recommended" or "Optional"), with a diagram.
6. Effort estimate by phase with deterministic totals, contingency, what-if inputs and visible assumptions.
7. Risk, assumption and unknown lists, kept separate from confirmed facts.
8. Phased roadmap with duration ranges and no calendar dates.
9. A 16-section proposal draft, downloadable as Markdown.
10. A clearly labeled **demo mode** that runs on a built-in synthetic RFP without any AI call.

**Not implemented [Proposed for later]:** OCR for scanned PDFs, retrieval over Cynbit's past proposals, DOCX export, user accounts, saved history, CRM integration, and calibration against real delivery data.

## 8. Expected business benefits

These are **expected** benefits. None has been measured at Cynbit, and I give no numbers for them.

| Expected benefit | How it could be measured at Cynbit |
|---|---|
| Less manual effort to produce a first-draft scope | Time from receiving a document to a reviewed first draft, compared with a baseline from recent enquiries |
| Better requirement coverage | Share of requirements in a document that the draft captured, checked by a reviewer |
| More consistent proposals | Agreement between different reviewers on requirements, questions and effort ranges for the same document |
| Fewer missed unknowns | Number of customer questions that were needed later but not asked in the first round |
| Easier onboarding of junior presales staff | Reviewer rating of the drafts and the time to reach acceptable quality |

## 9. Market and competitor overview

I searched public product pages and review sites on 24 November 2026. This is a limited overview, not a market study.

**Category 1: RFP and proposal response platforms [Public].** Products such as Loopio, Responsive (formerly RFPIO), Inventive AI, AutoRFP.ai and 1up are listed together as RFP response management software [S8, S9, S10, S11]. They help a team *answer* RFPs, security questionnaires and similar documents, for example by extracting questions and drafting answers from a library of past responses [S9]. Loopio states that its product is designed to help organisations respond to RFPs, not issue them [S10]. The vendors publish their own efficiency claims, which I have not verified and do not reuse here.

**Category 2: General-purpose AI assistants [Assumption].** A person can paste a document into a general chat assistant and ask for requirements and an estimate. This is flexible, but the output is unstructured and unchecked unless someone builds the checks.

**Category 3: Spreadsheets and in-house templates [Assumption].** Many firms estimate with their own spreadsheets and past experience. I did not research this category.

**Where the Copilot is different [Proposed]:**

| | RFP response platforms | General AI assistant | Presales Copilot (this PoC) |
|---|---|---|---|
| Main job | Answer questionnaires from a content library | Anything | Turn a customer requirement document into a scoped technical draft |
| Architecture and effort | Not their focus [Assumption from product descriptions] | Possible but unstructured | Built in, with deterministic estimate rules |
| Source traceability for each requirement | Varies | No | Yes, with unverified excerpts flagged |
| Content library, collaboration, CRM links | Strong | No | **Not built** |

**Honest limits of this comparison:** I did not find a public product that does exactly "requirements, then architecture, then effort range, then roadmap" for custom-software firms in my limited search. That is not proof that none exists. The commercial platforms are far more mature in collaboration, content management and integrations than this proof of concept.

## 10. Feasibility and technical requirements

**[Observed] The proof of concept shows the core workflow is technically feasible with modest resources:** Python 3.14, Streamlit, PyMuPDF for PDF text, Pydantic for validation, pandas, and a hosted LLM API (a free-tier Gemini model during development). It runs on a normal Windows laptop.

**What a real deployment at Cynbit would need [Proposed]:**

- A model API with suitable data-handling terms, or a privately hosted model, because customer documents can be confidential.
- A set of past RFPs, proposals and estimates to test against and to calibrate the effort rules.
- Cynbit's own architecture patterns and estimation conventions added as reference material.
- A person from presales or delivery to review outputs during a pilot.
- Basic engineering for accounts, saved history and logging.

## 11. Risks and limitations

| Risk or limitation | Detail | Mitigation in the PoC or proposed |
|---|---|---|
| Wrong or invented content | LLMs can produce plausible but unsupported statements | Source excerpt required for each requirement, verbatim check, "Not specified" rule, schema validation, human review notice |
| Run-to-run variation [Observed] | Before guardrails existed, one development run estimated about 130 to 235 person-days where another gave 192 to 354. In the formal evaluation (3 runs, after the guardrails) the AI chose the same inputs every time and the estimate was 192 to 354 in all three. Requirement extraction did vary between runs (recall 100%, 79%, 79%). Three runs on one document are too few to rule out variation on other documents | Rule-based guardrails (no corrections were needed in the 3 evaluation runs), what-if controls, estimates labeled preliminary, human review |
| Uncalibrated estimates | Effort rules are generic assumptions, not based on Cynbit's delivery history | Stated on every estimate; calibration is a proposed pilot step |
| Confidential data | Documents are sent to an external model API | Use an approved API or private model before real customer use |
| Service reliability [Observed] | During development one model name was retired for new users and another returned repeated overload errors | Fallback models, retries, and a clearly labeled demo mode |
| Scanned documents | No OCR in the MVP | Clear error message; OCR proposed later |
| Over-trust | A polished draft can look more certain than it is | Every page and the proposal carry a draft and human-review notice; confidence values are labeled as not calibrated |
| Small evidence base | Testing used one synthetic document | Results are presented as a demonstration of method, not as proof of accuracy |

## 12. Expected implementation roadmap (adoption at Cynbit) [Proposed]

Durations are indicative ranges and depend on team size and access to people and data.

| Phase | Activities | Output | Indicative duration |
|---|---|---|---|
| 1. Validate the workflow | Short interviews with presales and delivery leads; confirm or correct the assumed workflow in section 3 | Agreed problem statement and review criteria | 1 to 2 weeks |
| 2. Retrospective pilot | Run the Copilot on a set of past enquiries; compare with what was actually proposed and delivered | Measured coverage and consistency, list of gaps | 2 to 4 weeks |
| 3. Calibrate and extend | Tune effort rules with historical data; add Cynbit templates and architecture patterns; add DOCX export | Calibrated estimate rules, branded proposal template | 3 to 5 weeks |
| 4. Integrate and harden | Accounts, saved history, logging, CRM or ticket links, data-protection review | Internal tool ready for live use | 4 to 8 weeks |
| 5. Live pilot and review | Use on real enquiries with human review and feedback | Go or no-go decision based on measured metrics | 4 to 6 weeks |

## 13. Success metrics [Proposed]

Targets are deliberately not invented here. They should be set with Cynbit after a baseline is measured in Phase 2.

| Metric | Definition | Where to find the first measurement |
|---|---|---|
| Requirement extraction quality | Recall and precision of extracted requirements against a reviewed reference list | PoC: `reports/evaluation_results.md` (sample RFP only) |
| Requirement coverage | Share of requirements that are either captured or flagged as unclear | PoC evaluation; then pilot |
| Gap coverage | Share of detected information gaps that have a clarification question | PoC evaluation; then pilot |
| Estimate consistency | Totals add up, assumptions are visible, and spread of results across repeated runs | PoC evaluation |
| Architecture relevance | Human reviewer score of each recommended component (0 to 2) | PoC human review sheet |
| Risk identification | Coverage of expected risk themes | PoC evaluation |
| Roadmap completeness | All six major phases present | PoC evaluation |
| Reliability | Pass rate for invalid files, empty input, malformed model output and missing key | PoC evaluation |
| Time to first draft | Minutes from document received to reviewed draft, versus baseline | Pilot only |
| Reviewer acceptance | Share of drafts accepted with minor edits | Pilot only |

---

## Sources

All pages were accessed on 24 November 2026. Company statements are claims by the company. Third-party listings may be out of date.

| ID | Source | Used for |
|---|---|---|
| S1 | Cynbit Technologies, home page: https://www.cynbit.in/ | Service pillars: AI automation, software development, cloud on AWS and Azure |
| S2 | Cynbit Technologies, services page: https://www.cynbit.in/services | AWS and Azure deployment, zero-trust security, tools such as Docker, Kubernetes, Terraform, CI/CD; Jaipur headquarters |
| S3 | Cynbit Technologies, our story: https://www.cynbit.in/story | Founded in Jaipur; official launch in 2024 |
| S4 | Cynbit Technologies, contact page: https://www.cynbit.in/contact | AI agents, LLM integrations and workflow automation; enquiry form; clients served globally |
| S5 | Page on a Vercel deployment of Cynbit's site: https://cynbit.vercel.app/ | Team size and project count claims; legacy modernisation and AWS/Azure migration; examples of AI automation. Appears to be a version of the company's site; claims should be confirmed on cynbit.in |
| S6 | Crunchbase profile: https://www.crunchbase.com/organization/cynbit-technologies | Private company, 11 to 50 employees (third-party listing) |
| S7 | Cynbit Technologies on GitHub: https://github.com/Cynbit-Technologies | Service categories and cloud tooling |
| S8 | Loopio features: https://loopio.com/features | Example of an RFP response platform |
| S9 | Loopio, RFP automation: https://loopio.com/info/rfi-software | How response platforms extract requirements and draft answers from past responses |
| S10 | G2, Loopio vs Responsive comparison: https://www.g2.com/compare/loopio-vs-responsive-formerly-rfpio | Loopio's stated purpose (responding to RFPs, not issuing them) |
| S11 | Gartner Peer Insights listing: https://www.gartner.com/reviews/product/sifthub-72076134 | Category listing of RFP response management products and alternatives |

**Not used as sources:** other people's public code repositories about Cynbit, which are third-party interpretations and may contain errors. Vendor performance claims were not reused because they are unverified marketing statements.
