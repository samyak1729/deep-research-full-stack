"""Request/Response logging for external APIs (Tavily and OpenRouter).

This module provides centralized logging for all external API calls to help
track agent behavior, detect loops, and debug issues.
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional
from pathlib import Path

# Configure logging
logger = logging.getLogger("api_requests")

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Create file handler for API request logs
log_file = LOGS_DIR / "api_requests.log"
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create console handler for real-time logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

logger.setLevel(logging.INFO)


def log_tavily_request(query: str, max_results: int = 3, topic: str = "general"):
    """Log a Tavily search request.
    
    Args:
        query: Search query
        max_results: Maximum results requested
        topic: Topic filter
    """
    logger.info(
        f"[TAVILY] REQUEST | query='{query}' | max_results={max_results} | topic={topic}"
    )


def log_tavily_response(query: str, num_results: int, first_result: Optional[dict] = None):
    """Log a Tavily search response.
    
    Args:
        query: Original search query
        num_results: Number of results returned
        first_result: First result dict (to extract title/content snippet)
    """
    snippet = ""
    if first_result and "title" in first_result:
        snippet = f" | first_result='{first_result['title'][:80]}...'"
    
    logger.info(
        f"[TAVILY] RESPONSE | query='{query}' | results_count={num_results}{snippet}"
    )


def log_openrouter_request(
    model: str,
    messages: list,
    max_tokens: Optional[int] = None,
    request_type: str = "general"
):
    """Log an OpenRouter API request.
    
    Args:
        model: Model ID being called
        messages: List of message dicts
        max_tokens: Max tokens requested
        request_type: Type of request (e.g., 'research', 'summarization', 'refinement')
    """
    # Extract first user message for context
    user_message = ""
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str):
                user_message = content[:120]  # First 120 chars
            break
    
    logger.info(
        f"[OPENROUTER] REQUEST | type={request_type} | model={model} | "
        f"num_messages={len(messages)} | max_tokens={max_tokens} | "
        f"first_msg='{user_message}...'"
    )


def log_openrouter_response(
    model: str,
    response_content: str,
    request_type: str = "general",
    usage: Optional[dict] = None
):
    """Log an OpenRouter API response.
    
    Args:
        model: Model ID that was called
        response_content: Response content from the model
        request_type: Type of request
        usage: Token usage dict with 'prompt_tokens' and 'completion_tokens'
    """
    # Get first ~100 characters of response
    response_snippet = response_content[:100] if response_content else ""
    
    tokens_info = ""
    if usage:
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        tokens_info = f" | tokens=(prompt={prompt_tokens}, completion={completion_tokens})"
    
    logger.info(
        f"[OPENROUTER] RESPONSE | type={request_type} | model={model} | "
        f"response='{response_snippet}...'{tokens_info}"
    )


def log_tavily_error(query: str, error: str):
    """Log a Tavily API error.
    
    Args:
        query: Search query that failed
        error: Error message
    """
    logger.error(f"[TAVILY] ERROR | query='{query}' | error={error}")


def log_openrouter_error(model: str, request_type: str, error: str):
    """Log an OpenRouter API error.
    
    Args:
        model: Model being called
        request_type: Type of request
        error: Error message
    """
    logger.error(f"[OPENROUTER] ERROR | type={request_type} | model={model} | error={error}")


def log_agent_iteration(agent_type: str, iteration: int, action: str):
    """Log agent iteration progress.
    
    Args:
        agent_type: Type of agent ('researcher' or 'supervisor')
        iteration: Iteration number
        action: Action being taken
    """
    logger.info(f"[AGENT] {agent_type.upper()} | iteration={iteration} | action={action}")


def get_api_log_summary() -> str:
    """Get a summary of API calls from the current log file.
    
    Returns:
        String summary of API calls
    """
    if not log_file.exists():
        return "No API log file found yet"
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # Count different types of requests
    tavily_requests = sum(1 for line in lines if "[TAVILY] REQUEST" in line)
    tavily_responses = sum(1 for line in lines if "[TAVILY] RESPONSE" in line)
    openrouter_requests = sum(1 for line in lines if "[OPENROUTER] REQUEST" in line)
    openrouter_responses = sum(1 for line in lines if "[OPENROUTER] RESPONSE" in line)
    errors = sum(1 for line in lines if "ERROR" in line)
    
    summary = f"""
=== API Request Summary ===
Tavily Requests:      {tavily_requests}
Tavily Responses:     {tavily_responses}
OpenRouter Requests:  {openrouter_requests}
OpenRouter Responses: {openrouter_responses}
Errors:               {errors}
Log file: {log_file}
    """
    return summary


def print_api_logs_tail(num_lines: int = 30):
    """Print the last N lines of API logs to console.
    
    Args:
        num_lines: Number of lines to print
    """
    if not log_file.exists():
        print("No API log file found yet")
        return
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    print(f"\n=== Last {num_lines} API Log Entries ===")
    for line in lines[-num_lines:]:
        print(line.rstrip())
