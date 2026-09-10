from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()

class ResearchRequest(BaseModel):
    query: str
    thread_id: str

class ResearchResponse(BaseModel):
    thread_id: str
    final_report: str
    current_step: int

@router.post("/research", response_model=ResearchResponse)
async def run_research(request: Request, payload: ResearchRequest):
    graph = request.app.state.graph
    
    config = {
        "configurable": {"thread_id": payload.thread_id},
        "recursion_limit": 50
    }
    
    initial_state = {
        "query": payload.query
    }
    
    try:
        # Execute asynchronously
        result = await graph.ainvoke(initial_state, config=config)
        
        return ResearchResponse(
            thread_id=payload.thread_id,
            final_report=result.get("final_report", "No report generated."),
            current_step=result.get("current_step", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))