from agents.decisions.criteria.models import (
    AlternativeOption,
    DecisionCriterion,
    EvidenceScore,
)
from agents.decisions.recommendations.generator import (
    generate_final_recommendation,
)
from agents.decisions.scoring.engine import calculate_weighted_scores


def test_calculate_weighted_scores():
    criteria = [
        DecisionCriterion(
            name="Cost",
            weight=0.4,
            description="Lower cost is better",
        ),
        DecisionCriterion(
            name="Scalability",
            weight=0.6,
            description="Higher scalability is better",
        ),
    ]

    options = [
        AlternativeOption(
            option_name="Option A",
            scores=[
                EvidenceScore(
                    criterion_name="Cost",
                    normalized_score=8.0,
                    evidence_summary="Cheaper",
                    citation_ids=["doc1"],
                    claim_state="SUPPORTED",
                ),
                EvidenceScore(
                    criterion_name="Scalability",
                    normalized_score=5.0,
                    evidence_summary="Average",
                    citation_ids=["doc2"],
                    claim_state="SUPPORTED",
                ),
            ],
        ),
        AlternativeOption(
            option_name="Option B",
            scores=[
                EvidenceScore(
                    criterion_name="Cost",
                    normalized_score=5.0,
                    evidence_summary="Pricier",
                    citation_ids=["doc3"],
                    claim_state="SUPPORTED",
                ),
                EvidenceScore(
                    criterion_name="Scalability",
                    normalized_score=9.0,
                    evidence_summary="Highly scalable",
                    citation_ids=["doc4"],
                    claim_state="SUPPORTED",
                ),
            ],
        ),
    ]

    scored = calculate_weighted_scores(options, criteria)

    # Option B: (5.0 * 0.4) + (9.0 * 0.6) = 2.0 + 5.4 = 7.4
    # Option A: (8.0 * 0.4) + (5.0 * 0.6) = 3.2 + 3.0 = 6.2
    assert scored[0].option_name == "Option B"
    assert scored[0].total_weighted_score == 7.4
    assert scored[1].option_name == "Option A"
    assert scored[1].total_weighted_score == 6.2


def test_generate_final_recommendation():
    criteria = [
        DecisionCriterion(
            name="Cost",
            weight=0.5,
            description="Cost factor",
        ),
        DecisionCriterion(
            name="Performance",
            weight=0.5,
            description="Performance factor",
        ),
    ]

    options = [
        AlternativeOption(
            option_name="FastEngine",
            scores=[
                EvidenceScore(
                    criterion_name="Cost",
                    normalized_score=6.0,
                    evidence_summary="Moderate",
                    citation_ids=["s1"],
                    claim_state="SUPPORTED",
                ),
                EvidenceScore(
                    criterion_name="Performance",
                    normalized_score=10.0,
                    evidence_summary="Extremely fast",
                    citation_ids=["s2"],
                    claim_state="SUPPORTED",
                ),
            ],
            total_weighted_score=8.0,
        ),
        AlternativeOption(
            option_name="BudgetEngine",
            scores=[
                EvidenceScore(
                    criterion_name="Cost",
                    normalized_score=9.0,
                    evidence_summary="Very cheap",
                    citation_ids=["s3"],
                    claim_state="SUPPORTED",
                ),
                EvidenceScore(
                    criterion_name="Performance",
                    normalized_score=5.0,
                    evidence_summary="Slower",
                    citation_ids=["s4"],
                    claim_state="SUPPORTED",
                ),
            ],
            total_weighted_score=7.0,
        ),
    ]

    recommendation = generate_final_recommendation(
        "Select backend engine", options, criteria
    )

    assert recommendation.recommended_option == "FastEngine"
    assert recommendation.research_objective == "Select backend engine"
    assert recommendation.overall_confidence >= 0.0