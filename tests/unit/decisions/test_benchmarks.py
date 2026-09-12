from decisions.criteria.models import (
    AlternativeOption,
    DecisionCriterion,
    EvidenceScore,
)
from decisions.recommendations.generator import generate_final_recommendation
from decisions.scoring.engine import calculate_weighted_scores


def test_sensitivity_to_weight_changes():
    """
    Benchmark: Proves the recommendation dynamically shifts when the user's
    priorities (criteria weights) change, satisfying the trade-off requirement.
    """
    options = [
        AlternativeOption(
            option_name="SelfHostedDB",
            scores=[
                EvidenceScore(criterion_name="Security", normalized_score=10.0, evidence_summary="Local", citation_ids=["doc1"], claim_state="SUPPORTED"),
                EvidenceScore(criterion_name="EaseOfUse", normalized_score=4.0, evidence_summary="Complex", citation_ids=["doc2"], claim_state="SUPPORTED"),
            ],
        ),
        AlternativeOption(
            option_name="CloudDB",
            scores=[
                EvidenceScore(criterion_name="Security", normalized_score=5.0, evidence_summary="Public", citation_ids=["doc3"], claim_state="SUPPORTED"),
                EvidenceScore(criterion_name="EaseOfUse", normalized_score=10.0, evidence_summary="Managed", citation_ids=["doc4"], claim_state="SUPPORTED"),
            ],
        ),
    ]

    # Scenario A: Security is the top priority (80% weight)
    security_heavy_criteria = [
        DecisionCriterion(name="Security", weight=0.8, description="Data privacy"),
        DecisionCriterion(name="EaseOfUse", weight=0.2, description="Managed service"),
    ]
    
    scored_a = calculate_weighted_scores(options, security_heavy_criteria)
    recommendation_a = generate_final_recommendation("Select DB", scored_a, security_heavy_criteria)
    
    # SelfHostedDB: (10*0.8) + (4*0.2) = 8.8. CloudDB: (5*0.8) + (10*0.2) = 6.0
    assert recommendation_a.recommended_option == "SelfHostedDB"
    assert "CloudDB may become preferable" in recommendation_a.trade_off_analysis

    # Scenario B: Ease of Use is the top priority (80% weight)
    ease_heavy_criteria = [
        DecisionCriterion(name="Security", weight=0.2, description="Data privacy"),
        DecisionCriterion(name="EaseOfUse", weight=0.8, description="Managed service"),
    ]
    
    scored_b = calculate_weighted_scores(options, ease_heavy_criteria)
    recommendation_b = generate_final_recommendation("Select DB", scored_b, ease_heavy_criteria)
    
    # CloudDB: (5*0.2) + (10*0.8) = 9.0. SelfHostedDB: (10*0.2) + (4*0.8) = 5.2
    assert recommendation_b.recommended_option == "CloudDB"


def test_criterion_consistency_with_missing_weights():
    """
    Benchmark: Verifies the engine safely defaults to 0.0 weight if Abood's
    verification stage passes an evidence score for a criterion that Abd's planner
    did not officially request.
    """
    strict_criteria = [
        DecisionCriterion(name="Cost", weight=1.0, description="Only cost matters"),
    ]
    
    options = [
        AlternativeOption(
            option_name="Option X",
            scores=[
                EvidenceScore(criterion_name="Cost", normalized_score=8.0, evidence_summary="Cheap", citation_ids=["x1"], claim_state="SUPPORTED"),
                # This criterion is NOT in the strict_criteria list
                EvidenceScore(criterion_name="RogueMetric", normalized_score=10.0, evidence_summary="Irrelevant", citation_ids=["x2"], claim_state="SUPPORTED"),
            ],
        )
    ]
    
    scored = calculate_weighted_scores(options, strict_criteria)
    
    # The RogueMetric should be ignored (weight 0.0), so total is exactly 8.0
    assert scored[0].total_weighted_score == 8.0

def test_uncertainty_calibration():
    """
    Benchmark: Verifies the engine correctly calibrates overall confidence
    by penalizing the score 10% for every uncertainty flag across all options,
    bounding the minimum confidence at 0.0.
    """
    criteria = [
        DecisionCriterion(name="Reliability", weight=1.0, description="Uptime"),
    ]
    
    options = [
        AlternativeOption(
            option_name="System Alpha",
            scores=[
                EvidenceScore(criterion_name="Reliability", normalized_score=8.0, evidence_summary="Stable", citation_ids=["doc1"], claim_state="SUPPORTED")
            ],
            # 2 uncertainty flags
            uncertainty_flags=["Conflicting downtime report in Source B", "Missing SLAs for 2023"] 
        ),
        AlternativeOption(
            option_name="System Beta",
            scores=[
                EvidenceScore(criterion_name="Reliability", normalized_score=9.0, evidence_summary="Very Stable", citation_ids=["doc2"], claim_state="SUPPORTED")
            ],
            # 1 uncertainty flag
            uncertainty_flags=["Vendor claims lack independent verification"] 
        ),
    ]

    scored = calculate_weighted_scores(options, criteria)
    recommendation = generate_final_recommendation("Select Reliable System", scored, criteria)

    # Total flags = 3. Expected confidence = 1.0 - (3 * 0.1) = 0.7
    assert recommendation.overall_confidence == 0.7

    # Test mathematical floor: Confidence cannot drop below 0.0 even with excessive flags
    options[0].uncertainty_flags = ["Flag"] * 12
    scored_floor = calculate_weighted_scores(options, criteria)
    recommendation_floor = generate_final_recommendation("Select Reliable System", scored_floor, criteria)
    
    assert recommendation_floor.overall_confidence == 0.0