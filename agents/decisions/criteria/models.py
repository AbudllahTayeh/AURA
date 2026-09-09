from typing import List

from pydantic import BaseModel, Field


class DecisionCriterion(BaseModel):
    name: str
    weight: float = Field(
        ..., description="Decimal weight summing to 1.0 across all criteria"
    )
    description: str


class EvidenceScore(BaseModel):
    criterion_name: str
    normalized_score: float = Field(..., ge=1, le=10)
    evidence_summary: str
    citation_ids: List[str] = Field(
        ..., description="Required links to verified Sources/Document IDs"
    )
    claim_state: str = Field(..., description="e.g., SUPPORTED, CONFLICTING")


class AlternativeOption(BaseModel):
    option_name: str
    scores: List[EvidenceScore]
    total_weighted_score: float = 0.0
    uncertainty_flags: List[str] = Field(default_factory=list)


class FinalRecommendation(BaseModel):
    research_objective: str
    criteria_used: List[DecisionCriterion]
    alternatives_compared: List[AlternativeOption]
    recommended_option: str
    trade_off_analysis: str
    overall_confidence: float
