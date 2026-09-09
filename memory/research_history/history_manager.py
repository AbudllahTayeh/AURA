from typing import List, Optional

from memory.long_term.postgres_store import ResearchSessionArtifact


class ResearchHistoryManager:
    def __init__(self):
        self._history: List[ResearchSessionArtifact] = []

    def add_to_history(self, artifact: ResearchSessionArtifact) -> None:
        """Stores a completed research artifact into history."""
        self._history.append(artifact)

    def search_history(self, query: str) -> List[ResearchSessionArtifact]:
        """Searches past research sessions by keyword match in query or report."""
        keyword = query.lower()
        return [
            art
            for art in self._history
            if keyword in art.query.lower() or keyword in art.final_report.lower()
        ]

    def get_latest_session(self) -> Optional[ResearchSessionArtifact]:
        """Retrieves the most recent research artifact from history."""
        return self._history[-1] if self._history else None
