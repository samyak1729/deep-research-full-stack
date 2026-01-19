# Quick Start Guide - Deep Research Fullstack App

Get the FastAPI + Streamlit app running in 5 minutes.

## Prerequisites

- Python 3.11+
- OpenAI API key (from https://platform.openai.com/api-keys)
- Tavily API key (from https://tavily.com)

## Option 1: Local Development (Recommended for Development)

### 1. Setup

```bash
# Install dependencies
uv sync

# Create .env file with your keys
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Start Backend

```bash
python app/backend/main.py
```

Backend runs at `http://localhost:8000`
- Check health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

### 3. Start Frontend (New Terminal)

```bash
streamlit run app/frontend/app.py
```

Frontend runs at `http://localhost:8501`

### 4. Use the App

1. Open browser to `http://localhost:8501`
2. Enter research query
3. Select research type (Supervisor or Single Agent)
4. Click "Start Research"
5. Wait for results

## Option 2: Docker Compose (Recommended for Production)

### 1. Setup

```bash
# Copy and edit .env file
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Run

```bash
docker-compose up
```

Services will be available at:
- Frontend: `http://localhost:8501`
- Backend: `http://localhost:8000`

### 3. Stop

```bash
docker-compose down
```

## Testing the API

```bash
# Check health
curl http://localhost:8000/health

# Submit research
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "quantum computing", "research_type": "supervisor"}'

# Get status
curl http://localhost:8000/research/research_1

# List all
curl http://localhost:8000/research
```

## Key Files

- `app/backend/main.py` - FastAPI server
- `app/frontend/app.py` - Streamlit UI
- `docker-compose.yml` - Docker Compose config
- `Dockerfile` - Multi-stage Docker builds
- `pyproject.toml` - Python dependencies

## Troubleshooting

**Port already in use:**
```bash
# Change port (change 8000 to another port)
python app/backend/main.py --port 8001
```

**Import errors:**
```bash
# Reinstall dependencies
uv sync --force
```

**API not responding:**
```bash
# Check if backend is running and healthy
curl http://localhost:8000/health
```

## Next Steps

- Customize frontend styling in `app/frontend/app.py`
- Extend backend with new research agent types
- Deploy to cloud (AWS, GCP, Heroku, etc.)
- Add authentication and user management
- Set up monitoring and logging

See `app/README.md` for detailed documentation.
