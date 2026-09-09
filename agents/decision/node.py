from typing import Any, Dict
from decisions.recommendations.generator import generate_final_recommendation
from decisions.scoring.engine import calculate_weighted_scores
from agents.common.state import AuraState  

def decision_node(state: AuraState) -> AuraState:
    """LangGraph node that runs the Decision Intelligence logic on current state."""

    # 1. Extract verified evidence and criteria from the global state
    objective = state.get("objective", state.get("query", "Unknown Objective"))
    criteria = state.get("criteria", [])
    raw_options = state.get("alternatives", [])

    # 2. Score the alternatives based on explicit criteria
    scored_options = calculate_weighted_scores(raw_options, criteria)

    # 3. Generate the evidence-grounded recommendation
    recommendation = generate_final_recommendation(objective, scored_options, criteria)

    # 4. Append the results back to the global state for the output/reporting stage
    return {
        "final_report": recommendation.model_dump_json(),   
        "current_step": state.get("current_step", 0) + 1,
    }
