# Deep Research - Fullstack Architecture

## Overview

The Deep Research project has been converted into a production-ready fullstack application using:
- **Backend**: FastAPI (REST API, async processing, background tasks)
- **Frontend**: Streamlit (interactive UI, real-time polling)
- **Research Core**: LangGraph agents (supervisor and researcher agents)

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (Port 8501)            │
│  - Research UI with query submission                         │
│  - Real-time status polling (2s interval)                    │
│  - Result visualization (summary, notes, report)             │
│  - Research history and browsing                             │
│  - Download functionality (JSON, Markdown)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                    HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Main Routes                                            │ │
│  │ - GET  /health          → Check API health            │ │
│  │ - POST /research        → Submit new research task     │ │
│  │ - GET  /research/{id}   → Get task status & results   │ │
│  │ - GET  /research        → List all tasks              │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                   │
│         ┌───────────────┼───────────────┐                   │
│         │               │               │                   │
│     Background Tasks    │         Research Store            │
│     (async executor)    │     (in-memory cache)             │
│         │               │               │                   │
│         └───────────────┼───────────────┘                   │
│                         │                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
              Calls LangGraph Agents
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼─────────────┐       ┌──────────▼──────────┐
│  Supervisor Agent   │       │  Researcher Agent   │
│ (multi-agent        │       │  (single agent      │
│  coordination)      │       │   research)         │
└───────┬─────────────┘       └──────────┬──────────┘
        │                                 │
        │      ┌────────────────────────┐ │
        │      │  LangGraph State Graph │ │
        │      │  - LLM Calls          │ │
        │      │  - Tool Execution     │ │
        │      │  - State Management   │ │
        │      └────────────────────────┘ │
        │                                 │
        │      ┌────────────────────────┐ │
        │      │  Research Tools        │ │
        │      │  - Tavily Search       │ │
        │      │  - Think Tool          │ │
        │      │  - Refine Report       │ │
        │      └────────────────────────┘ │
        │                                 │
        └────────────────┬────────────────┘
                         │
              ┌──────────┴────────────┐
              │                       │
        ┌─────▼──────────┐    ┌──────▼───────┐
        │  OpenAI Models │    │  Tavily      │
        │  (gpt-5, etc)  │    │  Search API  │
        └────────────────┘    └──────────────┘
```

## Component Details

### Frontend (Streamlit)

**File**: `app/frontend/app.py`

**Key Features**:
- Query submission form
- Research type selection (supervisor/researcher)
- Real-time status polling
- Result visualization with tabs
- Research history browser
- Download functionality

**Data Flow**:
1. User submits query → POST `/research`
2. Frontend polls `/research/{id}` every 2 seconds
3. Display status updates in real-time
4. Show final results with formatting

**State Management**:
- Session state for research history
- Cache for API responses

### Backend (FastAPI)

**File**: `app/backend/main.py`

**Key Features**:
- RESTful API endpoints
- Async task processing
- In-memory research store
- CORS middleware for frontend access
- Health checks and monitoring

**Request/Response Models**:
```python
ResearchRequest:
  - query: str
  - research_type: "supervisor" | "researcher"

ResearchResponse:
  - research_id: str
  - status: "pending" | "running" | "completed" | "failed"
  - query: str
  - result: dict | null
  - error: str | null
```

**Background Task Processing**:
1. Request → Validate → Assign research_id
2. Return immediately with research_id
3. Run agent in background task
4. Update research_store with results
5. Frontend polls and retrieves results

### Research Agents

**Supervisor Agent** (`src/multi_agent_supervisor.py`):
- Coordinates multiple researcher agents
- Uses parallel execution for efficiency
- Makes strategic decisions about research direction
- Compresses findings from sub-agents

**Researcher Agent** (`src/research_agent.py`):
- Single-agent research workflow
- Iterative search and synthesis
- Automatic decision to continue or conclude

**State Definitions** (`src/state_*.py`):
- ResearcherState: Messages, topic, findings
- SupervisorState: Supervisor messages, brief, notes
- Output schemas for structured results

**Tools** (`src/utils.py`):
- `tavily_search()`: Web search with content summarization
- `think_tool()`: Strategic reflection
- `refine_draft_report()`: Report synthesis

## Data Models

### Research Task Lifecycle

```
┌─────────────┐
│   Pending   │  Task created, queued for execution
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Running   │  Agent is actively researching
└──────┬──────┘
       │
       ├─────────────┬─────────────┐
       │ Success     │ Failure     │
       ▼             ▼
┌──────────────┐ ┌──────────┐
│   Completed  │ │  Failed  │
└──────────────┘ └──────────┘
```

### Research Result Structure

```json
{
  "research_id": "research_1",
  "status": "completed",
  "query": "Research question...",
  "result": {
    "compressed_research": "Summary of findings...",
    "raw_notes": [
      "Raw note 1 from research process",
      "Raw note 2 from research process"
    ],
    "draft_report": "Full structured report..."
  },
  "error": null
}
```

## API Specification

### Health Check
```
GET /health

Response 200:
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Submit Research
```
POST /research
Content-Type: application/json

{
  "query": "What is quantum computing?",
  "research_type": "supervisor"
}

Response 200:
{
  "research_id": "research_1",
  "status": "pending",
  "query": "What is quantum computing?",
  "result": null,
  "error": null
}
```

### Get Research Status
```
GET /research/{research_id}

Response 200:
{
  "research_id": "research_1",
  "status": "completed",
  "query": "What is quantum computing?",
  "result": {
    "compressed_research": "...",
    "raw_notes": [...],
    "draft_report": "..."
  },
  "error": null
}

Response 404:
{"detail": "Research not found"}
```

### List All Research
```
GET /research

Response 200:
[
  { ...research_1... },
  { ...research_2... },
  ...
]
```

## Deployment Scenarios

### Local Development
```bash
# Terminal 1
python app/backend/main.py

# Terminal 2
streamlit run app/frontend/app.py
```

### Docker Compose
```bash
docker-compose up
```

### Kubernetes (Example)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deep-research-backend
spec:
  # Backend configuration
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deep-research-frontend
spec:
  # Frontend configuration
```

### Cloud Deployment (AWS, GCP, Heroku)
- Backend on Cloud Run / App Engine
- Frontend on Cloud Run / Heroku
- Persistent storage for research history
- Database instead of in-memory store

## Performance Considerations

### Backend
- **Async Processing**: Non-blocking research execution
- **Background Tasks**: Concurrent task handling
- **In-Memory Cache**: Fast status retrieval
- **Connection Pooling**: Efficient API calls

### Frontend
- **Polling Interval**: 2 seconds (configurable)
- **Timeout**: 5 minutes max wait
- **Session State**: Efficient history management
- **Lazy Loading**: Tabs load on demand

### Scaling
- Add database for persistent research store
- Use message queue (Redis, RabbitMQ) for async tasks
- Add caching layer (Redis) for frequent requests
- Load balance multiple backend instances
- Use CDN for static assets

## Security

### Current Implementation
- CORS enabled for all origins (development)
- No authentication required
- API keys in environment variables

### Production Hardening
- Restrict CORS to specific origins
- Add authentication (OAuth2, API keys)
- Use HTTPS/TLS
- Rate limiting
- Input validation
- Error handling (no sensitive info in errors)
- API key rotation
- Environment-specific configs

## Future Enhancements

### Planned Features
- User authentication and authorization
- Persistent database storage
- Research result caching
- Advanced analytics
- Custom research agents
- Webhook notifications
- API key management
- Research templates
- Collaborative research

### Technical Improvements
- Add websockets for real-time updates
- Implement streaming responses
- Add request/response validation
- Comprehensive error handling
- Unit and integration tests
- API versioning
- GraphQL option
- OpenAPI/Swagger doc generation

## File Structure

```
Deep_Research/
├── app/
│   ├── backend/
│   │   ├── __init__.py
│   │   └── main.py                 # FastAPI server
│   ├── frontend/
│   │   ├── __init__.py
│   │   └── app.py                  # Streamlit UI
│   ├── docker-compose.yml          # Docker composition
│   ├── Dockerfile                  # Multi-stage builds
│   └── README.md                   # App documentation
├── src/
│   ├── research_agent.py           # Single agent implementation
│   ├── multi_agent_supervisor.py   # Multi-agent coordination
│   ├── state_research.py           # Research state definitions
│   ├── state_multi_agent_supervisor.py  # Supervisor state
│   ├── prompts.py                  # LLM prompts
│   ├── utils.py                    # Helper functions and tools
│   └── __init__.py
├── ARCHITECTURE.md                 # This file
├── QUICKSTART.md                   # Quick start guide
├── pyproject.toml                  # Python dependencies
├── requirements.txt                # Alternative requirements
├── start.sh                        # Unix startup script
├── start.bat                       # Windows startup script
├── .env.example                    # Environment template
└── README.md                       # Main project documentation
```

## Monitoring & Logging

### Logging Setup
- Backend: Python logging (INFO level)
- Frontend: Streamlit logging
- Application logs in console/files

### Metrics to Track
- Research task duration
- Success/failure rates
- API response times
- Agent iterations
- Token usage
- Error types

## Testing

### Manual Testing
1. API endpoint testing with curl
2. Frontend UI testing
3. End-to-end workflow testing

### Automated Testing (Future)
```bash
pytest tests/
```

## Troubleshooting Guide

### Common Issues

**Port Already in Use**:
```bash
# Find process using port
lsof -i :8000
kill -9 <PID>
```

**API Connection Failed**:
- Check backend is running
- Verify port 8000 is accessible
- Check firewall settings

**Research Timeout**:
- Increase timeout in frontend
- Check API rate limits
- Monitor backend resources

**Import Errors**:
```bash
uv sync --force
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Docker Documentation](https://docs.docker.com/)
