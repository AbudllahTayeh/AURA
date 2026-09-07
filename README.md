# AURA

## Autonomous Unified Research Agent

AURA is a multi-agent research system that combines Retrieval-Augmented
Generation (RAG), agent orchestration, hybrid retrieval, evidence
verification, and citation-grounded report generation.

## Goals

AURA is designed to:

- Decompose complex research questions
- Retrieve information from multiple sources
- Perform hybrid vector and keyword search
- Rerank retrieved documents
- Verify evidence
- Detect unsupported claims
- Use tools when necessary
- Generate citation-grounded research reports

## Architecture

```text
User Query
    ↓
Planner Agent
    ↓
Research Tasks
    ↓
Research Agents
    ↓
Web Search / Knowledge Base / Tools
    ↓
Hybrid Retrieval
    ↓
Reranker
    ↓
Evidence Verification
    ↓
Synthesizer
    ↓
Citation Validation
    ↓
Final Research Report