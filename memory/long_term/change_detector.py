from typing import Any, Dict, List

from memory.long_term.postgres_store import ResearchSessionArtifact


class ResearchChangeDetector:
    @staticmethod
    def detect_changes(
        old_artifact: ResearchSessionArtifact,
        new_artifact: ResearchSessionArtifact,
    ) -> Dict[str, Any]:
        """Compares two research artifacts and returns differences.

        Tracks added/removed sources and content updates.
        """
        old_sources = set(old_artifact.sources_used)
        new_sources = set(new_artifact.sources_used)

        added_sources: List[str] = list(new_sources - old_sources)
        removed_sources: List[str] = list(old_sources - new_sources)

        content_changed = (
            old_artifact.final_report.strip() != new_artifact.final_report.strip()
        )

        return {
            "query": new_artifact.query,
            "content_changed": content_changed,
            "added_sources": added_sources,
            "removed_sources": removed_sources,
            "has_delta": content_changed or bool(added_sources or removed_sources),
        }
