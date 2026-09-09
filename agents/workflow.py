from typing import Any, Dict
from langgraph.graph import END, StateGraph

from agents.common.state import AuraState
from agents.planner.graph import generate_plan

# ---------------------------------------------------------
# 1. Mock Nodes (Placeholders for Qusai and Amr)
# ---------------------------------------------------------
def mock_researcher(state: AuraState) -> Dict[str, Any]:
    current_step = state.get("current_step", 0)
    task = state["plan"][current_step]
    
    print(f"--- [MOCK RESEARCHER] Executing task: {task} ---")
    
    # Simulate finding data and updating the state
    mock_data = state.get("research_data", {})
    mock_data[f"step_{current_step}"] = {"status": "scraped", "content": "Mock data"}
    
    # Return the updated data and increment the step
    return {
        "research_data": mock_data,
        "current_step": current_step + 1
    }

def mock_decision(state: AuraState) -> Dict[str, Any]:
    print(f"--- [MOCK DECISION] Generating final recommendation ---")
    return {
        "final_report": "Mock Recommendation: Qdrant is the best option."
    }

# ---------------------------------------------------------
# 2. Dynamic Router Logic
# ---------------------------------------------------------
def route_research(state: AuraState) -> str:
    """Evaluates the state to determine the next node."""
    current_step = state.get("current_step", 0)
    plan_length = len(state.get("plan", []))
    
    # If we have not finished all steps, loop back to the researcher
    if current_step < plan_length:
        return "researcher"
    
    # If all steps are done, exit the loop and make a decision
    return "decision"

# ---------------------------------------------------------
# 3. Master Graph Construction
# ---------------------------------------------------------
def build_master_graph(checkpointer=None):  # <-- Add argument here
    workflow = StateGraph(AuraState)
    
    # Register all nodes
    workflow.add_node("planner", generate_plan)
    workflow.add_node("researcher", mock_researcher)
    workflow.add_node("decision", mock_decision)
    
    # Define the starting point
    workflow.set_entry_point("planner")
    
    # Conditional Edges
    workflow.add_conditional_edges(
        source="planner",
        path=route_research,
        path_map={"researcher": "researcher", "decision": "decision"}
    )
    workflow.add_conditional_edges(
        source="researcher",
        path=route_research,
        path_map={"researcher": "researcher", "decision": "decision"}
    )
    
    workflow.add_edge("decision", END)
    
    # Pass the checkpointer into compile()
    return workflow.compile(checkpointer=checkpointer)