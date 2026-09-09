from typing import Any, Dict, List, Optional

from memory.long_term.change_detector import ResearchChangeDetector
from memory.long_term.postgres_store import (
    LongTermMemoryManager,
    ResearchSessionArtifact,
)
from memory.research_history.history_manager import ResearchHistoryManager
from memory.short_term.redis_store import ShortTermMemoryManager


class MemoryAgent:
    def __init__(self):
        self.short_term = ShortTermMemoryManager()
        self.long_term = LongTermMemoryManager()
        self.history = ResearchHistoryManager()
        self.change_detector = ResearchChangeDetector()

    def checkpoint_session(self, session_id: str, state_data: Dict[str, Any]) -> None:
        """Saves current running session state to short-term cache."""
        self.short_term.save_session_state(session_id, state_data)

    def retrieve_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieves active running session state from short-term cache."""
        return self.short_term.get_session_state(session_id)

    def archive_session(
        self,
        session_id: str,
        query: str,
        final_report: str,
        sources: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Archives a completed research session into long-term memory and history."""
        artifact = ResearchSessionArtifact(
            session_id=session_id,
            query=query,
            final_report=final_report,
            sources_used=sources or [],
        )
        self.history.add_to_history(artifact)
        return self.long_term.format_artifact_for_storage(artifact)

    def search_past_research(self, query: str) -> List[ResearchSessionArtifact]:
        """Searches archived research sessions."""
        return self.history.search_history(query)

    def compare_artifacts(
        self,
        old_artifact: ResearchSessionArtifact,
        new_artifact: ResearchSessionArtifact,
    ) -> Dict[str, Any]:
        """Detects differences between two research artifacts."""
        return self.change_detector.detect_changes(old_artifact, new_artifact)
