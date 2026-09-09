from datetime import datetime
from typing import List

from pydantic import BaseModel


class ResearchArtifact(BaseModel):
    session_id: str
    query: str
    report_summary: str
    sources: List[str]
    created_at: datetime = datetime.utcnow()

class LongTermMemoryStore:
    def save_research_history(self, artifact: ResearchArtifact):
        # Database persistence logic using PostgreSQL connection
        pass
