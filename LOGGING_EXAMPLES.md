# API Logging Examples

This document shows practical examples of using the API logging system to debug and monitor your agent.

## Quick Start

After running a research task, check the API logs:

```bash
# Summary view
python3 check_api_logs.py

# See last 30 lines
python3 check_api_logs.py --tail 30

# Search for errors
python3 check_api_logs.py --grep ERROR

# Detailed analysis
python3 check_api_logs.py --summary
```

## Scenario 1: Agent Sent Too Many Requests (Your Case)

You mentioned the agent sent ~10 requests to OpenRouter but you weren't sure what they were.

### Check what requests were made

```bash
python3 check_api_logs.py --tail 50 | grep "OPENROUTER.*REQUEST"
```

Output:
```
[OPENROUTER] REQUEST | type=research | model=xiaomi/mimo-v2-flash:free | num_messages=3 | max_tokens=None | first_msg='What are advances in...'
[OPENROUTER] REQUEST | type=summarization | model=xiaomi/mimo-v2-flash:free | num_messages=1 | max_tokens=None | first_msg='Summarize this webpage...'
[OPENROUTER] REQUEST | type=research | model=xiaomi/mimo-v2-flash:free | num_messages=4 | max_tokens=None | first_msg='Now I have found that...'
...
```

### See what type of requests dominated

```bash
python3 check_api_logs.py --summary
```

Output shows:
```
OpenRouter Requests by Type:
  - research: 7
  - summarization: 2
  - compression: 1
```

## Scenario 2: Detecting Agent Loops

If you suspect the agent is looping, check for repeated patterns:

### Check if same search queries are repeated

```bash
python3 check_api_logs.py --tail 100 | grep "TAVILY.*REQUEST"
```

Look for duplicate query patterns like:
```
[TAVILY] REQUEST | query='quantum computing' | max_results=3 | topic=general
[TAVILY] REQUEST | query='AI research trends' | max_results=3 | topic=general
[TAVILY] REQUEST | query='quantum computing' | max_results=3 | topic=general  # DUPLICATE!
```

### Check agent iterations

```bash
python3 check_api_logs.py --tail 50 | grep "AGENT"
```

If iterations keep increasing without progress:
```
[AGENT] RESEARCHER | iteration=1 | action=called 2 tools
[AGENT] RESEARCHER | iteration=2 | action=called 2 tools
[AGENT] RESEARCHER | iteration=3 | action=called 2 tools
[AGENT] RESEARCHER | iteration=4 | action=called 2 tools
[AGENT] RESEARCHER | iteration=5 | action=called 2 tools
[AGENT] RESEARCHER | iteration=6 | action=called 2 tools
[AGENT] RESEARCHER | iteration=7 | action=called 2 tools
[AGENT] RESEARCHER | iteration=8 | action=called 2 tools
[AGENT] RESEARCHER | iteration=9 | action=called 2 tools
[AGENT] RESEARCHER | iteration=10 | action=called 2 tools  # Loop detected!
[AGENT] RESEARCHER | iteration=11 | action=called 2 tools
[AGENT] RESEARCHER | iteration=12 | action=called 2 tools
[AGENT] RESEARCHER | iteration=13 | action=called 2 tools
[AGENT] RESEARCHER | iteration=14 | action=called 2 tools
[AGENT] RESEARCHER | iteration=15 | action=called 2 tools  # Max iterations hit
```

## Scenario 3: Analyzing Response Content

See what the first few words of each response are:

```bash
python3 check_api_logs.py --tail 30 | grep "OPENROUTER.*RESPONSE"
```

Output:
```
[OPENROUTER] RESPONSE | type=research | model=xiaomi/mimo-v2-flash:free | response='Based on the search results, I found...'
[OPENROUTER] RESPONSE | type=research | model=xiaomi/mimo-v2-flash:free | response='The key findings suggest that AI is...'
[OPENROUTER] RESPONSE | type=compression | model=xiaomi/mimo-v2-flash:free | response='Summary: The research revealed that quantum...'
```

If you see similar responses repeating, the agent might be looping on the same content.

## Scenario 4: Debugging Tavily Searches

Check which searches are running and how many results each returned:

```bash
python3 check_api_logs.py --tail 30 | grep "TAVILY"
```

Output:
```
[TAVILY] REQUEST | query='quantum computing advances 2025' | max_results=3 | topic=general
[TAVILY] RESPONSE | query='quantum computing advances 2025' | results_count=3 | first_result='Google's Quantum Breakthrough...'
[TAVILY] REQUEST | query='AI in healthcare' | max_results=3 | topic=general
[TAVILY] RESPONSE | query='AI in healthcare' | results_count=5 | first_result='Medical AI Transforms Diagnosis...'
```

If a search returns 0 results, it's logged as:
```
[TAVILY] RESPONSE | query='obscure topic' | results_count=0 | first_result=''
```

## Scenario 5: Checking for API Errors

```bash
python3 check_api_logs.py --grep ERROR
```

Output if there are errors:
```
[TAVILY] ERROR | query='test' | error=Connection timeout
[OPENROUTER] ERROR | type=research | model=xiaomi/mimo-v2-flash:free | error=Rate limit exceeded
```

## Scenario 6: Real-time Monitoring

While running a research task in one terminal, monitor logs in another:

```bash
# Terminal 1: Run the backend
cd /home/samyak/Deep_Research
source .venv/bin/activate
python app/backend/main.py

# Terminal 2: Monitor logs (updates every 2 seconds)
cd /home/samyak/Deep_Research
watch -n 2 "python3 check_api_logs.py --tail 15"
```

Or use continuous tail:
```bash
tail -f logs/api_requests.log
```

## Scenario 7: After Task Completion

Once a research task finishes, the backend automatically prints the summary:

```
=== API Request Summary ===
Tavily Requests:      5
Tavily Responses:     5
OpenRouter Requests:  8
OpenRouter Responses: 8
Errors:               0
Log file: /home/samyak/Deep_Research/logs/api_requests.log
```

You'll also see this in the backend logs.

## Scenario 8: Comparing Multiple Runs

Run research twice and compare the logs:

```bash
# Clear old logs
rm logs/api_requests.log

# Run first task
python app/backend/main.py  # Start backend
# Submit research through frontend

# Check results
python3 check_api_logs.py

# Rename logs to keep them
mv logs/api_requests.log logs/api_requests_run1.log

# Repeat with second task
python3 check_api_logs.py

# Compare
echo "=== Run 1 ===" && grep "REQUEST" logs/api_requests_run1.log | wc -l
echo "=== Run 2 ===" && grep "REQUEST" logs/api_requests.log | wc -l
```

## Scenario 9: Full Request-Response Pairs

See complete request-response sequences:

```bash
python3 check_api_logs.py --tail 50
```

Look for patterns like:
```
[OPENROUTER] REQUEST | type=research | model=xiaomi/mimo-v2-flash:free | num_messages=3 | max_tokens=None | first_msg='What are...'
[OPENROUTER] RESPONSE | type=research | model=xiaomi/mimo-v2-flash:free | response='I should search for...'
[AGENT] RESEARCHER | iteration=1 | action=called 2 tools
[TAVILY] REQUEST | query='topic A' | max_results=3 | topic=general
[TAVILY] RESPONSE | query='topic A' | results_count=3 | first_result='Title...'
[OPENROUTER] REQUEST | type=summarization | model=xiaomi/mimo-v2-flash:free | num_messages=1 | max_tokens=None | first_msg='Summarize...'
[OPENROUTER] RESPONSE | type=summarization | model=xiaomi/mimo-v2-flash:free | response='<summary>Key finding...'
```

This shows the complete flow of one agent iteration.

## Scenario 10: Finding Specific Information

### Find all research-type LLM calls
```bash
python3 check_api_logs.py --grep "type=research"
```

### Find all summarization calls
```bash
python3 check_api_logs.py --grep "type=summarization"
```

### Find searches about a specific topic
```bash
python3 check_api_logs.py --grep "quantum"
```

### Find responses that contain specific words
```bash
python3 check_api_logs.py --grep "important" | head -20
```

## Tips for Effective Monitoring

1. **Set up continuous monitoring while testing:**
   ```bash
   watch -n 1 "python3 check_api_logs.py --tail 10"
   ```

2. **Create a comparison baseline:**
   ```bash
   python3 check_api_logs.py --summary > baseline.txt
   # ... run experiment ...
   python3 check_api_logs.py --summary > after.txt
   diff baseline.txt after.txt
   ```

3. **Check for rate limiting by watching response times:**
   Timestamps in logs show response timing - if there are long gaps, you might be hitting rate limits.

4. **Archive logs between test runs:**
   ```bash
   cp logs/api_requests.log logs/api_requests_$(date +%Y%m%d_%H%M%S).log
   ```

5. **Correlate with backend logs:**
   ```bash
   tail -f app.log | tee -a logs/full_session.log &
   tail -f logs/api_requests.log | tee -a logs/full_session.log
   ```

## Understanding Request Counts

Expected request counts for a simple research task:
- **Tavily Requests**: 3-5 (searches for different aspects)
- **OpenRouter Requests**: 5-10 (research, summarization, compression)
- **Total**: ~10-15 requests

If you see significantly more (e.g., 20-30), the agent may be:
- Looping on the same content
- Over-summarizing
- Making too many refinement passes

Use the logging to identify which request type is causing the excess.
