# OpenRouter Configuration

This project uses OpenRouter models exclusively with `ChatOpenAI` via OpenRouter's API endpoint.

## Setup

### 1. Get an OpenRouter API Key
- Sign up at https://openrouter.ai
- Get your API key from the dashboard

### 2. Configure .env
```bash
cp .env.example .env
```

Add your OpenRouter API key:
```env
OPENROUTER_API_KEY=sk-or-...
TAVILY_API_KEY=tvly-...
```

### 3. Run the project
```bash
uv run python app/backend/main.py  # Terminal 1
streamlit run app/frontend/app.py  # Terminal 2
```

## Current Model

**`xiaomi/mimo-v2-flash:free`** - Xiaomi's free flash model on OpenRouter

The system uses `ChatOpenAI` configured with:
- Base URL: `https://openrouter.ai/api/v1`
- API Key: From `OPENROUTER_API_KEY` environment variable

## Switching Models

To use a different OpenRouter model, update the `MODEL_ID` constant in these files:
- `src/utils.py`
- `src/research_agent.py`
- `src/research_agent_scope.py`
- `src/research_agent_full.py`
- `src/multi_agent_supervisor.py`

Example - to use Claude 3.5 Sonnet:
```python
MODEL_ID = "anthropic/claude-3-5-sonnet-20241022"
```

Other popular options:
- `anthropic/claude-3-5-opus-20241022` - Highest quality
- `meta-llama/llama-3.1-405b` - Open source, powerful
- `openai/gpt-4-turbo` - OpenAI GPT-4 via OpenRouter
- `mistral/mistral-7b-instruct` - Lightweight, fast

## Implementation Details

- All model instances use `ChatOpenAI` from `langchain_openai`
- API key is retrieved from the `OPENROUTER_API_KEY` environment variable
- The system validates that the key is set on startup
- Models are configured with OpenRouter's API endpoint for compatibility

## Files Modified

- `.env.example` - Updated to only require `OPENROUTER_API_KEY`
- `src/utils.py` - Uses ChatOpenAI with OpenRouter configuration
- `src/research_agent.py` - Uses ChatOpenAI with OpenRouter configuration
- `src/research_agent_scope.py` - Uses ChatOpenAI with OpenRouter configuration
- `src/research_agent_full.py` - Uses ChatOpenAI with OpenRouter configuration
- `src/multi_agent_supervisor.py` - Uses ChatOpenAI with OpenRouter configuration
