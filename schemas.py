"""Data shapes (schemas) for every stage. LLM output is validated against these."""
from typing import List, Literal

from pydantic import BaseModel, Field, field_validator

NOT_SPECIFIED = "Not specified"

PROJECT_CATEGORIES = [
    "Web application development",
    "Mobile application development",
    "AI/ML implementation",
    "Business process automation",
    "Cloud migration",
    "Data engineering",
    "Enterprise software integration",
    "SaaS development",
    "API development",
    "Legacy system modernization",
]

Level = Literal["High", "Medium", "Low"]


def _normalize_level(value):
    """Accept 'high', 'HIGH', ' High ' and turn them into 'High'."""
    if isinstance(value, str):
        cleaned = value.strip().capitalize()
        if cleaned in ("High", "Medium", "Low"):
            return cleaned
    return value


# ---------- Stage: requirement extraction ----------
class Requirement(BaseModel):
    requirement_id: str
    description: str
    category: str  # e.g. Functional, Security, Integration, Performance, Compliance
    priority: Level = "Medium"
    source_excerpt: str = NOT_SPECIFIED  # supporting text copied from the document
    confidence: float = 0.7  # 0.0 to 1.0
    missing_information: str = "None identified"
    notes: str = ""

    @field_validator("priority", mode="before")
    @classmethod
    def _priority(cls, v):
        return _normalize_level(v)

    @field_validator("confidence", mode="before")
    @classmethod
    def _confidence(cls, v):
        try:
            return max(0.0, min(1.0, float(v)))
        except (TypeError, ValueError):
            return 0.5


class ProjectOverview(BaseModel):
    project_name: str = NOT_SPECIFIED
    client_industry: str = NOT_SPECIFIED
    business_problem: str = NOT_SPECIFIED
    business_objectives: List[str] = Field(default_factory=list)
    target_users: List[str] = Field(default_factory=list)
    required_integrations: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    cloud_preferences: str = NOT_SPECIFIED
    security_requirements: List[str] = Field(default_factory=list)
    compliance_requirements: List[str] = Field(default_factory=list)
    performance_requirements: List[str] = Field(default_factory=list)
    scalability_requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    budget_information: str = NOT_SPECIFIED
    timeline_information: str = NOT_SPECIFIED


class ExtractionResult(BaseModel):
    overview: ProjectOverview
    requirements: List[Requirement] = Field(default_factory=list)


# ---------- Stage: project classification ----------
class ClassificationItem(BaseModel):
    category: Literal[tuple(PROJECT_CATEGORIES)]  # type: ignore[valid-type]
    reasoning: str


class ClassificationResult(BaseModel):
    classifications: List[ClassificationItem] = Field(default_factory=list)


# ---------- Stage: clarification questions ----------
class ClarificationQuestion(BaseModel):
    question: str
    reason: str  # which gap this question closes
    related_requirement_ids: List[str] = Field(default_factory=list)
    priority: Level = "Medium"

    @field_validator("priority", mode="before")
    @classmethod
    def _priority(cls, v):
        return _normalize_level(v)


class ClarificationResult(BaseModel):
    questions: List[ClarificationQuestion] = Field(default_factory=list)


# ---------- Stage: architecture ----------
class ArchitectureComponent(BaseModel):
    layer: str  # Frontend, Backend, Database, Authentication, Monitoring ...
    component_name: str
    suggested_service: str  # e.g. Amazon RDS for PostgreSQL / Azure SQL Database
    purpose: str
    reason: str
    requirement_ids: List[str] = Field(default_factory=list)
    considerations: str = ""
    status: Literal["Recommended", "Optional"] = "Recommended"

    @field_validator("status", mode="before")
    @classmethod
    def _status(cls, v):
        if isinstance(v, str) and v.strip().capitalize() in ("Recommended", "Optional"):
            return v.strip().capitalize()
        return v


class ArchitectureResult(BaseModel):
    cloud_provider: Literal["AWS", "Azure"]
    assumptions: List[str] = Field(default_factory=list)
    components: List[ArchitectureComponent] = Field(default_factory=list)
    communication_flow: str = ""
    trade_offs: List[str] = Field(default_factory=list)
    security_considerations: List[str] = Field(default_factory=list)
    scalability_considerations: List[str] = Field(default_factory=list)
    mermaid_diagram: str = ""
    @field_validator("cloud_provider", mode="before")
    @classmethod
    def _provider(cls, v):
        if isinstance(v, str):
            return {"aws": "AWS", "azure": "Azure"}.get(v.strip().lower(), v)
        return v


# ---------- Stage: effort estimation ----------
class EffortInputs(BaseModel):
    """The LLM only suggests these 'complexity signals'. Python does the maths."""
    size: Literal["Small", "Medium", "Large"] = "Medium"
    integration_count: int = 0
    security_level: Literal["Standard", "High"] = "Standard"
    requirement_clarity: Literal["Clear", "Partial", "Unclear"] = "Partial"
    ai_complexity: Literal["None", "Low", "Medium", "High"] = "None"
    has_mobile_app: bool = False
    rationale: List[str] = Field(default_factory=list)

    @field_validator("size", "security_level", "requirement_clarity", "ai_complexity", mode="before")
    @classmethod
    def _capitalize(cls, v):
        return v.strip().capitalize() if isinstance(v, str) else v

    @field_validator("integration_count", mode="before")
    @classmethod
    def _count(cls, v):
        try:
            return max(0, int(v))
        except (TypeError, ValueError):
            return 0


# ---------- Stage: risks and assumptions ----------
class RiskItem(BaseModel):
    risk_id: str
    description: str
    severity: Level = "Medium"
    potential_impact: str = ""
    suggested_mitigation: str = ""
    related_requirement: str = NOT_SPECIFIED

    @field_validator("severity", mode="before")
    @classmethod
    def _severity(cls, v):
        return _normalize_level(v)


class RiskResult(BaseModel):
    risks: List[RiskItem] = Field(default_factory=list)
    confirmed_facts: List[str] = Field(default_factory=list)  # stated in the document
    assumptions: List[str] = Field(default_factory=list)  # we are assuming these
    unknowns: List[str] = Field(default_factory=list)  # information still missing


# ---------- Stage: roadmap ----------
class RoadmapPhase(BaseModel):
    phase_name: str
    activities: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    estimated_duration: str = ""  # e.g. "2-3 weeks (depends on team size)"
    dependencies: List[str] = Field(default_factory=list)
    completion_criteria: List[str] = Field(default_factory=list)


class RoadmapResult(BaseModel):
    phases: List[RoadmapPhase] = Field(default_factory=list)
    notes: str = ""

# ---------- Stage: effort estimate (calculated by Python, never by the LLM) ----------
class PhaseEstimate(BaseModel):
    phase: str
    role: str
    tasks: List[str] = Field(default_factory=list)
    min_days: int
    max_days: int
    dependencies: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


class EstimateResult(BaseModel):
    phases: List[PhaseEstimate]
    total_min: int
    total_max: int
    contingency_percent: int
    contingency_min: int
    contingency_max: int
    overall_min: int
    overall_max: int
    drivers: List[str] = Field(default_factory=list)  # the rules that were applied, in plain words
    disclaimers: List[str] = Field(default_factory=list)
    inputs: EffortInputs    