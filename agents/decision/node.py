from typing import Any, Dict
from decisions.scoring.engine import calculate_weighted_scores
from decisions.recommendations.generator import generate_final_recommendation
from decisions.recommendations.formatter import format_decision_report
from agents.common.state import AuraState

def decision_node(state: AuraState) -> AuraState:
    """LangGraph node that runs the Decision Intelligence logic on current state."""
    
    objective = state.get("objective", state.get("query", "Unknown Objective"))
    criteria = state.get("criteria", [])
    raw_options = state.get("alternatives", [])
    
    scored_options = calculate_weighted_scores(raw_options, criteria)
    recommendation = generate_final_recommendation(objective, scored_options, criteria)
    
    # Format the recommendation into Markdown before updating the state
    markdown_report = format_decision_report(recommendation)
    
    return {
        "final_report": markdown_report,
        "current_step": state.get("current_step", 0) + 1,
    }