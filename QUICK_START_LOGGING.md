# Quick Start: API Request Logging

## What Was Added

A complete request/response logging system for Tavily and OpenRouter API calls to help you:
- See exactly what requests your agent is making
- Detect if the agent is looping
- Debug API issues
- Track agent behavior

## Files Created

1. **src/request_logger.py** - Core logging module
2. **src/logging_utils.py** - Python/Jupyter utilities
3. **check_api_logs.py** - Command-line tool for viewing logs
4. **API_LOGGING.md** - Detailed documentation
5. **LOGGING_EXAMPLES.md** - Practical examples
6. **.gitignore** - Excludes logs from git

## Files Modified

1. **src/utils.py** - Added logging to Tavily and OpenRouter calls
2. **src/research_agent.py** - Added logging to research iterations
3. **src/multi_agent_supervisor.py** - Added logging to supervisor iterations
4. **app/backend/main.py** - Added summary output after research completes

## Usage: The Fastest Way

After running research, see what happened:

```bash
python3 check_api_logs.py
```

Output:
```
==================================================
API Request Summary
==================================================
Tavily Requests:      5
Tavily Responses:     5
OpenRouter Requests:  10
OpenRouter Responses: 10
Errors:               0
Agent Iterations:     15
Total Lines: 70
==================================================
```

## Common Commands

### See the last 30 lines
```bash
python3 check_api_logs.py --tail 30
```

### Find errors
```bash
python3 check_api_logs.py --grep ERROR
```

### Detailed breakdown by request type
```bash
python3 check_api_logs.py --summary
```

### Search for specific patterns
```bash
python3 check_api_logs.py --grep "quantum"
```

## In Python / Jupyter

```python
from src.logging_utils import print_summary, print_last_n, detect_loop

# Quick summary
print_summary()

# View last 20 entries
print_last_n(20)

# Check for loops
if detect_loop():
    print("⚠️ Potential loop detected!")
```

Or in Jupyter for pretty HTML display:
```python
from src.logging_utils import jupyter_display_summary
jupyter_display_summary()
```

## What Gets Logged

### Tavily Searches
```
[TAVILY] REQUEST | query='search term' | max_results=3 | topic=general
[TAVILY] RESPONSE | query='search term' | results_count=3 | first_result='Title...'
```

### OpenRouter LLM Calls
```
[OPENROUTER] REQUEST | type=research | model=xiaomi/mimo-v2-flash:free | num_messages=3 | max_tokens=None | first_msg='Hello...'
[OPENROUTER] RESPONSE | type=research | model=xiaomi/mimo-v2-flash:free | response='I found that...'
```

### Agent Progress
```
[AGENT] RESEARCHER | iteration=1 | action=called 2 tools
[AGENT] SUPERVISOR | iteration=2 | action=called 1 tools
```

### Errors
```
[TAVILY] ERROR | query='search' | error=Connection timeout
[OPENROUTER] ERROR | type=research | model=... | error=Rate limit
```

## Finding Your 10 Requests

Remember you mentioned the agent sent 10 OpenRouter requests? Now you can see exactly what they were:

```bash
python3 check_api_logs.py --tail 50 | grep "OPENROUTER.*REQUEST"
```

This shows you each request with the request type and first words of the prompt.

## Detecting Loops

To see if the agent is stuck:

1. Check iteration count
   ```bash
   python3 check_api_logs.py --grep "AGENT.*iteration"
   ```

2. Look for repeated searches
   ```bash
   python3 check_api_logs.py --grep "TAVILY.*REQUEST" | sort | uniq -d
   ```

3. Check if same response patterns appear
   ```bash
   python3 check_api_logs.py --tail 50 | grep "OPENROUTER.*RESPONSE"
   ```

Or use the Python function:
```python
from src.logging_utils import detect_loop
if detect_loop(threshold=10):
    print("Loop detected - agent exceeded 10 iterations")
```

## Real-Time Monitoring

While running a task, watch logs in real-time:

```bash
# Terminal 1: Run research
python app/backend/main.py

# Terminal 2: Watch logs (updates every 2 seconds)
watch -n 2 "python3 check_api_logs.py --tail 10"
```

Or continuous tail:
```bash
tail -f logs/api_requests.log
```

## Log Location

All logs are saved to:
```
logs/api_requests.log
```

This directory is created automatically and is in .gitignore (won't be committed).

## Output Format

Each log line includes:
- **Timestamp** - When the request/response happened
- **Type** - `[TAVILY]`, `[OPENROUTER]`, or `[AGENT]`
- **Action** - REQUEST, RESPONSE, or ERROR
- **Details** - Query, response snippet, model, iteration count, etc.

First 100 characters of prompts and responses are logged to keep file sizes manageable.

## Next Steps

1. Run a research task
2. Check what happened:
   ```bash
   python3 check_api_logs.py --summary
   ```
3. If you see unexpected behavior, search the logs:
   ```bash
   python3 check_api_logs.py --tail 100 | less
   ```
4. For detailed analysis, see LOGGING_EXAMPLES.md

## Troubleshooting

### "No API log file found yet"
- The logs are created on first API call
- Run a research task first

### Too many requests
- Normal tasks make 10-15 requests
- 20+ might indicate looping
- Check iteration count and search patterns

### Want to clear logs
```bash
rm logs/api_requests.log
```

## For More Details

- **API_LOGGING.md** - Full documentation
- **LOGGING_EXAMPLES.md** - Practical examples for different scenarios
- **src/logging_utils.py** - Python API for programmatic access
- **check_api_logs.py** - CLI tool source code

---

**That's it!** You now have full visibility into what your agent is doing. 🎯
