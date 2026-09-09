from agents.workflow import build_master_graph
from langgraph.checkpoint.postgres import PostgresSaver
from apps.api.core.config import settings

def main():
    # 1. Use the DB URL defined in your FastAPI config
    db_uri = settings.database_url
    
    # 2. Connect to the Postgres container
    with PostgresSaver.from_conn_string(db_uri) as checkpointer:
        
        # This automatically creates the LangGraph tables in your database 
        # if this is the very first time you are running it.
        checkpointer.setup()
        
        # 3. Compile the graph using the checkpointer
        app = build_master_graph(checkpointer=checkpointer)
        
        # 4. We MUST provide a thread_id config to track state. 
        # In production, this would be a unique Session ID or User ID.
        config = {
            "configurable": {"thread_id": "demo-thread-1"},
            "recursion_limit": 50
        }
        
        initial_state = {
            "query": "Compare Qdrant, Pinecone, and Weaviate for a production RAG application."
        }
        
        print("🚀 Starting Master Workflow with Postgres Checkpointing...")
        result = app.invoke(initial_state, config=config)
        
        print("\n=== FINAL REPORT ===")
        print(result.get("final_report"))

if __name__ == "__main__":
    main()