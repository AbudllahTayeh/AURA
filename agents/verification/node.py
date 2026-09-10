from typing import Any, Dict

from agents.common.state import AuraState
from verification.claims.extractor import extract_claims
from verification.evidence.rag_checker import check_claim_against_rag


def verification_node(state: AuraState) -> Dict[str, Any]:
    """
    LangGraph node that runs the Verification Agent on the final
    report produced by the Decision node.

    1. Extract individual factual claims from the final report.
    2. Check each claim against the real RAG knowledge base + Gemini.
    3. Write the verified claims back into the shared AuraState so
       downstream nodes (or the API response) can access them.
    """
    print("--- [VERIFICATION] Checking final report for factual claims ---")

    final_report = state.get("final_report", "")

    if not final_report:
        return {"verified_claims": []}

    claims = extract_claims(final_report)

    verified = []
    for claim in claims:
        checked = check_claim_against_rag(claim)
        verified.append(
            {
                "text": checked.text,
                "status": checked.status.value,
                "confidence": checked.confidence,
            }
        )

    print(f"--- [VERIFICATION] Checked {len(verified)} claim(s) ---")

    return {"verified_claims": verified}
