import json
import os

from dotenv import load_dotenv
from google import genai

from rag.tools import query_knowledge_base
from verification.claims.models import Claim, ClaimStatus

load_dotenv()

_client = None


def _get_client():
    """Lazily create the Gemini client."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")
        _client = genai.Client(api_key=api_key)
    return _client


def check_claim_against_rag(claim: Claim, top_k: int = 3) -> Claim:
    """
    The full, real verification pipeline:
    1. Query the real RAG knowledge base (built by Lyth) for evidence
       related to the claim.
    2. Ask Gemini to judge whether that evidence supports,
       contradicts, or is unrelated to the claim.
    3. Update the claim with the verdict.

    This replaces the manual placeholder Evidence objects we used
    earlier with real retrieved context from the knowledge base.
    """
    # 1. Retrieve real context from RAG
    context = query_knowledge_base.invoke({"query": claim.text, "top_k": top_k})

    if not context or "currently empty" in context or "No relevant context" in context:
        claim.status = ClaimStatus.UNSUPPORTED
        claim.confidence = 0.0
        return claim

    # 2. Ask Gemini to judge the claim against the retrieved context
    prompt = f"""You are a fact-checking assistant.

CLAIM:
"{claim.text}"

RETRIEVED CONTEXT FROM KNOWLEDGE BASE:
{context}

Decide whether the context SUPPORTS, CONTRADICTS, or is UNRELATED to
the claim. Respond with ONLY a JSON object in this exact format,
with no extra text before or after it:

{{
  "status": "SUPPORTED" | "CONFLICTING" | "UNSUPPORTED",
  "confidence": <number between 0.0 and 1.0>,
  "reasoning": "<one short sentence explaining why>"
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
        claim.status = ClaimStatus(result["status"])
        claim.confidence = float(result["confidence"])
    except (json.JSONDecodeError, KeyError, ValueError):
        claim.status = ClaimStatus.UNKNOWN
        claim.confidence = 0.0

    return claim
