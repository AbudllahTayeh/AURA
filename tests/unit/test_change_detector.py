from memory.long_term.change_detector import ResearchChangeDetector
from memory.long_term.postgres_store import ResearchSessionArtifact


def test_change_detector_deltas():
    old_art = ResearchSessionArtifact(
        session_id="session_001",
        query="Vector DBs",
        final_report="Old report",
        sources_used=["https://old.com"],
    )
    new_art = ResearchSessionArtifact(
        session_id="session_002",
        query="Vector DBs",
        final_report="New updated report",
        sources_used=["https://old.com", "https://new.com"],
    )

    diff = ResearchChangeDetector.detect_changes(old_art, new_art)

    assert diff["content_changed"] is True
    assert diff["has_delta"] is True
    assert "https://new.com" in diff["added_sources"]
    assert len(diff["removed_sources"]) == 0
