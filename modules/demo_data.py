"""Deterministic demo output for the built-in sample RFP. Used only in clearly labeled DEMO MODE."""
import config
from schemas import (
    NOT_SPECIFIED,
    ArchitectureResult,
    ClarificationResult,
    ClassificationResult,
    EffortInputs,
    ExtractionResult,
    RiskResult,
    RoadmapResult,
)

SAMPLE_RFP_PATH = config.BASE_DIR / "data" / "sample_rfp.txt"


def is_sample_document(text: str) -> bool:
    """True only for the built-in synthetic sample RFP."""
    return "SYNTHETIC DEMONSTRATION DOCUMENT" in text and "MCH-RFP-2026-014" in text


def _req(rid, desc, cat, pri, excerpt, conf, missing, notes=""):
    return {
        "requirement_id": rid,
        "description": desc,
        "category": cat,
        "priority": pri,
        "source_excerpt": excerpt,
        "confidence": conf,
        "missing_information": missing,
        "notes": notes,
    }


def demo_extraction() -> ExtractionResult:
    overview = {
        "project_name": "Patient Record Management Modernization Programme",
        "client_industry": "Healthcare (multi-specialty hospital group)",
        "business_problem": (
            "Patient records are spread across paper files, shared folders and spreadsheets at each site, "
            "so staff lose time searching, documents are duplicated or misfiled, and there is no record of "
            "who viewed or changed a patient file."
        ),
        "business_objectives": [
            "Replace fragmented records with a single, secure digital patient-record workflow",
            "Reduce time spent locating and filing patient documents",
            "Improve traceability of access to and changes in patient information",
            "Reduce missed and double-booked appointments",
        ],
        "target_users": [
            "Doctors", "Nurses", "Front-desk and reception staff", "Medical records staff", "Hospital administrators",
        ],
        "required_integrations": ["Existing Hospital Management System (HMS) via its API"],
        "data_sources": [
            "Existing paper files, shared network folders and spreadsheets (historical migration is out of scope)",
            "Uploaded patient documents (lab reports, referral letters, discharge summaries)",
            "HMS patient demographic and appointment data",
        ],
        "cloud_preferences": "Cloud-hosted solution required; no provider specified",
        "security_requirements": [
            "Role-based access control",
            "Authenticated user accounts",
            "Encryption of data at rest and in transit",
            "Audit logging of access and changes",
        ],
        "compliance_requirements": [
            "India's Digital Personal Data Protection Act, 2023",
            "Additional healthcare-specific regulations to be identified by the vendor",
        ],
        "performance_requirements": ["Search and record retrieval should feel fast during busy periods (no measurable target)"],
        "scalability_requirements": ["Must scale to support additional sites in the future"],
        "constraints": [
            "Hospital IT team has three staff and can support testing but not development",
            "Migration of historical paper records is out of scope",
        ],
        "dependencies": [
            "HMS vendor cooperation for API access",
            "Hospital staff availability for workshops and user acceptance testing",
        ],
        "budget_information": NOT_SPECIFIED,
        "timeline_information": (
            "First release approximately nine months after contract signing, with phased rollout across three hospitals"
        ),
    }

    requirements = [
        _req("REQ-001", "Secure web application accessible from desktop browsers inside the hospitals", "Functional", "High",
             "The system shall provide a secure web application accessible from standard desktop browsers inside the hospitals.",
             0.95, "Supported browsers and whether tablets or mobile devices are needed are not specified."),
        _req("REQ-002", "Create, view, update and archive patient records", "Functional", "High",
             "The system shall allow authorised staff to create, view, update and archive patient records.",
             0.95, "Patient record fields and data model are not specified; existing database is not described."),
        _req("REQ-003", "Role-based access control for doctors, nurses, front-desk, records staff and administrators", "Security", "High",
             "The system shall enforce role-based access control so that doctors, nurses, front-desk staff, records staff and administrators see only the information their role permits.",
             0.95, "The permission matrix per role is not specified."),
        _req("REQ-004", "Upload scanned and digital patient documents and attach them to a patient record", "Functional", "High",
             "The system shall allow staff to upload scanned and digital patient documents (for example lab reports, referral letters and discharge summaries) and attach them to a patient record.",
             0.95, "Allowed file types, maximum file size and expected document volume are not specified."),
        _req("REQ-005", "Audit log of who viewed, created, changed or downloaded patient information", "Security", "High",
             "The system shall maintain an audit log that records who viewed, created, changed or downloaded patient information, and when.",
             0.95, "Audit log retention period and who may review logs are not specified."),
        _req("REQ-006", "Appointment management: book, reschedule, cancel and view a doctor's daily schedule", "Functional", "High",
             "The system shall provide appointment management, including booking, rescheduling, cancelling and viewing a doctor's daily schedule.",
             0.95, "Number of doctors and departments, and any reminder (SMS or email) needs, are not specified."),
        _req("REQ-007", "Integrate with the existing Hospital Management System (HMS) through its API", "Integration", "High",
             "The system shall integrate with the hospital's existing Hospital Management System (HMS) through its API so that patient demographic details and appointment information stay consistent.",
             0.9, "HMS product name, API specification, authentication method and data-sync direction are not provided."),
        _req("REQ-008", "AI-assisted suggestion of document type for uploaded documents, confirmed by staff", "AI/ML", "Medium",
             "The system shall include an AI-assisted feature that suggests a document type (for example lab report, prescription, discharge summary) for each uploaded patient document.",
             0.9, "List of document types, target accuracy, and whether patient data may be sent to external AI services are not specified.",
             "A staff member must confirm or correct each suggestion, so this is a human-in-the-loop feature."),
        _req("REQ-009", "Encrypt patient information at rest and in transit", "Security", "High",
             "Patient information must be stored securely, with encryption of data at rest and in transit.",
             0.95, "Key management approach is not specified."),
        _req("REQ-010", "Cloud hosting that can scale to additional sites", "Scalability", "High",
             "The solution must be hosted in the cloud and must scale to support growth across additional sites in the future.",
             0.9, "Expected number of concurrent users and growth figures are not specified; cloud provider is not specified."),
        _req("REQ-011", "High availability during hospital working hours", "Availability", "High",
             "The system must be highly available during hospital working hours, as clinical staff depend on it.",
             0.9, "Uptime target, recovery time objective (RTO) and recovery point objective (RPO) are not specified."),
        _req("REQ-012", "Fast search and record retrieval during busy periods", "Performance", "Medium",
             "Search and record retrieval should feel fast for staff during busy periods.",
             0.7, "No measurable response-time target is given."),
        _req("REQ-013", "Simple user interface for staff with limited technical training", "Non-functional", "Medium",
             "The user interface must be simple enough for staff with limited technical training.",
             0.85, "None identified"),
        _req("REQ-014", "Require authenticated user accounts", "Security", "High",
             "Access to the system must require authenticated user accounts.",
             0.9, "Authentication mechanism (for example single sign-on or multi-factor authentication) is not specified."),
        _req("REQ-015", "Comply with India's Digital Personal Data Protection Act, 2023", "Compliance", "High",
             "The solution must handle patient data in line with applicable data protection law, including India's Digital Personal Data Protection Act, 2023.",
             0.9, "Data residency and data retention periods are not specified."),
        _req("REQ-016", "Vendor to describe how additional healthcare-specific regulations will be identified and met", "Compliance", "Medium",
             "The vendor must describe how any additional healthcare-specific regulatory requirements will be identified and met.",
             0.8, "Which healthcare-specific regulations apply is not specified."),
        _req("REQ-017", "Hospital IT team can support testing but not development", "Constraint", "Medium",
             "The hospital IT team has three staff members and can support testing but not development.",
             0.95, "None identified"),
        _req("REQ-018", "Historical paper record migration is out of scope; only new documents are in scope", "Constraint", "Medium",
             "Migration of historical paper records is outside the scope of this project; only newly created documents are in scope.",
             0.95, "None identified"),
        _req("REQ-019", "First release about nine months after contract signing, with phased rollout across three hospitals", "Timeline", "Medium",
             "The hospital group would like the first release to go live approximately nine months after contract signing, with a phased rollout across the three hospitals.",
             0.9, "Rollout order of the hospitals is not specified."),
    ]
    return ExtractionResult.model_validate({"overview": overview, "requirements": requirements})

def demo_clarifications() -> ClarificationResult:
    def q(question, reason, ids, priority):
        return {"question": question, "reason": reason, "related_requirement_ids": ids, "priority": priority}

    questions = [
        q("How many staff are expected to use the system at the same time (peak concurrent users) across the three hospitals, and what growth is expected when new sites are added?",
          "The RFP asks for scalability but gives no user numbers, which drives sizing and cost.", ["REQ-010", "REQ-011"], "High"),
        q("Does the hospital group have a preferred or mandated cloud provider (AWS, Azure or another), or an existing cloud agreement?",
          "No cloud provider is specified, so the architecture and services depend on this choice.", ["REQ-010"], "High"),
        q("What database and data model does the HMS use today, and is there existing patient-record data that must be reused or linked?",
          "Existing database details are not described, which affects data design and integration effort.", ["REQ-002", "REQ-007"], "High"),
        q("What are the HMS product name and version, the API documentation (REST, SOAP or HL7/FHIR), the authentication method, and which system is the master for patient and appointment data?",
          "The integration is required but the API specification is not provided, making it the largest effort and risk uncertainty.", ["REQ-007"], "High"),
        q("What are the required recovery time objective (RTO), recovery point objective (RPO) and uptime target during working hours?",
          "High availability is required but no measurable targets exist, which determines redundancy and backup design.", ["REQ-011"], "High"),
        q("How long must patient records, uploaded documents and audit logs be retained, and must data stay within India?",
          "Retention and data residency are not specified but are needed for storage design and compliance with the Digital Personal Data Protection Act, 2023.", ["REQ-015", "REQ-005"], "High"),
        q("Which sign-in method is required (for example single sign-on with the hospital directory, multi-factor authentication or local accounts)?",
          "The RFP requires authenticated accounts but does not name a mechanism.", ["REQ-014"], "Medium"),
        q("Is there an expected budget range or funding constraint for this programme?",
          "No budget information is given, which limits how the solution and phasing can be scoped.", [], "Medium"),
        q("Which document types should the AI classify, what accuracy is acceptable, and is patient data allowed to be processed by external AI services?",
          "The AI feature is requested without document types, accuracy targets or data-handling limits for sensitive data.", ["REQ-008"], "Medium"),
    ]
    return ClarificationResult.model_validate({"questions": questions})


def demo_classification() -> ClassificationResult:
    items = [
        {"category": "Web application development",
         "reasoning": "REQ-001 to REQ-006 ask for a secure, role-based web application for patient records and appointments."},
        {"category": "Enterprise software integration",
         "reasoning": "REQ-007 requires integration with the existing Hospital Management System through its API."},
        {"category": "AI/ML implementation",
         "reasoning": "REQ-008 asks for AI-assisted classification of uploaded patient documents with staff confirmation."},
        {"category": "Business process automation",
         "reasoning": "The project replaces manual paper, folder and spreadsheet processes with a digital workflow (business objectives and background)."},
    ]
    return ClassificationResult.model_validate({"classifications": items})

def demo_effort_inputs() -> EffortInputs:
    return EffortInputs.model_validate(
        {
            "size": "Medium",
            "integration_count": 1,
            "security_level": "High",
            "requirement_clarity": "Partial",
            "ai_complexity": "Medium",
            "has_mobile_app": False,
            "rationale": [
                "Medium size: about 19 requirements covering five user roles, patient records, documents, appointments and audit logging (REQ-001 to REQ-006).",
                "One external integration: the existing HMS API (REQ-007), whose specification has not been provided.",
                "High security: sensitive patient data, role-based access, audit logging, encryption and DPDP Act compliance (REQ-003, REQ-005, REQ-009, REQ-015).",
                "Partial clarity: user volumes, cloud provider, retention, recovery targets and API details are missing.",
                "Medium AI complexity: document type classification with staff confirmation, which needs configuration and accuracy checks (REQ-008).",
            ],
        }
    )


# Each component lists the service for both providers so one table can build either design.
_ARCH_COMPONENTS = [
    {
        "layer": "Frontend", "name": "Staff web application",
        "aws": "Single-page web app on Amazon S3 with Amazon CloudFront",
        "azure": "Single-page web app on Azure Static Web Apps",
        "purpose": "Browser interface for doctors, nurses, front-desk and records staff.",
        "reason": "REQ-001 and REQ-013 need a simple, secure web application; static hosting behind a CDN is low-maintenance and HTTPS-only.",
        "ids": ["REQ-001", "REQ-013"],
        "considerations": "The UI framework (for example React) is an assumption. Supported browsers are not specified.",
        "status": "Recommended",
    },
    {
        "layer": "Backend", "name": "Application backend",
        "aws": "Containerised service on AWS Fargate (Amazon ECS)",
        "azure": "Azure Container Apps",
        "purpose": "Business logic for patient records, documents, appointments and role checks.",
        "reason": "Covers REQ-002, REQ-003 and REQ-006. Managed containers avoid server administration, which suits a three-person hospital IT team (REQ-017).",
        "ids": ["REQ-002", "REQ-003", "REQ-006", "REQ-017"],
        "considerations": "Language and framework are open. Scaling rules depend on the unknown concurrent user count.",
        "status": "Recommended",
    },
    {
        "layer": "API layer", "name": "API gateway",
        "aws": "Amazon API Gateway",
        "azure": "Azure API Management",
        "purpose": "Single entry point with throttling and token validation.",
        "reason": "Helpful for central access control and rate limiting, but the requirements do not demand it. A load balancer may be enough.",
        "ids": ["REQ-003", "REQ-014"],
        "considerations": "Adds cost and complexity. Decide after expected load and integration needs are known.",
        "status": "Optional",
    },
    {
        "layer": "Database", "name": "Relational database",
        "aws": "Amazon RDS for PostgreSQL (Multi-AZ)",
        "azure": "Azure Database for PostgreSQL Flexible Server (zone-redundant)",
        "purpose": "Stores patient records, appointments, roles and audit events.",
        "reason": "Patient and appointment data is structured and relational (REQ-002, REQ-006). Managed high availability supports REQ-011.",
        "ids": ["REQ-002", "REQ-006", "REQ-011"],
        "considerations": "Existing database details are not provided and PostgreSQL is an assumption. Backup and recovery targets (RTO/RPO) are unknown.",
        "status": "Recommended",
    },
    {
        "layer": "File storage", "name": "Document storage",
        "aws": "Amazon S3 with server-side encryption and versioning",
        "azure": "Azure Blob Storage with encryption and soft delete",
        "purpose": "Stores uploaded scanned and digital patient documents.",
        "reason": "REQ-004 requires document uploads. Object storage is the standard fit and supports encryption at rest (REQ-009).",
        "ids": ["REQ-004", "REQ-009"],
        "considerations": "File types, size limits and volumes are unknown. Lifecycle rules depend on the retention period.",
        "status": "Recommended",
    },
    {
        "layer": "Authentication", "name": "Identity and access",
        "aws": "Amazon Cognito (federated with the hospital directory if one exists)",
        "azure": "Microsoft Entra ID",
        "purpose": "Sign-in, optional multi-factor authentication and role assignment.",
        "reason": "REQ-014 requires authenticated users and REQ-003 requires role-based access.",
        "ids": ["REQ-003", "REQ-014"],
        "considerations": "The authentication mechanism is not specified. Confirm whether a hospital directory exists.",
        "status": "Recommended",
    },
    {
        "layer": "Security", "name": "Encryption keys and secrets",
        "aws": "AWS KMS and AWS Secrets Manager",
        "azure": "Azure Key Vault",
        "purpose": "Manage encryption keys and application secrets.",
        "reason": "REQ-009 requires encryption at rest and in transit. Central key management keeps secrets out of code.",
        "ids": ["REQ-009"],
        "considerations": "Key ownership (provider-managed or customer-managed keys) is not specified.",
        "status": "Recommended",
    },
    {
        "layer": "Security", "name": "Network and web protection",
        "aws": "AWS WAF and a VPC with private subnets",
        "azure": "Azure Front Door WAF and a Virtual Network with private endpoints",
        "purpose": "Keep data stores private and filter malicious web traffic.",
        "reason": "Patient data is sensitive (REQ-009, REQ-015). Private data stores reduce exposure.",
        "ids": ["REQ-009", "REQ-015"],
        "considerations": "Whether access is limited to hospital networks or a VPN is unknown.",
        "status": "Recommended",
    },
    {
        "layer": "Logging", "name": "Audit logging",
        "aws": "Application audit table in PostgreSQL, plus Amazon CloudWatch Logs and AWS CloudTrail",
        "azure": "Application audit table in PostgreSQL, plus Azure Monitor Logs and the Activity Log",
        "purpose": "Record who viewed, created, changed or downloaded patient information.",
        "reason": "REQ-005 requires an audit log. User-level events must be written by the application; cloud logs cover infrastructure activity.",
        "ids": ["REQ-005"],
        "considerations": "Retention period and tamper-protection needs are not specified.",
        "status": "Recommended",
    },
    {
        "layer": "Monitoring", "name": "Monitoring and alerting",
        "aws": "Amazon CloudWatch",
        "azure": "Azure Monitor and Application Insights",
        "purpose": "Track availability, errors and response times.",
        "reason": "Supports REQ-011 (availability) and REQ-012 (responsiveness).",
        "ids": ["REQ-011", "REQ-012"],
        "considerations": "No measurable targets exist yet, so alert thresholds are placeholders.",
        "status": "Recommended",
    },
    {
        "layer": "AI/ML", "name": "Document type classification",
        "aws": "Amazon Textract for text extraction with a custom classifier (for example Amazon Comprehend)",
        "azure": "Azure AI Document Intelligence (custom classification)",
        "purpose": "Suggest a document type for each upload, confirmed by staff.",
        "reason": "REQ-008 asks for AI-assisted document type suggestions. Managed services avoid building and hosting a custom model.",
        "ids": ["REQ-008"],
        "considerations": "The document type list, accuracy target and rules for sending patient data to this service are unknown. Check service availability and data residency in the chosen region.",
        "status": "Recommended",
    },
    {
        "layer": "Integration", "name": "HMS integration service",
        "aws": "Integration worker on ECS with Amazon SQS for retries",
        "azure": "Azure Container Apps job with Azure Service Bus",
        "purpose": "Exchange patient and appointment data with the hospital's HMS through its API.",
        "reason": "REQ-007 requires HMS integration. A queue-backed worker tolerates HMS downtime and retries failed calls.",
        "ids": ["REQ-007"],
        "considerations": "The HMS API specification, authentication and sync direction are unknown. A VPN or private link to the hospital network may be needed.",
        "status": "Recommended",
    },
    {
        "layer": "Deployment", "name": "CI/CD and environments",
        "aws": "GitHub Actions or AWS CodePipeline, Amazon ECR, separate dev, test and production environments",
        "azure": "GitHub Actions or Azure DevOps, Azure Container Registry, separate dev, test and production environments",
        "purpose": "Repeatable builds and releases.",
        "reason": "Supports user acceptance testing (REQ-017) and the phased rollout in REQ-019.",
        "ids": ["REQ-017", "REQ-019"],
        "considerations": "Release approval steps and change windows at the hospitals are not specified.",
        "status": "Recommended",
    },
    {
        "layer": "Resilience", "name": "Cross-region disaster recovery",
        "aws": "Cross-region backup copies with AWS Backup and a standby environment",
        "azure": "Geo-redundant backups and a paired-region standby environment",
        "purpose": "Recover from a regional outage.",
        "reason": "Only worth adding if the (unknown) RTO/RPO targets or the business require it.",
        "ids": ["REQ-011"],
        "considerations": "Must respect data residency rules. Cost increases significantly.",
        "status": "Optional",
    },
]


def demo_architecture(provider: str = "AWS") -> ArchitectureResult:
    key = "aws" if provider == "AWS" else "azure"
    other = "Azure" if provider == "AWS" else "AWS"
    components = [
        {
            "layer": c["layer"], "component_name": c["name"], "suggested_service": c[key],
            "purpose": c["purpose"], "reason": c["reason"], "requirement_ids": c["ids"],
            "considerations": c["considerations"], "status": c["status"],
        }
        for c in _ARCH_COMPONENTS
    ]
    return ArchitectureResult.model_validate(
        {
            "cloud_provider": provider,
            "assumptions": [
                f"The RFP names no cloud provider. {provider} was selected for this draft; generate {other} to compare.",
                "Hosting in an India region is assumed because the RFP cites India's DPDP Act. Data residency must be confirmed.",
                "Staff reach the application over the hospital network or a VPN. The access model is unconfirmed.",
                "Concurrent users are unknown, so the design uses managed services that can scale and includes no sizing.",
                "PostgreSQL is assumed as the database engine because no existing database is described.",
            ],
            "components": components,
            "communication_flow": (
                "Staff open the web application in a browser over HTTPS and sign in through the identity service. "
                "The frontend calls the backend API, optionally through an API gateway. The backend reads and writes "
                "patient and appointment data in the relational database, stores uploaded documents in object storage "
                "and writes audit events. After an upload, the backend asks the AI service for a document type suggestion "
                "and shows it for staff to confirm. A queue-backed integration service exchanges data with the HMS API. "
                "Monitoring and logging collect telemetry from all components."
            ),
            "trade_offs": [
                "Managed services reduce operations effort for a small hospital IT team but create provider lock-in and ongoing service costs.",
                "One relational database keeps patient, appointment and audit data consistent; heavy document search may later need a separate search service.",
                "Managed AI classification is faster than a custom model but gives less control over accuracy and needs a decision on how patient data is handled.",
                "An API gateway improves central control but adds cost and complexity, so it is marked optional.",
                "Multi-zone high availability is recommended; cross-region disaster recovery stays optional until RTO/RPO and residency rules are known.",
            ],
            "security_considerations": [
                "Encrypt data at rest and in transit using managed keys (REQ-009).",
                "Keep the database and storage on private networks and expose only the web entry point.",
                "Enforce role-based access in the backend, not only in the user interface (REQ-003).",
                "Write user-level audit events for every view, change and download (REQ-005).",
                "Confirm data residency and processing rules under the DPDP Act, 2023 before choosing regions and the AI service (REQ-015).",
                "Use least-privilege service roles and keep secrets in a managed vault.",
            ],
            "scalability_considerations": [
                "Run the backend as stateless containers so instances can be added as load grows (REQ-010).",
                "Serve the frontend from a CDN so web traffic does not load the backend.",
                "Grow the database with larger instances or read replicas; sizing needs the concurrent user count.",
                "Add new hospital sites as configuration of the same deployment rather than separate copies.",
            ],
            "mermaid_diagram": "",
        }
    )

def demo_risks() -> RiskResult:
    def risk(rid, desc, sev, impact, mitigation, related):
        return {
            "risk_id": rid, "description": desc, "severity": sev, "potential_impact": impact,
            "suggested_mitigation": mitigation, "related_requirement": related,
        }

    return RiskResult.model_validate(
        {
            "risks": [
                risk("RISK-001", "The HMS API specification, authentication and access are not yet provided, so the integration scope is unclear.",
                     "High", "Integration effort and schedule may grow, and rework is likely if the API differs from assumptions.",
                     "Obtain API documentation and a test environment before design freeze. Run a short integration spike and agree an interface contract with the HMS vendor.", "REQ-007"),
                risk("RISK-002", "Compliance and data residency rules for sensitive patient data are not defined (DPDP Act, 2023 and other healthcare rules).",
                     "High", "Late discovery of legal requirements could force changes to hosting region, storage and the AI service.",
                     "Confirm requirements with the customer's compliance team early, host in an agreed region, and complete a privacy review during design.", "REQ-015, REQ-016, REQ-009"),
                risk("RISK-003", "Key sizing and resilience inputs are missing: concurrent users, data retention, recovery targets, authentication method and budget.",
                     "High", "Architecture sizing and the effort range are uncertain, so the estimate may change after discovery.",
                     "Run a discovery workshop, close the open clarification questions and re-baseline the estimate afterwards.", "REQ-010, REQ-011, REQ-014"),
                risk("RISK-004", "Accuracy of AI document type classification is unknown: no accuracy target, sample documents or scan-quality information exist.",
                     "Medium", "Poor suggestions could slow staff down and reduce trust in the feature.",
                     "Collect representative sample documents, agree an accuracy target, keep staff confirmation mandatory and measure results on documents not used for tuning.", "REQ-008"),
                risk("RISK-005", "An external AI service may process patient data in ways the customer has not approved (location, retention, vendor terms).",
                     "Medium", "Privacy or compliance objections could block the AI feature or force a different service.",
                     "Confirm data-handling rules before selecting the AI service and check service availability in the approved region.", "REQ-008, REQ-015"),
                risk("RISK-006", "The nine-month target with a phased rollout to three hospitals may be unrealistic given the open scope and the dependency on the HMS vendor.",
                     "Medium", "Schedule slippage or reduced scope in the first release.",
                     "Plan a first release for one hospital, track the HMS dependency on the critical path and confirm team size before committing dates.", "REQ-019, REQ-007"),
                risk("RISK-007", "Cloud running costs cannot be estimated because workload and budget are not stated.",
                     "Medium", "The customer may face unexpected hosting costs.",
                     "Build a cost model once usage is known, using current provider pricing tools, and set budget alerts after go-live.", "REQ-010"),
                risk("RISK-008", "The hospital IT team is small (three people) and can support testing only. Staff availability for workshops and acceptance testing is a dependency.",
                     "Medium", "Delays in feedback and testing, and limited in-house support after go-live.",
                     "Agree a UAT schedule early, use managed cloud services and plan handover training.", "REQ-017"),
                risk("RISK-009", "Scope may grow: appointment reminders, mobile access, extra browsers or historical record migration could be requested later.",
                     "Low", "Unplanned work and disputes over what was included.",
                     "Record exclusions in the proposal and use a change-control process for new requests.", "REQ-018, REQ-006"),
            ],
            "confirmed_facts": [
                "A secure, cloud-hosted web application is required (REQ-001, REQ-010).",
                "Role-based access control, audit logging and encryption of patient data are required (REQ-003, REQ-005, REQ-009).",
                "Integration with the existing Hospital Management System through its API is required (REQ-007).",
                "An AI-assisted document type suggestion, confirmed by staff, is required (REQ-008).",
                "The first release is targeted about nine months after contract signing, with a phased rollout across three hospitals (REQ-019).",
                "Migration of historical paper records is out of scope (REQ-018).",
            ],
            "assumptions": [
                "The HMS vendor will provide API documentation and test access during detailed design.",
                "Hosting will use an India region, pending confirmation of data residency rules.",
                "Staff use desktop browsers inside the hospitals; no native mobile app is needed.",
                "The customer will answer the clarification questions before the design is frozen.",
            ],
            "unknowns": [
                "Exact scope of appointment notifications (SMS, email).",
                "Rollout order of the three hospitals.",
            ],
        }
    )


def demo_roadmap() -> RoadmapResult:
    def phase(name, activities, deliverables, duration, deps, criteria):
        return {
            "phase_name": name, "activities": activities, "deliverables": deliverables,
            "estimated_duration": duration, "dependencies": deps, "completion_criteria": criteria,
        }

    return RoadmapResult.model_validate(
        {
            "phases": [
                phase("Phase 1: Discovery and requirement finalization",
                      ["Run requirement workshops with clinical, front-desk and records staff",
                       "Answer open clarification questions (user volumes, cloud provider, retention, recovery targets, authentication, budget)",
                       "Obtain HMS API documentation and test access",
                       "Confirm compliance and data residency requirements"],
                      ["Approved requirements baseline", "Updated assumptions and risk register", "Re-baselined estimate"],
                      "About 3 to 4 weeks (depends on stakeholder availability and team size)",
                      ["Customer stakeholders available for workshops", "HMS vendor contact identified"],
                      ["High-priority clarification questions answered", "Requirements baseline approved by the customer"]),
                phase("Phase 2: Architecture and technical design",
                      ["Confirm cloud provider and region", "Design the data model and role permission matrix",
                       "Design the HMS integration interface and the document classification flow",
                       "Design security and audit logging", "Create UI wireframes"],
                      ["Architecture document", "Data model", "API contracts", "UI designs"],
                      "About 3 to 4 weeks (depends on team size)",
                      ["Phase 1 outputs", "Cloud account access"],
                      ["Design reviewed and approved by customer IT and compliance"]),
                phase("Phase 3: MVP development",
                      ["Build authentication and role-based access", "Build patient record management and document upload",
                       "Implement audit logging", "Build appointment management", "Set up environments and CI/CD"],
                      ["Working MVP in a test environment for the first hospital"],
                      "About 10 to 14 weeks (depends on team size)",
                      ["Approved design", "Test environment available"],
                      ["Core workflows demonstrated end to end", "Audit log captures the agreed events"]),
                phase("Phase 4: Integrations and advanced functionality",
                      ["Build and test the HMS integration", "Implement AI-assisted document type suggestions with staff confirmation",
                       "Add notifications if confirmed in discovery"],
                      ["HMS integration service", "Document classification feature", "Accuracy evaluation report"],
                      "About 6 to 10 weeks (may overlap with Phase 3)",
                      ["HMS API access", "Sample documents and agreed accuracy target"],
                      ["Patient and appointment data sync verified", "AI accuracy reviewed against the agreed target"]),
                phase("Phase 5: Testing and security validation",
                      ["Functional and role-permission testing", "Performance testing against agreed targets",
                       "Security testing and privacy review", "User acceptance testing with hospital staff"],
                      ["Test report", "Security findings closed or accepted", "UAT sign-off"],
                      "About 4 to 6 weeks (depends on team size)",
                      ["Features complete in a test environment", "Staff available for UAT"],
                      ["No open critical or high defects", "UAT signed off by the customer"]),
                phase("Phase 6: Deployment and handover",
                      ["Set up production environment", "Roll out in phases to the three hospitals",
                       "Train staff and the hospital IT team", "Deliver documentation and provide initial support"],
                      ["Production system", "User and administrator guides", "Handover and training records"],
                      "About 2 to 3 weeks per rollout wave (depends on rollout plan)",
                      ["Testing and UAT complete", "Hospital rollout schedule agreed"],
                      ["First hospital live and stable", "Handover accepted by the customer IT team"]),
            ],
            "notes": (
                "Durations are indicative ranges and depend on team size, working calendar and final scope. "
                "Phases 3 and 4 may overlap. Whether the nine-month target in REQ-019 is achievable cannot be confirmed "
                "until the team size and open clarification questions are settled."
            ),
        }
    )