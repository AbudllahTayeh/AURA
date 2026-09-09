import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResearchSessionArtifact(BaseModel):
    session_id: str
    user_id: Optional[str] = "default_user"
    query: str
    final_report: str
    sources_used: List[str] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LongTermMemoryManager:
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.getenv(
            "DATABASE_URL", "postgresql://aura:aura@localhost:5432/aura"
        )

    def format_artifact_for_storage(
        self, artifact: ResearchSessionArtifact
    ) -> Dict[str, Any]:
        """Prepares a research artifact for persistent storage."""
        return artifact.model_dump()
