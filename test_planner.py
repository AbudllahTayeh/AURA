from agents.planner.graph import build_planner_graph

def main():
    # 1. Compile the graph
    app = build_planner_graph()
    
    # 2. Define the initial state (the user's question)
    initial_state = {
        "query": "Compare Qdrant, Pinecone, and Weaviate for a production RAG application.",
        "plan": [],
        "current_step": 0,
        "research_data": {},
        "messages": [],
        "final_report": ""
    }
    
    # 3. Run the graph
    print("🚀 Starting Planner Agent...\n")
    result = app.invoke(initial_state)
    
    # 4. Print the output state
    print("\n=== FINAL AURA STATE ===")
    print(f"Query: {result['query']}")
    print("Generated Plan:")
    for step in result['plan']:
        print(f"  -> {step}")

if __name__ == "__main__":
    main()