from typing import Any, Dict

from agents.common.state import AuraState
from decisions.criteria.models import AlternativeOption, DecisionCriterion
from decisions.recommendations.formatter import format_decision_report
from decisions.recommendations.generator import generate_final_recommendation
from decisions.scoring.engine import calculate_weighted_scores


def decision_node(state: AuraState | Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node that runs the Decision Intelligence logic on current state."""
    objective = state.get("objective") or state.get("query", "Unknown Objective")

    raw_criteria = state.get("criteria", [])
    criteria = [
        DecisionCriterion(**c) if isinstance(c, dict) else c for c in raw_criteria
    ]

    raw_options = state.get("alternatives", [])
    options = [
        AlternativeOption(**opt) if isinstance(opt, dict) else opt for opt in raw_options
    ]

    scored_options = calculate_weighted_scores(options, criteria)
    recommendation = generate_final_recommendation(objective, scored_options, criteria)

    # Format the recommendation into Markdown before updating the state
    markdown_report = format_decision_report(recommendation)

    return {
        "final_report": markdown_report,
        "current_step": state.get("current_step", 0) + 1,
    }