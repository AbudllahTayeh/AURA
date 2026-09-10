from verification.citations.generator import generate_citation_report
from verification.claims.models import Claim, ClaimStatus


def test_empty_claims_returns_message():
    report = generate_citation_report([])
    assert "No claims" in report


def test_report_includes_coverage_percentage():
    claims = [
        Claim(text="Claim A", status=ClaimStatus.SUPPORTED, confidence=0.9),
        Claim(text="Claim B", status=ClaimStatus.UNSUPPORTED, confidence=0.0),
    ]
    report = generate_citation_report(claims)
    assert "50%" in report


def test_report_groups_supported_claims():
    claims = [Claim(text="Claim A", status=ClaimStatus.SUPPORTED, confidence=0.9)]
    report = generate_citation_report(claims)
    assert "Supported Claims" in report
    assert "Claim A" in report


def test_report_groups_unsupported_claims():
    claims = [Claim(text="Claim B", status=ClaimStatus.UNSUPPORTED, confidence=0.0)]
    report = generate_citation_report(claims)
    assert "Unsupported Claims" in report
    assert "Claim B" in report


def test_report_groups_conflicting_claims():
    claims = [Claim(text="Claim C", status=ClaimStatus.CONFLICTING, confidence=0.5)]
    report = generate_citation_report(claims)
    assert "Conflicting Claims" in report


def test_all_supported_claims_gives_100_percent_coverage():
    claims = [
        Claim(text="Claim A", status=ClaimStatus.SUPPORTED, confidence=1.0),
        Claim(text="Claim B", status=ClaimStatus.SUPPORTED, confidence=1.0),
    ]
    report = generate_citation_report(claims)
    assert "100%" in report
