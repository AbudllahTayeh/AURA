import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Import the Google GenAI SDK directly to hack the warning flag
from google.genai.models import Models

from agents.common.state import AuraState

# ---------------------------------------------------------
# HACK: Mute the uncatchable AFC warning in the Google SDK
# ---------------------------------------------------------
Models._logged_afc_warning = True 

load_dotenv()

# 1. Structured output definition
class PlanOutput(BaseModel):
    """An ordered list of atomic research tasks to execute."""
    steps: List[str] = Field(
        description="A clear, sequential list of steps to research and answer the user query."
    )

# 2. Node Execution
def generate_plan(state: AuraState):
    print(f"--- PLANNER AGENT THINKING ABOUT: {state['query']} ---")
    
    llm = ChatGoogleGenerativeAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini-3.6-flash"
    )
    
    structured_llm = llm.with_structured_output(PlanOutput, method="json_schema")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are the Orchestration Planner for the AURA research system. "
            "Your job is to break down the user's research query into a series of clear, sequential, and atomic steps. "
            "Always include steps for searching for evidence, verifying claims, and generating a final report."
        )),
        ("human", "{query}")
    ])
    
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