from unittest.mock import MagicMock, patch

from agents.common.state import AuraState
from agents.decision.node import decision_node
from decisions.criteria.extractor import (
    DecisionMatrixExtraction,
    extract_criteria_and_alternatives,
)
from decisions.criteria.models import (
    AlternativeOption,
    DecisionCriterion,
    EvidenceScore,
)


def test_extract_criteria_and_alternatives_empty_data():
    criteria, alternatives = extract_criteria_and_alternatives(
        objective="Test Objective",
        research_data={},
    )
    assert criteria == []
    assert alternatives == []


def test_extract_criteria_and_alternatives_with_mock_llm():
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm

    mock_extraction = DecisionMatrixExtraction(
        criteria=[
            DecisionCriterion(name="Cost", weight=0.6, description="Monthly cost"),
            DecisionCriterion(name="Performance", weight=0.4, description="Throughput"),
        ],
        alternatives=[
            AlternativeOption(
                option_name="OptionA",
                scores=[
                    EvidenceScore(
                        criterion_name="Cost",
                        normalized_score=9.0,
                        evidence_summary="Free tier available",
                        citation_ids=["doc1"],
                        claim_state="SUPPORTED",
                    ),
                    EvidenceScore(
                        criterion_name="Performance",
                        normalized_score=8.0,
                        evidence_summary="Fast latency",
                        citation_ids=["doc2"],
                        claim_state="SUPPORTED",
                    ),
                ],
            )
        ],
    )
    mock_structured_llm.invoke.return_value = mock_extraction

    research_data = {
        "step_0": "OptionA has a generous free tier and fast p95 response times."
    }

    criteria, alternatives = extract_criteria_and_alternatives(
        objective="Evaluate OptionA",
        research_data=research_data,
        llm=mock_llm,
    )

    assert len(criteria) == 2
    assert criteria[0].name == "Cost"
    assert len(alternatives) == 1
    assert alternatives[0].option_name == "OptionA"


@patch("agents.decision.node.extract_criteria_and_alternatives")
def test_decision_node_autonomous_extraction(mock_extractor):
    mock_extractor.return_value = (
        [
            DecisionCriterion(name="Hosting", weight=0.7, description="Self hostable"),
            DecisionCriterion(name="Speed", weight=0.3, description="Query speed"),
        ],
        [
            AlternativeOption(
                option_name="Qdrant",
                scores=[
                    EvidenceScore(
                        criterion_name="Hosting",
                        normalized_score=9.0,
                        evidence_summary="Open-source Docker image",
                        citation_ids=["qdrant_doc"],
                        claim_state="SUPPORTED",
                    ),
                    EvidenceScore(
                        criterion_name="Speed",
                        normalized_score=8.5,
                        evidence_summary="Engine written in Rust",
                        citation_ids=["qdrant_bench"],
                        claim_state="SUPPORTED",
                    ),
                ],
            )
        ],
    )

    state: AuraState = {
        "query": "Should we pick Qdrant?",
        "objective": "Database selection",
        "current_step": 3,
        "research_data": {
            "step_0": "Researched Qdrant Docker images and Rust engine speed."
        },
    }

    result = decision_node(state)

    assert "final_report" in result
    report = result["final_report"]
    assert "## Decision Recommendation: Qdrant" in report
    assert "### Criteria Comparison Matrix" in report
    assert "| **Hosting** | 70% | 9.0/10 |" in report
    assert "*(Citations: qdrant_doc)*" in report
    assert result["current_step"] == 4
