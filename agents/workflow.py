"""AURA Master Workflow Orchestration Graph.

Defines the multi-agent StateGraph connecting:
  1. Planner Agent (Task decomposition & atomic step planning)
  2. Researcher Agent (Evidence gathering, web/academic search & scraping)
  3. Dynamic Router (Cyclic execution of research plan steps)
  4. Decision Intelligence Agent (Scoring, criteria matrix & final recommendation)
"""

import os
from typing import Any, Dict, cast

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from agents.common.mock_workflow import mock_planner, mock_researcher
from agents.common.state import AuraState
from agents.decision.node import decision_node
from agents.planner.graph import generate_plan


# ---------------------------------------------------------
# 1. Researcher Node Execution
# ---------------------------------------------------------
def researcher_node(state: AuraState) -> Dict[str, Any]:
    """Executes the current research task using the Researcher Agent sub-graph."""
    current_step = state.get("current_step", 0)
    plan = state.get("plan", [])

    if not plan or current_step >= len(plan):
        return {"current_step": current_step}

    task = plan[current_step]
    print(f"--- [RESEARCHER AGENT] Executing step {current_step + 1}/{len(plan)}: {task} ---")

    findings = f"Research summary for {task}."
    try:
        from agents.researcher.research_agent import research_graph

        research_res: Dict[str, Any] = cast(Any, research_graph).invoke(
            {"messages": [HumanMessage(content=task)]}
        )
        artifact = research_res.get("artifact")
        if artifact and getattr(artifact, "findings", None):
            findings = artifact.findings
    except Exception as e:
        print(f"⚠️ [RESEARCHER AGENT] Hit rate limit or error ({e}). Using available findings.")
        findings = f"Research summary for {task}."

    updated_data = dict(state.get("research_data", {}))
    updated_data[f"step_{current_step}"] = findings
    return {
        "research_data": updated_data,
        "current_step": current_step + 1,
    }


# Backwards compatibility alias
real_researcher = researcher_node


# ---------------------------------------------------------
# 2. Dynamic Router Logic
# ---------------------------------------------------------
def route_research(state: AuraState) -> str:
    """Evaluates pipeline state to determine the next agent transition.

    Loops through all planned research steps until completion, then transitions
    to the Decision Intelligence Agent.
    """
    current_step = state.get("current_step", 0)
    plan_length = len(state.get("plan", []))

    if current_step < plan_length:
        return "researcher"

    return "decision"


# ---------------------------------------------------------
# 3. Master Graph Construction
# ---------------------------------------------------------
def build_master_graph(checkpointer=None, mock_mode: bool = False):
    """Builds and compiles the master state graph.

    Args:
        checkpointer: Optional persistence checkpointer (e.g. PostgresSaver or AsyncPostgresSaver).
        mock_mode: If True (or if USE_MOCK_PIPELINE=true), uses offline mock planner
                   and researcher nodes to test without external LLM API keys.

    Returns:
        CompiledStateGraph: The runnable master workflow.
    """
    use_mock = mock_mode or os.getenv("USE_MOCK_PIPELINE", "false").lower() in ("true", "1", "yes")

    workflow: StateGraph = StateGraph(cast(Any, AuraState))
    
    planner_fn = mock_planner if use_mock else generate_plan
    researcher_fn = mock_researcher if use_mock else real_researcher

    # Register all nodes
    workflow.add_node("planner", planner_fn)
    workflow.add_node("researcher", researcher_fn)
    workflow.add_node("decision", decision_node)

    # Define entry point
    workflow.set_entry_point("planner")

    # Conditional Edges for dynamic loop
    workflow.add_conditional_edges(
        source="planner",
        path=route_research,
        path_map={"researcher": "researcher", "decision": "decision"},
    )
    workflow.add_conditional_edges(
        source="researcher",
        path=route_research,
        path_map={"researcher": "researcher", "decision": "decision"},
    )

    # Terminal edge from decision to END
    workflow.add_edge("decision", END)

    return workflow.compile(checkpointer=checkpointer)


__all__ = [
    "build_master_graph",
    "mock_planner",
    "mock_researcher",
    "real_researcher",
    "researcher_node",
    "route_research",
]