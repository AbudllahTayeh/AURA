from typing import Annotated, Any, Dict, List, TypedDict


# Reducer function to append new messages instead of overwriting them
def merge_lists(a: list, b: list) -> list:
    if not a:
        return b
    if not b:
        return a
    return a + b

class AuraState(TypedDict):
    # The original user question
    query: str 
    
    # The list of sub-tasks the Planner creates
    plan: List[str] 
    
    # Track which step we are currently executing
    current_step: int 
    
    # A dictionary holding all retrieved documents and evidence
    research_data: Dict[str, Any] 
    
    # A log of messages/actions passed between agents, appended sequentially
    messages: Annotated[list, merge_lists] 
    
    # The ultimate output of the Decision Agent
    final_report: str