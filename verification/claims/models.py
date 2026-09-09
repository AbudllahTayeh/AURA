from dataclasses import dataclass, field
from enum import Enum


class ClaimStatus(str, Enum):
    """The verification status of a claim."""
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONFLICTING = "CONFLICTING"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


@dataclass
class Evidence:
    """A piece of evidence retrieved to support/refute a claim."""
    id: str
    text: str
    source: str
    reliability_score: float = 0.5


@dataclass
class Claim:
    """A single factual claim extracted from a generated report."""
    text: str
    source_sentence: str = ""
    status: ClaimStatus = ClaimStatus.UNKNOWN
    confidence: float = 0.0
    evidence_ids: list[str] = field(default_factory=list)
