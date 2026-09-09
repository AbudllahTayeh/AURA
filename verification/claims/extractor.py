import re

from verification.claims.models import Claim


def extract_claims(text: str) -> list[Claim]:
    """
    Split a block of text into individual sentences and
    return each one as an unverified Claim.

    This is a simple first version. Later this can be
    improved to filter out non-factual sentences
    (questions, greetings, etc.) or use an LLM instead.
    """
    if not text or not text.strip():
        return []

    # Split on sentence-ending punctuation (., !, ?) followed by a space
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    claims = []
    for sentence in raw_sentences:
        sentence = sentence.strip()
        if sentence:
            claims.append(Claim(text=sentence, source_sentence=sentence))

    return claims
