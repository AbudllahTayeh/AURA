import json
import os

from dotenv import load_dotenv
from google import genai

from verification.claims.models import Claim, ClaimStatus, Evidence

load_dotenv()

_client = None


def _get_client():
    """Lazily create the Gemini client so importing this module
    doesn't fail if the API key isn't set yet."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")
        _client = genai.Client(api_key=api_key)
    return _client


def check_claim_with_llm(claim: Claim, evidence_list: list[Evidence]) -> Claim:
    """
    Use Gemini to decide whether a claim is supported, conflicting,
    or unsupported based on the given evidence. This replaces the
    naive word-overlap approach with real language understanding.
    """
    if not evidence_list:
        claim.status = ClaimStatus.UNSUPPORTED
        claim.confidence = 0.0
        return claim

    evidence_block = "\n".join(
        f"- (id={ev.id}, source={ev.source}): {ev.text}"
        for ev in evidence_list
    )

    prompt = f"""You are a fact-checking assistant.

CLAIM:
"{claim.text}"

EVIDENCE:
{evidence_block}

Decide whether the evidence SUPPORTS, CONTRADICTS, or is UNRELATED to
the claim. Respond with ONLY a JSON object in this exact format,
with no extra text before or after it:

{{
  "status": "SUPPORTED" | "CONFLICTING" | "UNSUPPORTED",
  "confidence": <number between 0.0 and 1.0>,
  "best_evidence_id": "<id of the most relevant evidence, or null>"
}}
"""

    client = _get_client()
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    raw_text = response.text.strip()
    # Strip markdown code fences if Gemini added them
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()

    try:
        result = json.loads(raw_text)
        claim.status = ClaimStatus(result["status"])
        claim.confidence = float(result["confidence"])
        if result.get("best_evidence_id"):
            claim.evidence_ids = [result["best_evidence_id"]]
    except (json.JSONDecodeError, KeyError, ValueError):
        # If Gemini didn't return valid JSON, mark as unknown
        # rather than crashing.
        claim.status = ClaimStatus.UNKNOWN
        claim.confidence = 0.0

    return claim
