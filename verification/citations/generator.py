from verification.claims.models import Claim, ClaimStatus


def generate_citation_report(claims: list[Claim]) -> str:
    """
    Turns a list of verified claims into a human-readable,
    citation-style report. Each claim is grouped by its
    verification status so a reader can quickly see what's
    trustworthy, what's disputed, and what couldn't be verified.
    """
    if not claims:
        return "No claims were extracted for this report."

    supported = [c for c in claims if c.status == ClaimStatus.SUPPORTED]
    partial = [c for c in claims if c.status == ClaimStatus.PARTIALLY_SUPPORTED]
    conflicting = [c for c in claims if c.status == ClaimStatus.CONFLICTING]
    unsupported = [c for c in claims if c.status == ClaimStatus.UNSUPPORTED]
    unknown = [c for c in claims if c.status == ClaimStatus.UNKNOWN]

    lines = []
    lines.append("# Verification Report\n")

    total = len(claims)
    coverage = len(supported) / total if total else 0.0
    lines.append(f"**Citation Coverage:** {coverage:.0%} ({len(supported)}/{total} claims supported)\n")

    if supported:
        lines.append("## ✅ Supported Claims\n")
        for c in supported:
            lines.append(f"- \"{c.text}\" (confidence: {c.confidence:.2f})")
        lines.append("")

    if partial:
        lines.append("## ⚠️ Partially Supported Claims\n")
        for c in partial:
            lines.append(f"- \"{c.text}\" (confidence: {c.confidence:.2f})")
        lines.append("")

    if conflicting:
        lines.append("## ❗ Conflicting Claims\n")
        for c in conflicting:
            lines.append(f"- \"{c.text}\" — sources disagree, needs human review")
        lines.append("")

    if unsupported:
        lines.append("## ❌ Unsupported Claims\n")
        for c in unsupported:
            lines.append(f"- \"{c.text}\" — no supporting evidence found")
        lines.append("")

    if unknown:
        lines.append("## ❓ Unverified Claims\n")
        for c in unknown:
            lines.append(f"- \"{c.text}\" — verification failed or inconclusive")
        lines.append("")

    return "\n".join(lines)
