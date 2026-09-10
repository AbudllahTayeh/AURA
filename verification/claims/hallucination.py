import os
import json

from dotenv import load_dotenv
from google import genai

from verification.claims.models import Claim

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")
        _client = genai.Client(api_key=api_key)
    return _client


def detect_hallucination(claim: Claim) -> dict:
    """
    Uses Gemini to flag claims that look suspiciously fabricated,
    even before we check them against real evidence. This catches
    things like invented statistics, oddly specific numbers with
    no plausible source, or internally inconsistent statements.

    Returns a dict with a boolean flag and a short reason, rather
    than mutating the Claim directly, since this is a pre-check
    that can run alongside (not instead of) evidence verification.
    """
    prompt = f"""You are reviewing a single factual claim for signs
of AI hallucination (fabricated or implausible information),
independent of whether evidence exists for it yet.

CLAIM:
"{claim.text}"

Look for red flags such as:
- Suspiciously specific numbers/statistics with no plausible source
- Claims that contradict well-known, widely established facts
- Internally inconsistent or nonsensical statements

Respond with ONLY a JSON object in this exact format:

{{
  "likely_hallucination": true | false,
  "reason": "<one short sentence>"
}}
"""

    client = _get_client()
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()

    try:
        result = json.loads(raw_text)
        return {
            "likely_hallucination": bool(result["likely_hallucination"]),
            "reason": result.get("reason", ""),
        }
    except (json.JSONDecodeError, KeyError, ValueError):
        return {"likely_hallucination": False, "reason": "Could not analyze claim."}
