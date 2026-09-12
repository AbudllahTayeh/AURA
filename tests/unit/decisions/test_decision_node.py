from agents.common.state import AuraState
from agents.decision import decision_node


def test_decision_node_generates_markdown_report():
    state: AuraState = {
        "query": "Compare Qdrant and Pinecone",
        "objective": "Select Vector DB",
        "current_step": 2,
        "criteria": [
            {"name": "Cost", "weight": 0.5, "description": "Hosting cost"},
            {"name": "Performance", "weight": 0.5, "description": "Latency"},
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
                        "normalized_score": 8.5,
                        "evidence_summary": "Rust-based low latency",
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
                        "evidence_summary": "Cloud pricing can scale high",
                        "citation_ids": ["doc3"],
                        "claim_state": "SUPPORTED",
                    },
                    {
                        "criterion_name": "Performance",
                        "normalized_score": 9.0,
                        "evidence_summary": "Managed high throughput",
                        "citation_ids": ["doc4"],
                        "claim_state": "SUPPORTED",
                    },
                ],
            },
        ],
    }

    result = decision_node(state)

    assert "final_report" in result
    assert "Decision Recommendation: Qdrant" in result["final_report"]
    assert result["current_step"] == 3


def test_decision_node_empty_alternatives_fallback():
    state: AuraState = {
        "query": "Empty research test",
        "current_step": 1,
    }

    result = decision_node(state)
        
    assert "final_report" in result
    assert result["current_step"] == 2
