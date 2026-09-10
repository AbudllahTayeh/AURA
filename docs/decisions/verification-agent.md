# Decision: Verification Agent Design

## Problem

AURA needs a way to fact-check claims made in generated reports before
presenting them to the user. Without this, the system could confidently
state incorrect or fabricated information (hallucinations) with no way
for the user to know which parts are trustworthy.

## Options Considered

### 1. Simple keyword/word-overlap matching (no AI)
Compare claim text against evidence text using shared word counts.

- **Pros:** Fast, free, no external dependencies.
- **Cons:** Inaccurate — cannot understand meaning, only literal word
  overlap. Tested against a real claim ("Qdrant supports hybrid search")
  and it incorrectly marked it as UNSUPPORTED due to low word overlap
  with the correct evidence.

### 2. LLM-based checking with manually provided evidence
Use Gemini to judge claim vs. evidence, but evidence is still supplied
manually (placeholder data).

- **Pros:** Much more accurate reasoning than word overlap.
- **Cons:** Evidence is not real — still disconnected from the actual
  knowledge base.

### 3. LLM-based checking with real RAG retrieval (chosen)
Use Gemini to judge claims against evidence retrieved live from the
real AURA knowledge base (`rag.tools.query_knowledge_base`, built by
the RAG team).

- **Pros:** Fully real pipeline — retrieval and reasoning both reflect
  the actual system state. Confirmed working end-to-end through the
  master LangGraph workflow.
- **Cons:** Depends on the RAG knowledge base being populated with
  real documents; depends on Gemini API availability.

## Decision

Option 3 was implemented as the primary evidence-checking path
(`verification/evidence/rag_checker.py`). Options 1 and 2 were kept
as earlier, simpler implementations (`checker.py`, `llm_checker.py`)
to show the progression and as fallbacks that don't require RAG data.

## Why Gemini specifically

Gemini 3.6 Flash was chosen because:
- Free tier available (no cost constraint for a portfolio project).
- No local GPU/model download required (unlike a self-hosted LLM),
  keeping setup simple for all team members.
- Fast enough for interactive use within the LangGraph workflow.

## Architecture Notes

- The Verification Agent only communicates with the rest of the system
  through the shared `AuraState` (reads `final_report`, writes
  `verified_claims`). It does not call other agents' node functions
  directly.
- It does call the shared `rag.tools.query_knowledge_base` tool
  directly from within its node, rather than requiring another node
  to pre-fetch evidence into the state. This was chosen because the
  claims to verify are only known after extracting them from the
  final report, so the evidence needed cannot be predicted in advance.

## Trade-offs / Future Revisit

- Evidence checking currently makes one Gemini call per claim, which
  could become slow/costly for reports with many claims. A batched or
  cached approach could be revisited if this becomes a bottleneck.
- Hallucination detection currently runs independently of evidence
  checking. It could be merged into a single call in the future to
  reduce API usage.
