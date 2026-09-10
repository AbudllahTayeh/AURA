from verification.claims.extractor import extract_claims
from verification.claims.models import ClaimStatus


def test_extract_claims_splits_sentences():
    text = "Qdrant supports hybrid search. It is open source."
    claims = extract_claims(text)
    assert len(claims) == 2


def test_extract_claims_returns_correct_text():
    text = "Qdrant supports hybrid search."
    claims = extract_claims(text)
    assert claims[0].text == "Qdrant supports hybrid search."


def test_extract_claims_new_claims_are_unknown():
    text = "Qdrant supports hybrid search."
    claims = extract_claims(text)
    assert claims[0].status == ClaimStatus.UNKNOWN


def test_extract_claims_empty_text_returns_empty_list():
    claims = extract_claims("")
    assert claims == []


def test_extract_claims_whitespace_only_returns_empty_list():
    claims = extract_claims("   ")
    assert claims == []


def test_extract_claims_handles_multiple_punctuation():
    text = "Is Qdrant fast? Yes, it is very fast! It scales well."
    claims = extract_claims(text)
    assert len(claims) == 3
