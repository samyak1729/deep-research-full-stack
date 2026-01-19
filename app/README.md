# Deep Research - FastAPI + Streamlit Full Stack App

A fullstack web application for the Deep Research agent system, combining a FastAPI backend with a Streamlit frontend.

## Architecture

```
┌─────────────────────────────────────┐
│     Streamlit Frontend (Port 8501)  │
│  - Research UI                      │
│  - Results visualization            │
│  - Research history                 │
└──────────────┬──────────────────────┘
               │ HTTP
               ↓
┌─────────────────────────────────────┐
│      FastAPI Backend (Port 8000)    │
│  - Research execution               │
│  - Status tracking                  │
│  - Result aggregation               │
└──────────────┬──────────────────────┘
               │
               ↓
      ┌────────────────────┐
      │  Research Agents   │
      │ - Supervisor Agent │
      │ - Researcher Agent │
      └────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Tavily API key

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Set environment variables:
```bash
export OPENAI_API_KEY='your-key'
export TAVILY_API_KEY='your-key'
```

### Running the Application

#### Option 1: Run Both Servers

**Terminal 1 - Start Backend:**
```bash
python app/backend/main.py
```

The API will be available at `http://localhost:8000`
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

**Terminal 2 - Start Frontend:**
```bash
streamlit run app/frontend/app.py
```

The frontend will be available at `http://localhost:8501`

#### Option 2: Using Docker Compose

```bash
docker-compose up
```

Both services will start automatically:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`

## API Documentation

### Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

#### POST /research
Submit a new research task.

**Request:**
```json
{
  "query": "Write a paper on quantum computing...",
  "research_type": "supervisor"
}
```

**Response:**
```json
{
  "research_id": "research_1",
  "status": "pending",
  "query": "Write a paper on quantum computing...",
  "result": null,
  "error": null
}
```

#### GET /research/{research_id}
Get status and results of a research task.

**Response:**
```json
{
  "research_id": "research_1",
  "status": "completed",
  "query": "Write a paper on quantum computing...",
  "result": {
    "compressed_research": "...",
    "raw_notes": ["..."],
    "draft_report": "..."
  },
  "error": null
}
```

#### GET /research
List all research tasks.

**Response:**
```json
[
  { ... research objects ... }
]
```

## Frontend Features

- **New Research**: Submit research queries with type selection
- **Real-time Status**: Watch research progress with live updates
- **Result Tabs**: View summary, raw notes, and full report
- **Download Options**: Export results as JSON or Markdown
- **Research History**: Browse and manage past research tasks
- **Filtering**: Filter by status (pending, running, completed, failed)

## Configuration

### Backend Configuration (app/backend/main.py)

- **API Host**: `0.0.0.0` (all interfaces)
- **API Port**: `8000`
- **CORS**: Enabled for all origins

### Frontend Configuration (app/frontend/app.py)

- **API Base URL**: `http://localhost:8000`
- **Poll Interval**: 2 seconds
- **Max Wait Time**: 300 seconds (5 minutes)

## Development

### Adding New Research Modes

To add a new research agent type:

1. Add to `research_type` options in frontend (`app/frontend/app.py`)
2. Implement handler in backend `run_research()` (`app/backend/main.py`)

Example:
```python
elif research_type == "custom":
    result = await custom_agent.ainvoke({...})
```

### Testing the API

Use the interactive API documentation:
```
http://localhost:8000/docs
```

Or test with curl:
```bash
# Health check
curl http://localhost:8000/health

# Submit research
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "research_type": "supervisor"}'

# Get status
curl http://localhost:8000/research/research_1
```

## Troubleshooting

### API Connection Failed
- Ensure backend is running: `python app/backend/main.py`
- Check if port 8000 is available
- Check firewall settings

### Frontend Not Loading
- Ensure Streamlit is installed: `pip install streamlit`
- Check if port 8501 is available
- Run with: `streamlit run app/frontend/app.py`

### Research Timeout
- Increase `max_wait_time` in `app/frontend/app.py`
- Check backend logs for errors
- Verify OpenAI and Tavily API keys

## File Structure

```
app/
├── backend/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── frontend/
│   ├── __init__.py
│   └── app.py           # Streamlit application
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Docker image definition
└── README.md           # This file
```

## Performance

### Backend
- Handles multiple concurrent research tasks
- Async task processing with background workers
- Configurable research iteration limits

### Frontend
- Real-time polling for status updates
- Lazy loading of result tabs
- Efficient session state management

## License

Same as parent Deep Research project
