from typing import Any, Dict, Optional

from memory.long_term.postgres_store import (
    LongTermMemoryManager,
    ResearchSessionArtifact,
)
from memory.short_term.redis_store import ShortTermMemoryManager


class MemoryAgent:
    def __init__(self):
        self.short_term = ShortTermMemoryManager()
        self.long_term = LongTermMemoryManager()

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
        """Archives a completed research session into long-term memory."""
        artifact = ResearchSessionArtifact(
            session_id=session_id,
            query=query,
            final_report=final_report,
            sources_used=sources or [],
        )
        return self.long_term.format_artifact_for_storage(artifact)
