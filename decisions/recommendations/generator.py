from typing import List

from decisions.criteria.models import (
    AlternativeOption,
    DecisionCriterion,
    FinalRecommendation,
)


def generate_final_recommendation(
    objective: str,
    scored_options: List[AlternativeOption],
    criteria: List[DecisionCriterion],
) -> FinalRecommendation:
    """Selects the top-scored option and formats the final traceable recommendation."""

    if not scored_options:
        return FinalRecommendation(
            research_objective=objective,
            criteria_used=criteria,
            alternatives_compared=[],
            recommended_option="None",
            trade_off_analysis="No alternatives available for comparison.",
            overall_confidence=0.0,
        )

    top_option = scored_options[0]

    # Calculate a basic confidence metric based on uncertainty flags
    total_flags = sum(len(opt.uncertainty_flags) for opt in scored_options)
    confidence = max(0.0, 1.0 - (total_flags * 0.1))

    if len(scored_options) > 1 and criteria:
        trade_off_summary = (
            f"{top_option.option_name} is recommended with a score of "
            f"{top_option.total_weighted_score}. "
            f"If the weight of {criteria[0].name} changes, "
            f"{scored_options[1].option_name} may become preferable."
        )
    else:
        trade_off_summary = (
            f"{top_option.option_name} is recommended with a score of "
            f"{top_option.total_weighted_score}. "
            "No additional alternatives available for trade-off comparison."
        )

    return FinalRecommendation(
        research_objective=objective,
        criteria_used=criteria,
        alternatives_compared=scored_options,
        recommended_option=top_option.option_name,
        trade_off_analysis=trade_off_summary,
        overall_confidence=confidence,
    )
