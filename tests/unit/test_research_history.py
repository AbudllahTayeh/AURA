from memory.long_term.postgres_store import ResearchSessionArtifact
from memory.research_history.history_manager import ResearchHistoryManager


def test_research_history_manager():
    manager = ResearchHistoryManager()
    artifact = ResearchSessionArtifact(
        session_id="session_001",
        query="Compare Qdrant and Pinecone",
        final_report="Qdrant is open source.",
    )

    manager.add_to_history(artifact)

    assert manager.get_latest_session().session_id == "session_001"
    results = manager.search_history("Qdrant")
    assert len(results) == 1
    assert results[0].session_id == "session_001"
