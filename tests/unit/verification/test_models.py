from verification.claims.models import Claim, ClaimStatus, Evidence


def test_claim_default_status_is_unknown():
    claim = Claim(text="Qdrant supports hybrid search.")
    assert claim.status == ClaimStatus.UNKNOWN


def test_claim_default_confidence_is_zero():
    claim = Claim(text="Some claim.")
    assert claim.confidence == 0.0


def test_claim_evidence_ids_default_empty_list():
    claim = Claim(text="Some claim.")
    assert claim.evidence_ids == []


def test_evidence_default_reliability_score():
    evidence = Evidence(id="ev1", text="Some evidence.", source="docs")
    assert evidence.reliability_score == 0.5


def test_claim_status_can_be_updated():
    claim = Claim(text="Some claim.")
    claim.status = ClaimStatus.SUPPORTED
    claim.confidence = 0.95
    assert claim.status == ClaimStatus.SUPPORTED
    assert claim.confidence == 0.95
