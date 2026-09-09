from agents.memory.agent import MemoryAgent


def test_memory_agent_flow():
    agent = MemoryAgent()
    session_id = "test_agent_session"

    # Test short-term checkpointing
    state_data = {"query": "Test query", "status": "in_progress"}
    agent.checkpoint_session(session_id, state_data)

    retrieved = agent.retrieve_session(session_id)
    assert retrieved["query"] == "Test query"

    # Test archiving
    archived = agent.archive_session(
        session_id=session_id,
        query="Test query",
        final_report="Test report",
        sources=["http://example.com"],
    )
    assert archived["session_id"] == session_id
    assert archived["final_report"] == "Test report"
