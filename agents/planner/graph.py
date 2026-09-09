import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from agents.common.state import AuraState

# Load env variables so isolated test scripts can find the API key
load_dotenv()

# 1. Define the exact structure we want the LLM to return
class PlanOutput(BaseModel):
    """An ordered list of atomic research tasks to execute."""
    steps: List[str] = Field(
        description="A clear, sequential list of steps to research and answer the user query."
    )

# 2. Define the Node Execution
def generate_plan(state: AuraState):
    print(f"--- PLANNER AGENT THINKING ABOUT: {state['query']} ---")
    
    # Initialize the model using OpenRouter's free Llama 3.3 model
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="openrouter/free", # <-- Auto-routes to an active free model!
        temperature=0
    )
    
    # Bind the model so it is physically forced to return our PlanOutput schema
    structured_llm = llm.with_structured_output(PlanOutput)
    
    # Give the agent its identity and instructions
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Orchestration Planner for the AURA research system. "
                   "Your job is to break down the user's research query into a series of clear, sequential, and atomic steps. "
                   "Always include steps for searching for evidence, verifying claims, and generating a final report."),
        ("human", "{query}")
    ])
    
    # Connect the prompt to the structured LLM and execute it
    planner_chain = prompt | structured_llm
    result = planner_chain.invoke({"query": state["query"]})
    
    return {"plan": result.steps, "current_step": 0}

# 3. Build the Graph
def build_planner_graph():
    workflow = StateGraph(AuraState)
    workflow.add_node("planner", generate_plan)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", END)
    return workflow.compile()