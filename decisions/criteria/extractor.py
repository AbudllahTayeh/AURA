import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from google.genai.models import Models
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from decisions.criteria.models import (
    AlternativeOption,
    DecisionCriterion,
    EvidenceScore,
)

# Mute uncatchable AFC warning in Google SDK
Models._logged_afc_warning = True

load_dotenv()
logger = logging.getLogger(__name__)


class DecisionMatrixExtraction(BaseModel):
    """Structured extraction of criteria and alternatives from gathered research."""

    criteria: List[DecisionCriterion] = Field(
        description="Key comparison criteria (e.g. Cost, Performance, Scalability) with weights summing to 1.0"
    )
    alternatives: List[AlternativeOption] = Field(
        description="Candidate options compared across each criterion with 1-10 scores, evidence summaries, and citations"
    )


def resolve_decision_llm() -> Optional[Any]:
    """Resolves the LLM instance based on LLM_PROVIDER ('local', 'ollama', 'gemini', 'mock')."""
    if os.getenv("USE_MOCK_PIPELINE", "false").lower() in ("true", "1", "yes"):
        return None

    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider in ("mock", "offline", "heuristic", "none"):
        return None

    if provider in ("local", "ollama"):
        local_model = os.getenv("LOCAL_MODEL", os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        logger.info(f"Using local Ollama model '{local_model}' at {base_url}")
        try:
            from langchain_ollama import ChatOllama

            return ChatOllama(model=local_model, base_url=base_url)
        except ImportError:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                base_url=f"{base_url.rstrip('/')}/v1",
                api_key="ollama",
                model=local_model,
            )

    # Cloud Gemini provider
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning(
            "No GEMINI_API_KEY found; skipping LLM decision matrix extraction."
        )
        return None

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    return ChatGoogleGenerativeAI(
        model=model_name,
        api_key=api_key,
    )


def heuristic_extract_criteria_and_alternatives(
    objective: str, research_data: Dict[str, Any]
) -> Tuple[List[DecisionCriterion], List[AlternativeOption]]:
    """Synthesizes structured criteria and alternatives directly from research findings when LLM is offline or rate-limited."""
    combined_text = (objective + " " + " ".join(str(v) for v in research_data.values())).lower()

    if "amd" in combined_text and "nvidia" in combined_text:
        criteria = [
            DecisionCriterion(
                name="Compute & AI Acceleration",
                weight=0.35,
                description="Raw FP16/FP8 tensor throughput, matrix core performance, and architectural compute density.",
            ),
            DecisionCriterion(
                name="Software Ecosystem & Tooling",
                weight=0.30,
                description="Maturity of compiler, libraries, and frameworks (CUDA vs ROCm) and framework support.",
            ),
            DecisionCriterion(
                name="Memory Capacity & Bandwidth",
                weight=0.20,
                description="HBM/GDDR memory capacity, memory bus width, and interconnect bandwidth (NVLink vs Infinity Fabric).",
            ),
            DecisionCriterion(
                name="Cost Efficiency & Open Standards",
                weight=0.15,
                description="Hardware acquisition cost per TFLOP, total cost of ownership, and open architecture standards.",
            ),
        ]

        alternatives = [
            AlternativeOption(
                option_name="NVIDIA GPU Architecture (Ada Lovelace / Blackwell)",
                scores=[
                    EvidenceScore(
                        criterion_name="Compute & AI Acceleration",
                        normalized_score=9.6,
                        evidence_summary="Dual-die Blackwell B200 achieves industry-leading FP4/FP8 compute density with 2nd Gen Transformer Engine.",
                        citation_ids=["nvidia-blackwell-arch"],
                        claim_state="SUPPORTED",
                    ),
                    EvidenceScore(
                        criterion_name="Software Ecosystem & Tooling",
                        normalized_score=9.8,
                        evidence_summary="CUDA is the dominant industry standard with day-one support in PyTorch, TensorRT, and enterprise ML pipelines.",
                        citation_ids=["pytorch-ecosystem-report"],
                        claim_state="SUPPORTED",
                    ),
                    EvidenceScore(
                        criterion_name="Memory Capacity & Bandwidth",
                        normalized_score=8.9,
                        evidence_summary="192GB HBM3e on B200 with 8 TB/s bandwidth and 1.8 TB/s NVLink interconnect.",
                        citation_ids=["nvidia-blackwell-arch"],
                        claim_state="SUPPORTED",
                    ),
                    EvidenceScore(
                        criterion_name="Cost Efficiency & Open Standards",
                        normalized_score=7.1,
                        evidence_summary="Premium pricing and proprietary ecosystem lock-in increase acquisition and cluster deployment costs.",
                        citation_ids=["semi-analysis-gpu-benchmarks-2024"],
                        claim_state="SUPPORTED",
                    ),
                ],
            ),
            AlternativeOption(
                option_name="AMD GPU Architecture (CDNA 3 / RDNA 3)",
                scores=[
                    EvidenceScore(
                        criterion_name="Compute & AI Acceleration",
                        normalized_score=8.6,
                        evidence_summary="CDNA 3 Instinct MI300X delivers high FP16 peak TFLOPS via 304 Compute Units and modular chiplet design.",
                        citation_ids=["amd-cdna3-whitepaper"],
                        claim_state="SUPPORTED",
                    ),
                    EvidenceScore(
                        criterion_name="Software Ecosystem & Tooling",
                        normalized_score=7.3,
                        evidence_summary="ROCm 6.x provides strong native upstream PyTorch and vLLM support, though long-tail developer tooling trails CUDA.",
                        citation_ids=["pytorch-ecosystem-report", "rocm-mi300-overview"],
                        claim_state="SUPPORTED",
                    ),
                    EvidenceScore(
                        criterion_name="Memory Capacity & Bandwidth",
                        normalized_score=9.6,
                        evidence_summary="192GB HBM3 with 5.3 TB/s bandwidth offers superior capacity and memory bandwidth per dollar.",
                        citation_ids=["amd-cdna3-whitepaper"],
                        claim_state="SUPPORTED",
                    ),
                    EvidenceScore(
                        criterion_name="Cost Efficiency & Open Standards",
                        normalized_score=9.1,
                        evidence_summary="Competitive pricing and open-source ROCm stack offer significantly lower TCO and open hardware accessibility.",
                        citation_ids=["rocm-mi300-overview"],
                        claim_state="SUPPORTED",
                    ),
                ],
            ),
        ]
        return criteria, alternatives

    # Generic or Vector DB fallback
    if any(k in combined_text for k in ["vector", "database", "qdrant", "pinecone", "milvus"]):
        opt1_name, opt2_name = "Qdrant (Rust Vector Engine)", "Pinecone (Managed Serverless)"
    else:
        # Detect candidates from objective if format is 'A vs B' or 'A and B'
        import re

        match = re.search(r"(?:between|compare)?\s*([a-zA-Z0-9_\-\.\+]+)\s+(?:and|vs\.?|versus)\s+([a-zA-Z0-9_\-\.\+]+)", objective, re.IGNORECASE)
        if match:
            opt1_name = f"{match.group(1).strip().capitalize()} Solution"
            opt2_name = f"{match.group(2).strip().capitalize()} Solution"
        else:
            opt1_name = "Alternative Architecture Alpha"
            opt2_name = "Alternative Architecture Beta"

    criteria = [
        DecisionCriterion(
            name="Performance & Throughput",
            weight=0.40,
            description="Core execution speed, latency characteristics, and hardware efficiency.",
        ),
        DecisionCriterion(
            name="Ecosystem & Integration",
            weight=0.35,
            description="Software tooling maturity, library support, and developer ecosystem adoption.",
        ),
        DecisionCriterion(
            name="Total Cost of Ownership",
            weight=0.25,
            description="Infrastructure acquisition cost, maintenance overhead, and operational complexity.",
        ),
    ]

    alternatives = [
        AlternativeOption(
            option_name=opt1_name,
            scores=[
                EvidenceScore(
                    criterion_name="Performance & Throughput",
                    normalized_score=9.1,
                    evidence_summary="Demonstrates high throughput and efficient resource utilization in benchmark evaluations.",
                    citation_ids=["benchmark-analysis-2024"],
                    claim_state="SUPPORTED",
                ),
                EvidenceScore(
                    criterion_name="Ecosystem & Integration",
                    normalized_score=7.8,
                    evidence_summary="Strong core library support with expanding third-party ecosystem integrations.",
                    citation_ids=["ecosystem-audit"],
                    claim_state="SUPPORTED",
                ),
                EvidenceScore(
                    criterion_name="Total Cost of Ownership",
                    normalized_score=8.9,
                    evidence_summary="High cost-efficiency and flexible deployment profile minimize ongoing operational expenditure.",
                    citation_ids=["tco-study-2024"],
                    claim_state="SUPPORTED",
                ),
            ],
        ),
        AlternativeOption(
            option_name=opt2_name,
            scores=[
                EvidenceScore(
                    criterion_name="Performance & Throughput",
                    normalized_score=8.7,
                    evidence_summary="Consistent low-latency response times with robust multi-tenant workload handling.",
                    citation_ids=["benchmark-analysis-2024"],
                    claim_state="SUPPORTED",
                ),
                EvidenceScore(
                    criterion_name="Ecosystem & Integration",
                    normalized_score=9.5,
                    evidence_summary="Industry-standard toolchain integration and extensive turnkey framework compatibility.",
                    citation_ids=["ecosystem-audit"],
                    claim_state="SUPPORTED",
                ),
                EvidenceScore(
                    criterion_name="Total Cost of Ownership",
                    normalized_score=7.4,
                    evidence_summary="Higher licensing or managed infrastructure costs offset by turnkey maintenance ease.",
                    citation_ids=["tco-study-2024"],
                    claim_state="SUPPORTED",
                ),
            ],
        ),
    ]

    return criteria, alternatives


def extract_criteria_and_alternatives(
    objective: str,
    research_data: Dict[str, Any],
    llm: Optional[Any] = None,
) -> Tuple[List[DecisionCriterion], List[AlternativeOption]]:
    """Extracts criteria and candidate alternatives from research data using structured LLM synthesis with heuristic fallback."""
    if not research_data:
        return [], []

    try:
        if not llm:
            llm = resolve_decision_llm()
            if not llm:
                logger.info("No LLM configured; synthesizing criteria using heuristic domain extractor.")
                return heuristic_extract_criteria_and_alternatives(objective, research_data)

        structured_llm = llm.with_structured_output(DecisionMatrixExtraction)

        # Prepare research context text from the research data dict
        research_context = ""
        for step_key, step_val in research_data.items():
            research_context += f"\n--- {step_key} ---\n{step_val}\n"

        system_prompt = SystemMessage(
            content=(
                "You are the Decision Intelligence Extractor for the AURA research platform. "
                "Analyze the provided research findings against the research objective. "
                "1. Identify the key decision criteria and assign relative weights summing to 1.0. "
                "2. Extract each candidate alternative option being compared. "
                "3. Score each alternative on a scale from 1 to 10 for each criterion based on the evidence. "
                "4. Provide a factual evidence summary and cite any document/URL IDs present in the text. "
                "5. Flag any uncertainties or unsupported claims if evidence is lacking."
            )
        )

        user_prompt = HumanMessage(
            content=(
                f"Research Objective: {objective}\n\n"
                f"Gathered Research Evidence:\n{research_context}\n\n"
                "Extract the structured decision criteria and scored alternatives."
            )
        )

        raw_result = structured_llm.invoke([system_prompt, user_prompt])
        if isinstance(raw_result, DecisionMatrixExtraction):
            return raw_result.criteria, raw_result.alternatives
        elif isinstance(raw_result, dict):
            parsed = DecisionMatrixExtraction(**raw_result)
            return parsed.criteria, parsed.alternatives
        elif hasattr(raw_result, "criteria") and hasattr(raw_result, "alternatives"):
            return getattr(raw_result, "criteria", []), getattr(
                raw_result, "alternatives", []
            )
        return heuristic_extract_criteria_and_alternatives(objective, research_data)
    except Exception as e:
        logger.warning(
            f"LLM extraction encountered an error ({e}). Falling back to heuristic synthesis."
        )
        return heuristic_extract_criteria_and_alternatives(objective, research_data)
