#!/usr/bin/env python3
"""AURA End-to-End Execution Runner.

Executes Planner -> Research Agent -> Decision Intelligence Agent.

Usage:
    ./.venv/bin/python3 scripts/run_research.py
    ./.venv/bin/python3 scripts/run_research.py "Your custom research prompt here"
"""

import os
import sys
import time

from dotenv import load_dotenv

from agents.workflow import build_master_graph

load_dotenv()


def main():
    raw_args = sys.argv[1:]
    is_live = "--live" in raw_args
    query_args = [arg for arg in raw_args if arg not in ("--live", "--mock")]

    if not is_live:
        os.environ["USE_MOCK_PIPELINE"] = "true"

    if query_args:
        user_query = " ".join(query_args)
    else:
        user_query = (
            "what's the difference between amd and Nvidia gpu architecture"
        )

    print("\n" + "=" * 60)
    print("🚀 AURA MULTI-AGENT PIPELINE")
    print("=" * 60)
    print(f"📌 Query: {user_query}")
    if is_live:
        print("🌐 Mode: LIVE LLM (Planner & Researcher using Gemini APIs)")
    else:
        print("🧪 Mode: MOCK PLANNER & RESEARCHER (Decision Intelligence Test Mode)")
        print("💡 Tip: Pass '--live' to run with live Gemini agents once API keys are active.")
    print("=" * 60 + "\n")

    start_time = time.time()

    # 1. Compile the master graph in memory
    app = build_master_graph(mock_mode=not is_live)

    # 2. Invoke the graph
    print("⏳ Executing workflow (Planner -> Researcher -> Decision Agent)...")
    result = app.invoke({"query": user_query})

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = elapsed % 60

    print("\n" + "=" * 60)
    print("🏁 FINAL DECISION INTELLIGENCE REPORT")
    print("=" * 60)
    print(result.get("final_report", "No report generated."))
    print("-" * 60)
    print(f"⏱️ Total Execution Time: {elapsed:.2f}s ({minutes}m {seconds:.1f}s)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
