from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class MetricComparison(BaseModel):
    metric_name: str

    employee_value: float
    role_average: float

    variance: float = Field(
        description="Difference from role average"
    )

    variance_percent: float = Field(
        description="Percentage difference from role average"
    )

    above_average: bool


class CapacitySignal(BaseModel):
    level: Literal[
        "VERY_HIGH",
        "HIGH",
        "MEDIUM",
        "LOW",
        "VERY_LOW"
    ]

    can_take_additional_work: bool

    recommended_capacity_change_pct: int = Field(
        description="Suggested workload increase/decrease"
    )

    confidence: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]


class QualitySignal(BaseModel):
    risk_level: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]

    high_accuracy: bool
    low_accuracy: bool

    confidence: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]


class BurnoutSignal(BaseModel):
    risk_level: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]

    confidence: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]

    reason: str


class MobilityRecommendation(BaseModel):
    action: Literal[
        "INCREASE_WORKLOAD",
        "DECREASE_WORKLOAD",
        "MAINTAIN_WORKLOAD",
        "ASSIGN_COMPLEX_TASKS",
        "ASSIGN_HIGH_VOLUME_TASKS",
        "COACHING_REQUIRED",
        "MENTOR_OTHERS",
        "REASSIGN_WORK"
    ]

    priority: int = Field(
        ge=1,
        le=5,
        description="1 is highest priority"
    )

    rationale: str


class SuitabilityProfile(BaseModel):
    high_volume_tasks: bool
    quality_sensitive_tasks: bool
    complex_reviews: bool
    escalation_handling: bool
    mentoring: bool


class BenchmarkAnalysis(BaseModel):
    mph: MetricComparison
    rph: MetricComparison
    accuracy: MetricComparison
    rating: MetricComparison


class WorkforceFlags(BaseModel):
    top_rated: bool
    mentor_candidate: bool
    promotion_candidate: bool
    reallocation_candidate: bool
    coaching_candidate: bool


class EmployeePerformanceAnalysis(BaseModel):
    id: int
    employee_name: str
    role: str

    performance_score: float

    performance_tier: Literal[
        "TOP_PERFORMER",
        "HIGH_PERFORMER",
        "SOLID_PERFORMER",
        "AVERAGE_PERFORMER",
        "LOW_PERFORMER"
    ]

    rank_in_role: int
    total_in_role: int
    percentile: float

    # Rename these to avoid collision with benchmark_analysis field names
    raw_mph: float
    raw_rph: float
    raw_accuracy: float
    raw_rating: float

    benchmark_analysis: BenchmarkAnalysis

    capacity_signal: CapacitySignal
    quality_signal: QualitySignal
    burnout_signal: BurnoutSignal

    deployment_score: float = Field(
        description="Overall staffing suitability score"
    )

    suitability_profile: SuitabilityProfile
    workforce_flags: WorkforceFlags
    recommendation: MobilityRecommendation

    key_strengths: List[str]
    improvement_areas: List[str]

    executive_summary: str
    
class EmployeePerformanceAnalysisList(BaseModel):
    analyses: List[EmployeePerformanceAnalysis]
    
class LLMPerformanceInsightsItem(BaseModel):
    id: int
    performance_tier: Literal[
        "TOP_PERFORMER", "HIGH_PERFORMER", "SOLID_PERFORMER",
        "AVERAGE_PERFORMER", "LOW_PERFORMER"
    ]
    capacity_signal: CapacitySignal
    quality_signal: QualitySignal
    burnout_signal: BurnoutSignal
    deployment_score: float
    suitability_profile: SuitabilityProfile
    recommendation: MobilityRecommendation
    key_strengths: List[str]
    improvement_areas: List[str]
    executive_summary: str


class LLMPerformanceInsightsBatch(BaseModel):
    results: List[LLMPerformanceInsightsItem]
    