from agents.memory.agent import MemoryAgent
from memory.long_term.postgres_store import ResearchSessionArtifact


def test_memory_agent_flow():
    agent = MemoryAgent()
    session_id = "test_agent_session"

    # Test short-term checkpointing
    state_data = {"query": "Test query", "status": "in_progress"}
    agent.checkpoint_session(session_id, state_data)

    retrieved = agent.retrieve_session(session_id)
    assert retrieved["query"] == "Test query"

    # Test archiving and history search
    archived = agent.archive_session(
        session_id=session_id,
        query="Test query",
        final_report="Test report",
        sources=["http://example.com"],
    )
    assert archived["session_id"] == session_id
    assert archived["final_report"] == "Test report"

    search_results = agent.search_past_research("Test")
    assert len(search_results) == 1
    assert search_results[0].session_id == session_id

    # Test artifact comparison
    old_art = ResearchSessionArtifact(
        session_id="s1", query="Q", final_report="Report v1", sources_used=[]
    )
    new_art = ResearchSessionArtifact(
        session_id="s2", query="Q", final_report="Report v2", sources_used=["src1"]
    )
    diff = agent.compare_artifacts(old_art, new_art)
    assert diff["content_changed"] is True
    assert "src1" in diff["added_sources"]
