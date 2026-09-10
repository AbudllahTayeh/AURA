from verification.claims.models import Claim, ClaimStatus, Evidence


def _word_overlap_score(text_a: str, text_b: str) -> float:
    """
    Very simple placeholder similarity: fraction of words in
    text_a that also appear in text_b. This is NOT a real
    semantic comparison — it's a temporary stand-in until
    the RAG system provides real embeddings/reranking.
    """
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())

    if not words_a:
        return 0.0

    overlap = words_a & words_b
    return len(overlap) / len(words_a)


def check_claim_against_evidence(
    claim: Claim,
    evidence_list: list[Evidence],
    support_threshold: float = 0.5,
) -> Claim:
    """
    Compare a claim's text against a list of evidence and
    update the claim's status, confidence, and evidence_ids
    based on the best-matching evidence found.
    """
    if not evidence_list:
        claim.status = ClaimStatus.UNSUPPORTED
        claim.confidence = 0.0
        return claim

    best_score = 0.0
    best_evidence: Evidence | None = None

    for evidence in evidence_list:
        score = _word_overlap_score(claim.text, evidence.text)
        # Weight the score by how reliable the source is
        weighted_score = score * evidence.reliability_score

        if weighted_score > best_score:
            best_score = weighted_score
            best_evidence = evidence

    if best_evidence is None or best_score < support_threshold:
        claim.status = ClaimStatus.UNSUPPORTED
        claim.confidence = round(best_score, 2)
        return claim

    claim.status = ClaimStatus.SUPPORTED
    claim.confidence = round(best_score, 2)
    claim.evidence_ids = [best_evidence.id]

    return claim
