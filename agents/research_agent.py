import logging
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from tools.academic import search_arxiv
from tools.scraper import scrape_url

# Import all custom tools from the tools/ directory
from tools.search import search_web
from tools.wiki import search_wikipedia
from tools.youtube import extract_youtube_transcript

load_dotenv()
logger = logging.getLogger(__name__)

# ==========================================
# 1. Pydantic Schemas for Structured Output
# ==========================================
class ResearchSource(BaseModel):
    title: str = Field(description="The title of the article, video, or paper.")
    url: str = Field(description="The URL, video link, or arXiv ID of the source.")
    source_type: str = Field(description="Must be one of: 'web', 'academic', 'youtube', 'wikipedia'")
    content_summary: str = Field(description="A brief summary of what this specific source provides.")

class ResearchArtifact(BaseModel):
    query: str = Field(description="The original research task requested by the Orchestrator.")
    findings: str = Field(description="A comprehensive synthesis of the research findings based ONLY on gathered tools.")
    sources: list[ResearchSource] = Field(description="The list of valid sources found and used.")

# ==========================================
# 2. Define the Graph State
# ==========================================
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    artifact: ResearchArtifact  # The final structured output will be stored here

# ==========================================
# 3. Wrap Python Functions into AI Tools
# ==========================================
@tool
def web_search_tool(query: str, max_results: int = 5):
    """Executes a web search to find general information, news, or URLs."""
    return search_web(query, max_results)

@tool
def web_scrape_tool(url: str):
    """Scrapes a URL to extract clean text content. Use this to read the actual contents of a webpage."""
    return scrape_url(url)

@tool
def academic_search_tool(query: str, max_results: int = 3):
    """Searches arXiv for academic, peer-reviewed, and scientific papers."""
    return search_arxiv(query, max_results)

@tool
def youtube_transcript_tool(video_url: str):
    """Extracts the full spoken text transcript from a YouTube video."""
    return extract_youtube_transcript(video_url)

@tool
def wikipedia_search_tool(query: str):
    """Searches Wikipedia for clean, encyclopedic summaries of a foundational topic."""
    return search_wikipedia(query)

# Combine into a list that the LLM can see
research_tools = [
    web_search_tool, 
    web_scrape_tool, 
    academic_search_tool, 
    youtube_transcript_tool, 
    wikipedia_search_tool
]

# ==========================================
# 4. Initialize the Brain (Gemini)
# ==========================================
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=os.getenv("GEMINI_API_KEY", "mock_key_for_ci_tests"),
    temperature=0.2 
)

llm_with_tools = llm.bind_tools(research_tools)

# ==========================================
# 5. Define Graph Nodes & Edges
# ==========================================
def research_node(state: ResearchState):
    """The reasoning node that evaluates the query and decides which tool to use."""
    messages = state["messages"]
    
    if len(messages) == 1:
        system_prompt = SystemMessage(content=(
            "You are the Research & Web Agent for the AURA multi-agent platform. "
            "Use web_search_tool for general queries, academic_search_tool for scientific papers, "
            "web_scrape_tool to extract deep context from URLs, youtube_transcript_tool for videos, "
            "and wikipedia_search_tool for foundational concepts. "
            "Gather comprehensive data using multiple tools before finishing."
        ))
        messages = [system_prompt] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def synthesize_results(state: ResearchState):
    """Packages the gathered context into a strict JSON schema."""
    logger.info("Packaging research into structured artifact...")
    messages = state["messages"]
    
    # Create a specialized LLM instance forced to output the Pydantic schema
    structured_llm = llm.with_structured_output(ResearchArtifact)
    
    # Instruct the LLM to format the history
    formatting_instruction = HumanMessage(
        content="Research complete. Please synthesize the above tool results into the final ResearchArtifact JSON structure. Ensure no formatting Markdown like ```json is included."
    )
    
    final_artifact = structured_llm.invoke(messages + [formatting_instruction])
    return {"artifact": final_artifact}

def route_tools(state: ResearchState):
    """Evaluates the LLM's response to decide the next step in the graph."""
    last_message = state["messages"][-1]
    
    if last_message.tool_calls:
        return "tools"
    # When done searching, route to the formatting node instead of END
    return "synthesize"

# ==========================================
# 6. Compile the StateGraph
# ==========================================
builder = StateGraph(ResearchState)

builder.add_node("agent", research_node)
builder.add_node("tools", ToolNode(research_tools))
builder.add_node("synthesize", synthesize_results)

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent", 
    route_tools, 
    {"tools": "tools", "synthesize": "synthesize"}
)
builder.add_edge("tools", "agent")
builder.add_edge("synthesize", END)

research_graph = builder.compile()

# --- Integration Test Block ---
if __name__ == "__main__":
    print("Initializing AURA Research Agent Pipeline...\n")
    
    # We will test both the new Wikipedia and YouTube tools in one prompt
    test_query = "Read the Wikipedia page for 'State machine' and extract the transcript from this LangGraph video to explain how they connect: [https://www.youtube.com/watch?v=R8KB-Zcynxc](https://www.youtube.com/watch?v=R8KB-Zcynxc)"
    initial_state = {"messages": [HumanMessage(content=test_query)]}
    
    # Execute the graph (invoke will run the whole thing and return the final state)
    print(f"Executing task: {test_query}\nAgent is thinking...\n")
    final_state = research_graph.invoke(initial_state)
    
    print("\n=== FINAL STRUCTURED JSON ARTIFACT ===")
    artifact = final_state.get("artifact")
    
    if artifact:
        # We use .model_dump_json() to cleanly print the Pydantic object
        print(artifact.model_dump_json(indent=2))
    else:
        print("Failed to generate structured artifact.")