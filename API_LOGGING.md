# API Request Logging

This document describes the request/response logging system for Tavily and OpenRouter API calls, which helps track agent behavior and detect potential loops.

## Overview

The logging system automatically tracks:
- **Tavily API requests** - Search queries, parameters, and response counts
- **OpenRouter API requests** - LLM calls, request types, and response snippets
- **Agent iterations** - What the agent is doing at each step
- **Errors** - Any API failures

All logs are written to `logs/api_requests.log` in the project root.

## Log File Location

```
logs/api_requests.log
```

The logs directory is created automatically on first use.

## Log Format

### Tavily Requests
```
[TAVILY] REQUEST | query='search query' | max_results=3 | topic=general
[TAVILY] RESPONSE | query='search query' | results_count=5 | first_result='Result Title...'
[TAVILY] ERROR | query='search query' | error=error message
```

### OpenRouter Requests
```
[OPENROUTER] REQUEST | type=research | model=xiaomi/mimo-v2-flash:free | num_messages=5 | max_tokens=None | first_msg='Hello...'
[OPENROUTER] RESPONSE | type=research | model=xiaomi/mimo-v2-flash:free | response='The answer is...'
[OPENROUTER] ERROR | type=research | model=xiaomi/mimo-v2-flash:free | error=error message
```

Request types include:
- `research` - Main research agent decision-making
- `summarization` - Webpage content summarization
- `refinement` - Draft report refinement
- `compression` - Research findings compression
- `supervisor` - Supervisor agent coordination

### Agent Iterations
```
[AGENT] RESEARCHER | iteration=3 | action=called 2 tools
[AGENT] SUPERVISOR | iteration=2 | action=called 1 tools
```

## Checking Logs

### Quick Summary
```bash
python3 check_api_logs.py
```

Shows counts of all request/response types:
```
==================================================
API Request Summary
==================================================
Tavily Requests:      10
Tavily Responses:     10
Tavily Errors:        0

OpenRouter Requests:  25
OpenRouter Responses: 25
OpenRouter Errors:    0

Agent Iterations:     15

Total Lines: 85
```

### View Last N Lines
```bash
python3 check_api_logs.py --tail 30
```

Shows the last 30 log entries in real-time format.

### Search for Patterns
```bash
python3 check_api_logs.py --grep ERROR
```

Find all lines containing a pattern (case-insensitive).

### Detailed Analysis
```bash
python3 check_api_logs.py --summary
```

Shows:
- Total requests by service
- Breakdown of OpenRouter requests by type
- Error summary
- Example errors (if any)

## Detecting Loops

To detect if the agent is stuck in a loop, check:

1. **Request frequency** - Are the same queries being repeated?
   ```bash
   python3 check_api_logs.py --tail 50 | grep "TAVILY.*REQUEST"
   ```

2. **Total iterations** - Check if iterations are exceeding expectations
   ```bash
   python3 check_api_logs.py --summary
   ```

3. **Error patterns** - Look for recurring errors
   ```bash
   python3 check_api_logs.py --grep ERROR
   ```

4. **Response content** - Check if responses are similar (stuck on same content)
   ```bash
   python3 check_api_logs.py --tail 100 | grep "OPENROUTER.*RESPONSE"
   ```

## Example Log Output

After running a research task, you'll see logs like:

```
2026-01-19 09:25:42 - api_requests - INFO - [OPENROUTER] REQUEST | type=supervisor | model=xiaomi/mimo-v2-flash:free | num_messages=3 | max_tokens=None | first_msg='What are recent advances...'
2026-01-19 09:25:45 - api_requests - INFO - [OPENROUTER] RESPONSE | type=supervisor | model=xiaomi/mimo-v2-flash:free | response='I should research the following areas...'
2026-01-19 09:25:45 - api_requests - INFO - [AGENT] SUPERVISOR | iteration=1 | action=called 2 tools
2026-01-19 09:25:46 - api_requests - INFO - [TAVILY] REQUEST | query='quantum computing 2025' | max_results=3 | topic=general
2026-01-19 09:25:48 - api_requests - INFO - [TAVILY] RESPONSE | query='quantum computing 2025' | results_count=3 | first_result='Google's Latest Quantum Breakthrough...'
2026-01-19 09:25:49 - api_requests - INFO - [OPENROUTER] REQUEST | type=research | model=xiaomi/mimo-v2-flash:free | num_messages=4 | max_tokens=None | first_msg='Based on this search result...'
2026-01-19 09:25:51 - api_requests - INFO - [OPENROUTER] RESPONSE | type=research | model=xiaomi/mimo-v2-flash:free | response='The search results show that quantum computing...'
```

## Integration Points

The logging is automatically integrated at these points:

### In `src/utils.py`:
- `tavily_search_multiple()` - Logs all Tavily searches
- `summarize_webpage_content()` - Logs summarization requests
- `refine_draft_report()` - Logs report refinement requests

### In `src/research_agent.py`:
- `llm_call()` - Logs research agent LLM calls
- `compress_research()` - Logs research compression calls

### In `src/multi_agent_supervisor.py`:
- `supervisor()` - Logs supervisor LLM calls

### In `app/backend/main.py`:
- `run_research()` - Prints summary after task completion

## Monitoring During Development

For real-time monitoring while testing:

```bash
# In one terminal, run the research
python3 app/backend/main.py

# In another terminal, continuously check logs
watch -n 2 "python3 check_api_logs.py --tail 20"
```

Or use `tail` directly:
```bash
tail -f logs/api_requests.log
```

## Troubleshooting

### Too many OpenRouter requests
- Check if agent is stuck in a loop with `python3 check_api_logs.py --summary`
- Look for repeated queries with `python3 check_api_logs.py --grep "research.*REQUEST"`
- Review the first few words of responses to see if they're similar

### Unexpected Tavily searches
- Each search is logged with the exact query - check what's being searched
- Look for duplicate queries that might indicate looping

### API errors
- All errors are logged with full context
- Use `python3 check_api_logs.py --grep ERROR` to find issues
- Check the error message for rate limits, authentication issues, etc.

## Customization

To customize logging behavior, edit `src/request_logger.py`:

- Change log level: Modify `logger.setLevel()`
- Change log file location: Modify `LOGS_DIR` path
- Add new log types: Create new logging functions
- Modify log format: Edit the formatter

## Performance Impact

The logging system has minimal performance overhead:
- Log writes are synchronous but very fast
- Only ~100 bytes per request logged
- No impact on API response times
- Can handle 100+ requests per task without slowdown

## Privacy Considerations

Note that logs contain:
- ✓ Search queries
- ✓ First words of LLM responses
- ✗ Full response content (only first 100 chars)
- ✗ Raw webpage content

Keep the `logs/` directory private if handling sensitive research queries.
