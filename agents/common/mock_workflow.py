"""Mock agent implementations for offline testing and development.

Provides deterministic responses for Planner and Researcher nodes without
requiring external LLM API keys or incurring rate limit penalties.
"""

from typing import Any, Dict

from agents.common.state import AuraState


def mock_planner(state: AuraState) -> Dict[str, Any]:
    """Generates realistic sequential research steps without invoking external LLM APIs."""
    query = state.get("query", "")
    print(f"\n--- [MOCK PLANNER] Decomposing research query: '{query}' ---")

    q_lower = query.lower()
    if "amd" in q_lower and "nvidia" in q_lower:
        plan = [
            "Analyze AMD RDNA/CDNA microarchitecture, Compute Units, and memory subsystem (Infinity Cache & HBM3)",
            "Analyze NVIDIA Ada Lovelace and Blackwell microarchitecture, Tensor Cores, and NVLink interconnect",
            "Evaluate software ecosystem: CUDA vs ROCm maturity, PyTorch optimization, and developer tooling",
        ]
    elif any(term in q_lower for term in ["database", "vector", "qdrant", "pinecone", "milvus"]):
        plan = [
            "Evaluate vector indexing algorithms (HNSW vs IVF), memory footprint, and query latency",
            "Analyze infrastructure deployment models: managed serverless vs open-source self-hosting TCO",
            "Assess client SDK maturity, ecosystem integration, and enterprise production readiness",
        ]
    else:
        plan = [
            f"Analyze core technical architecture and specifications for: {query}",
            f"Evaluate performance benchmarks, efficiency, and trade-offs for: {query}",
            f"Assess ecosystem maturity, developer adoption, and total cost of ownership for: {query}",
        ]

    for idx, step in enumerate(plan, 1):
        print(f"  Step {idx}: {step}")

    return {
        "plan": plan,
        "current_step": 0,
    }


def mock_researcher(state: AuraState) -> Dict[str, Any]:
    """Synthesizes realistic evidence and citations for each research step without external API calls."""
    current_step = state.get("current_step", 0)
    plan = state.get("plan", [])
    if not plan or current_step >= len(plan):
        return {"current_step": current_step}

    task = plan[current_step]
    total_steps = len(plan)
    print(f"--- [MOCK RESEARCHER] Executing step {current_step + 1}/{total_steps}: {task} ---")

    query = state.get("query", "").lower()
    task_lower = task.lower()

    if "amd" in query and "nvidia" in query:
        if "amd" in task_lower or current_step == 0:
            findings = (
                "AMD CDNA 3 (Instinct MI300X) and RDNA 3 (RX 7900 XTX) employ a modular chiplet architecture. "
                "CDNA 3 integrates 304 Compute Units, 19,456 stream cores, and up to 192GB HBM3 memory delivering 5.3 TB/s bandwidth. "
                "AI Matrix Accelerators support BF16, FP16, and INT8. AMD offers superior raw VRAM capacity and memory bandwidth per dollar. "
                "[Citation: amd-cdna3-whitepaper, rocm-mi300-overview]"
            )
        elif "nvidia" in task_lower or current_step == 1:
            findings = (
                "NVIDIA Ada Lovelace (RTX 4090) and Blackwell (B200) utilize dual-die packaging connected via 10 TB/s NV-HBI. "
                "Blackwell features 208 billion transistors, 2nd Gen Transformer Engine with FP4/FP8 precision, and 5th Gen NVLink (1.8 TB/s bidirectional). "
                "In deep learning training and inference, NVIDIA architecture demonstrates industry-leading compute density and tensor core efficiency. "
                "[Citation: nvidia-blackwell-arch, ada-lovelace-whitepaper]"
            )
        else:
            findings = (
                "Software ecosystem and compiler stack: NVIDIA CUDA remains the dominant industry standard with seamless PyTorch, "
                "TensorRT-LLM, and Triton integration. Zero setup required for 99% of open-source models. "
                "AMD ROCm 6.x has made massive progress with upstream PyTorch and vLLM support, though long-tail library porting and developer mindshare trail CUDA. "
                "[Citation: semi-analysis-gpu-benchmarks-2024, pytorch-ecosystem-report]"
            )
    elif any(term in query for term in ["database", "vector", "qdrant", "pinecone", "milvus"]):
        if current_step == 0:
            findings = (
                "Vector indexing benchmarks indicate that Rust-based Qdrant delivers sub-10ms P99 latency with custom HNSW graphs. "
                "Pinecone Serverless separates storage and compute, achieving infinite scale at variable latency. "
                "[Citation: vector-benchmarks-2024, qdrant-rust-perf]"
            )
        elif current_step == 1:
            findings = (
                "Total cost of ownership: Qdrant open-source self-hosting achieves ~65% cost savings for large datasets (>50M vectors). "
                "Pinecone managed serverless provides lower operational overhead for low-to-medium query volume. "
                "[Citation: tco-vector-db-study, pinecone-pricing-audit]"
            )
        else:
            findings = (
                "Ecosystem adoption: Both platforms provide rich Python, TypeScript, and Go SDKs. "
                "Qdrant provides superior on-premise and air-gapped compliance. "
                "[Citation: enterprise-eval-2024]"
            )
    else:
        findings = (
            f"Technical findings for '{task}': Candidate solutions exhibit contrasting architectural priorities. "
            f"Option A maximizes throughput, modularity, and cost efficiency, while Option B delivers turnkey developer experience and mature tooling. "
            f"[Citation: benchmark-analysis-2024, architecture-review]"
        )

    data = dict(state.get("research_data", {}))
    data[f"step_{current_step}"] = findings
    return {
        "research_data": data,
        "current_step": current_step + 1,
    }
