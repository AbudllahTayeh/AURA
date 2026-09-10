import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.tools import query_knowledge_base

if __name__ == "__main__":
    # Test query against your previously ingested resume
    response = query_knowledge_base.invoke({"query": "What experience did you have at Logatta?", "top_k": 2})
    print("--- Tool Output ---")
    print(response)