from unittest.mock import patch

from agents.common.state import AuraState
from agents.workflow import build_master_graph, route_research


def test_route_research_transitions():
    """Verify route_research correctly returns 'researcher' when steps remain and 'decision' when complete."""
    # When steps remain
    state_in_progress: AuraState = {
        "plan": ["Step 1", "Step 2"],
        "current_step": 0,
    }
    assert route_research(state_in_progress) == "researcher"

    state_last_step: AuraState = {
        "plan": ["Step 1", "Step 2"],
        "current_step": 1,
    }
    assert route_research(state_last_step) == "researcher"

    # When all steps are done
    state_done: AuraState = {
        "plan": ["Step 1", "Step 2"],
        "current_step": 2,
    }
    assert route_research(state_done) == "decision"


def _mock_researcher(state):
    step = state.get("current_step", 0)
    data = dict(state.get("research_data", {}))
    data[f"step_{step}"] = f"Research content for step {step}"
    return {"research_data": data, "current_step": step + 1}


@patch("agents.workflow.real_researcher", side_effect=_mock_researcher)
@patch("agents.decision.node.extract_criteria_and_alternatives")
@patch("agents.workflow.generate_plan")
def test_master_graph_executes_decision_node_fallback(
    mock_planner, mock_extractor, mock_research
):
    """Verify that the master graph routes through planner, researcher loop, and executes decision_node."""
    mock_planner.return_value = {
        "plan": ["Search alternatives", "Analyze features"],
        "current_step": 0,
    }
    mock_extractor.return_value = ([], [])

    graph = build_master_graph()
    initial_state: AuraState = {
        "query": "Compare Vector Databases",
    }

    result = graph.invoke(initial_state)

    assert "final_report" in result
    assert "## Decision Recommendation: None" in result["final_report"]
    assert result["current_step"] == 3
    assert "step_0" in result.get("research_data", {})
    assert "step_1" in result.get("research_data", {})


@patch("agents.workflow.real_researcher", side_effect=_mock_researcher)
@patch("agents.workflow.generate_plan")
def test_master_graph_executes_decision_node_with_options(
    mock_planner, mock_research
):
    """Verify master graph produces a real ranked decision report when criteria and alternatives are provided."""
    mock_planner.return_value = {
        "plan": ["Single Step"],
        "current_step": 0,
    }

    graph = build_master_graph()
    initial_state: AuraState = {
        "query": "Compare Vector Databases",
        "objective": "Select Vector DB",
        "criteria": [
            {"name": "Cost", "weight": 0.6, "description": "Hosting cost"},
            {"name": "Performance", "weight": 0.4, "description": "Latency"},
        ],
        "alternatives": [
            {
                "option_name": "Qdrant",
                "scores": [
                    {
                        "criterion_name": "Cost",
                        "normalized_score": 9.0,
                        "evidence_summary": "Open source and self-hostable",
                        "citation_ids": ["doc1"],
                        "claim_state": "SUPPORTED",
                    },
                    {
                        "criterion_name": "Performance",
                        "normalized_score": 8.0,
                        "evidence_summary": "Low latency Rust engine",
                        "citation_ids": ["doc2"],
                        "claim_state": "SUPPORTED",
                    },
                ],
            },
            {
                "option_name": "Pinecone",
                "scores": [
                    {
                        "criterion_name": "Cost",
                        "normalized_score": 5.0,
                        "evidence_summary": "Expensive managed pricing",
                        "citation_ids": ["doc3"],
                        "claim_state": "SUPPORTED",
                    },
                    {
                        "criterion_name": "Performance",
                        "normalized_score": 9.0,
                        "evidence_summary": "Fast cloud indices",
                        "citation_ids": ["doc4"],
                        "claim_state": "SUPPORTED",
                    },
                ],
            },
        ],
    }

    result = graph.invoke(initial_state)

    assert "final_report" in result
    assert "## Decision Recommendation: Qdrant" in result["final_report"]
    assert "| **Qdrant** | 8.6 |" in result["final_report"]
    assert "| **Pinecone** | 6.6 |" in result["final_report"]
    assert result["current_step"] == 2
