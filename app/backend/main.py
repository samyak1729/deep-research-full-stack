"""FastAPI backend for Deep Research application.

Exposes research agents as REST APIs for the Streamlit frontend.
"""

from contextlib import asynccontextmanager
from typing import Optional
import logging
import os
from pathlib import Path

# Load environment variables from .env file
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from deep_research.multi_agent_supervisor import supervisor_agent
from deep_research.research_agent import researcher_agent
from deep_research.request_logger import get_api_log_summary
from langchain_core.messages import HumanMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== REQUEST/RESPONSE SCHEMAS =====

class ResearchRequest(BaseModel):
    """Request body for research operations."""
    query: str = Field(..., description="Research query or topic")
    research_type: str = Field(
        default="supervisor",
        description="Type of research: 'supervisor' for multi-agent or 'researcher' for single agent"
    )

class ResearchResponse(BaseModel):
    """Response body for research operations."""
    research_id: str = Field(..., description="Unique research ID")
    status: str = Field(..., description="Status of research: pending, running, completed, failed")
    query: str = Field(..., description="Original research query")
    result: Optional[dict] = Field(None, description="Research result with findings and report")
    error: Optional[str] = Field(None, description="Error message if research failed")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="API health status")
    version: str = Field(..., description="API version")

# ===== GLOBALS FOR RESEARCH TRACKING =====

research_store: dict[str, ResearchResponse] = {}
research_counter = 0

# ===== LIFECYCLE =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Deep Research API starting up")
    yield
    logger.info("Deep Research API shutting down")

# ===== APP INITIALIZATION =====

app = FastAPI(
    title="Deep Research API",
    description="FastAPI backend for the Deep Research application",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== ENDPOINTS =====

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0"
    )

@app.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a new research task.
    
    Args:
        request: Research request with query and type
        background_tasks: FastAPI background tasks for async research
    
    Returns:
        ResearchResponse with research ID and initial status
    """
    global research_counter
    research_counter += 1
    research_id = f"research_{research_counter}"
    
    logger.info(f"Starting research {research_id}: {request.query}")
    
    response = ResearchResponse(
        research_id=research_id,
        status="pending",
        query=request.query,
        result=None,
        error=None
    )
    
    research_store[research_id] = response
    
    # Run research in background
    background_tasks.add_task(
        run_research,
        research_id=research_id,
        query=request.query,
        research_type=request.research_type
    )
    
    return response

@app.get("/research/{research_id}", response_model=ResearchResponse)
async def get_research_status(research_id: str):
    """Get the status and results of a research task.
    
    Args:
        research_id: ID of the research task
    
    Returns:
        ResearchResponse with current status and results
    
    Raises:
        HTTPException: If research ID not found
    """
    if research_id not in research_store:
        raise HTTPException(status_code=404, detail="Research not found")
    
    return research_store[research_id]

@app.get("/research", response_model=list[ResearchResponse])
async def list_research():
    """List all research tasks.
    
    Returns:
        List of all ResearchResponse objects
    """
    return list(research_store.values())

# ===== BACKGROUND TASKS =====

async def run_research(research_id: str, query: str, research_type: str):
    """Execute research in the background.
    
    Args:
        research_id: Unique research ID
        query: Research query
        research_type: Type of research to run
    """
    try:
        research_store[research_id].status = "running"
        logger.info(f"Running {research_type} research for {research_id}")
        
        if research_type == "supervisor":
            result = await supervisor_agent.ainvoke({
                "supervisor_messages": [HumanMessage(content=query)],
                "research_brief": query,
                "draft_report": ""
            })
        else:
            result = await researcher_agent.ainvoke({
                "researcher_messages": [HumanMessage(content=query)],
                "research_topic": query
            })
        
        research_store[research_id].status = "completed"
        
        # Extract results - draft_report may not exist for researcher agent
        draft_report = result.get("draft_report", "")
        
        # If no draft report, create one from compressed research
        if not draft_report:
            compressed = result.get("compressed_research", "")
            draft_report = f"# Research Report\n\n{compressed}"
        
        research_store[research_id].result = {
            "compressed_research": result.get("compressed_research", ""),
            "raw_notes": result.get("raw_notes", []),
            "draft_report": draft_report
        }
        logger.info(f"Completed research {research_id}")
        
        # Print API log summary after research completes
        logger.info(get_api_log_summary())
        
    except Exception as e:
        logger.error(f"Research {research_id} failed: {str(e)}", exc_info=True)
        research_store[research_id].status = "failed"
        research_store[research_id].error = str(e)
        
        # Print API log summary even on error
        logger.info(get_api_log_summary())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
