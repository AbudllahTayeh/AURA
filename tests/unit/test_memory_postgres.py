from memory.long_term.postgres_store import (
    LongTermMemoryManager,
    ResearchSessionArtifact,
)


def test_postgres_artifact_formatting():
    manager = LongTermMemoryManager()
    artifact = ResearchSessionArtifact(
        session_id="session_123",
        query="Vector DB performance",
        final_report="Qdrant demonstrates low latency.",
        sources_used=["https://qdrant.tech/docs"],
    )

    data = manager.format_artifact_for_storage(artifact)

    assert data["session_id"] == "session_123"
    assert data["query"] == "Vector DB performance"
    assert "https://qdrant.tech/docs" in data["sources_used"]
