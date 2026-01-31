"""FastAPI backend for Deep Research application.

Exposes research agents as REST APIs for the Streamlit frontend.
"""

from contextlib import asynccontextmanager
from typing import Optional
import logging
import os
from pathlib import Path
import uuid

# Load environment variables from .env file
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uvicorn

from deep_research.multi_agent_supervisor import supervisor_agent
from deep_research.research_agent import researcher_agent
from deep_research.request_logger import get_api_log_summary
from langchain_core.messages import HumanMessage

from .database import init_db, get_db, ResearchRepository, SessionLocal

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

# ===== LIFECYCLE =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Deep Research API starting up")
    # Initialize database on startup
    try:
        init_db()
        logger.info("Database initialization successful")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
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
async def start_research(
    request: ResearchRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new research task.
    
    Args:
        request: Research request with query and type
        background_tasks: FastAPI background tasks for async research
        db: Database session
    
    Returns:
        ResearchResponse with research ID and initial status
    """
    research_id = str(uuid.uuid4())
    
    logger.info(f"Starting research {research_id}: {request.query}")
    
    # Save to database
    task = ResearchRepository.create(
        db=db,
        research_id=research_id,
        query=request.query,
        research_type=request.research_type,
        status="pending"
    )
    
    response = ResearchResponse(
        research_id=research_id,
        status="pending",
        query=request.query,
        result=None,
        error=None
    )
    
    # Run research in background
    background_tasks.add_task(
        run_research,
        research_id=research_id,
        query=request.query,
        research_type=request.research_type
    )
    
    return response

@app.get("/research/{research_id}", response_model=ResearchResponse)
async def get_research_status(research_id: str, db: Session = Depends(get_db)):
    """Get the status and results of a research task.
    
    Args:
        research_id: ID of the research task
        db: Database session
    
    Returns:
        ResearchResponse with current status and results
    
    Raises:
        HTTPException: If research ID not found
    """
    task = ResearchRepository.get_by_id(db, research_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Research not found")
    
    return ResearchResponse(
        research_id=task.research_id,
        status=task.status,
        query=task.query,
        result=task.result,
        error=task.error
    )

@app.get("/research", response_model=list[ResearchResponse])
async def list_research(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all research tasks with pagination.
    
    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        db: Database session
    
    Returns:
        List of ResearchResponse objects
    """
    tasks = ResearchRepository.get_all(db, limit=limit, offset=offset)
    return [
        ResearchResponse(
            research_id=task.research_id,
            status=task.status,
            query=task.query,
            result=task.result,
            error=task.error
        )
        for task in tasks
    ]

# ===== BACKGROUND TASKS =====

async def run_research(research_id: str, query: str, research_type: str):
    """Execute research in the background.
    
    Args:
        research_id: Unique research ID
        query: Research query
        research_type: Type of research to run
    """
    db = SessionLocal()
    try:
        # Update status to running
        ResearchRepository.update_status(db, research_id, "running")
        logger.info(f"Running {research_type} research for {research_id}")
        
        async def execute_research():
            if research_type == "supervisor":
                return await supervisor_agent.ainvoke({
                    "supervisor_messages": [HumanMessage(content=query)],
                    "research_brief": query,
                    "draft_report": ""
                })
            else:
                return await researcher_agent.ainvoke({
                    "researcher_messages": [HumanMessage(content=query)],
                    "research_topic": query
                })
        
        result = await execute_research()
        
        # Extract results - draft_report may not exist for researcher agent
        draft_report = result.get("draft_report", "")
        
        # If no draft report, create one from compressed research
        if not draft_report:
            compressed = result.get("compressed_research", "")
            draft_report = f"# Research Report\n\n{compressed}"
        
        result_data = {
            "compressed_research": result.get("compressed_research", ""),
            "raw_notes": result.get("raw_notes", []),
            "draft_report": draft_report
        }
        
        # Save results to database
        ResearchRepository.update_result(db, research_id, result_data)
        logger.info(f"Completed research {research_id}")
        
        # Print API log summary after research completes
        logger.info(get_api_log_summary())
        
    except Exception as e:
        logger.error(f"Research {research_id} failed: {str(e)}", exc_info=True)
        ResearchRepository.update_error(db, research_id, str(e))
        
        # Print API log summary even on error
        logger.info(get_api_log_summary())
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
