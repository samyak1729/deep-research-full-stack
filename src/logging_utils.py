"""Utilities for viewing API logs in Jupyter notebooks and Python scripts."""

from pathlib import Path
from collections import Counter
from typing import Optional, List

def get_log_path() -> Path:
    """Get the API log file path."""
    return Path(__file__).parent.parent / "logs" / "api_requests.log"

def read_logs(limit: Optional[int] = None) -> List[str]:
    """Read all or recent API logs.
    
    Args:
        limit: Maximum number of lines to return (None = all)
    
    Returns:
        List of log lines
    """
    log_path = get_log_path()
    if not log_path.exists():
        return []
    
    with open(log_path, 'r') as f:
        lines = f.readlines()
    
    if limit:
        return lines[-limit:]
    return lines

def print_summary() -> None:
    """Print a summary of API calls."""
    lines = read_logs()
    
    if not lines:
        print("No API logs found yet")
        return
    
    tavily_requests = sum(1 for line in lines if "[TAVILY] REQUEST" in line)
    tavily_responses = sum(1 for line in lines if "[TAVILY] RESPONSE" in line)
    tavily_errors = sum(1 for line in lines if "[TAVILY] ERROR" in line)
    openrouter_requests = sum(1 for line in lines if "[OPENROUTER] REQUEST" in line)
    openrouter_responses = sum(1 for line in lines if "[OPENROUTER] RESPONSE" in line)
    openrouter_errors = sum(1 for line in lines if "[OPENROUTER] ERROR" in line)
    agent_logs = sum(1 for line in lines if "[AGENT]" in line)
    
    print(f"\n{'='*60}")
    print("API Request Summary")
    print(f"{'='*60}")
    print(f"Tavily Requests:      {tavily_requests:3d}")
    print(f"Tavily Responses:     {tavily_responses:3d}")
    print(f"Tavily Errors:        {tavily_errors:3d}")
    print(f"\nOpenRouter Requests:  {openrouter_requests:3d}")
    print(f"OpenRouter Responses: {openrouter_responses:3d}")
    print(f"OpenRouter Errors:    {openrouter_errors:3d}")
    print(f"\nAgent Iterations:     {agent_logs:3d}")
    print(f"\nTotal Lines:          {len(lines):3d}")
    print(f"{'='*60}\n")

def print_last_n(n: int = 20) -> None:
    """Print the last N log entries.
    
    Args:
        n: Number of lines to print
    """
    lines = read_logs(limit=n)
    
    if not lines:
        print("No API logs found")
        return
    
    print(f"\n{'='*80}")
    print(f"Last {len(lines)} API Log Entries")
    print(f"{'='*80}\n")
    
    for line in lines:
        print(line.rstrip())
    
    print(f"\n{'='*80}\n")

def print_requests(request_type: Optional[str] = None) -> None:
    """Print all requests of a specific type.
    
    Args:
        request_type: Type to filter by ('TAVILY', 'OPENROUTER', 'AGENT', or None for all)
    """
    lines = read_logs()
    
    if not lines:
        print("No API logs found")
        return
    
    if request_type:
        filtered = [line for line in lines if f"[{request_type}]" in line and "REQUEST" in line]
    else:
        filtered = [line for line in lines if "REQUEST" in line]
    
    print(f"\n{'='*80}")
    print(f"API Requests ({len(filtered)} total)")
    print(f"{'='*80}\n")
    
    for line in filtered:
        print(line.rstrip())
    
    print(f"\n{'='*80}\n")

def print_errors() -> None:
    """Print all errors from logs."""
    lines = read_logs()
    
    if not lines:
        print("No API logs found")
        return
    
    errors = [line for line in lines if "ERROR" in line]
    
    if not errors:
        print("No errors found in logs")
        return
    
    print(f"\n{'='*80}")
    print(f"API Errors ({len(errors)} total)")
    print(f"{'='*80}\n")
    
    for line in errors:
        print(line.rstrip())
    
    print(f"\n{'='*80}\n")

def get_request_type_breakdown() -> dict:
    """Get breakdown of OpenRouter requests by type.
    
    Returns:
        Dictionary with request type counts
    """
    lines = read_logs()
    request_types = []
    
    for line in lines:
        if "[OPENROUTER] REQUEST" in line and "type=" in line:
            start = line.find("type=") + 5
            end = line.find(" |", start)
            if end > start:
                request_types.append(line[start:end])
    
    return dict(Counter(request_types))

def detect_loop(threshold: int = 5) -> bool:
    """Detect if agent appears to be in a loop.
    
    Checks for:
    - Same searches repeated
    - High iteration count
    - Similar response patterns
    
    Args:
        threshold: Iteration threshold to flag as potential loop
    
    Returns:
        True if potential loop detected
    """
    lines = read_logs()
    
    if not lines:
        return False
    
    # Check iteration count
    agent_logs = [line for line in lines if "[AGENT]" in line]
    if agent_logs:
        last_agent_log = agent_logs[-1]
        # Extract iteration number
        if "iteration=" in last_agent_log:
            start = last_agent_log.find("iteration=") + 10
            end = last_agent_log.find(" |", start)
            if end > start:
                try:
                    iteration = int(last_agent_log[start:end])
                    if iteration >= threshold:
                        return True
                except ValueError:
                    pass
    
    # Check for duplicate searches
    searches = []
    for line in lines:
        if "[TAVILY] REQUEST" in line and "query=" in line:
            start = line.find("query='") + 7
            end = line.find("'", start)
            if end > start:
                searches.append(line[start:end])
    
    # If any search appears more than once, might be looping
    if searches and len(searches) != len(set(searches)):
        return True
    
    return False

def get_session_summary() -> dict:
    """Get comprehensive summary of the current session.
    
    Returns:
        Dictionary with session statistics
    """
    lines = read_logs()
    
    if not lines:
        return {}
    
    tavily_requests = sum(1 for line in lines if "[TAVILY] REQUEST" in line)
    tavily_responses = sum(1 for line in lines if "[TAVILY] RESPONSE" in line)
    openrouter_requests = sum(1 for line in lines if "[OPENROUTER] REQUEST" in line)
    openrouter_responses = sum(1 for line in lines if "[OPENROUTER] RESPONSE" in line)
    errors = sum(1 for line in lines if "ERROR" in line)
    
    request_types = get_request_type_breakdown()
    
    return {
        "total_lines": len(lines),
        "tavily_requests": tavily_requests,
        "tavily_responses": tavily_responses,
        "openrouter_requests": openrouter_requests,
        "openrouter_responses": openrouter_responses,
        "errors": errors,
        "request_type_breakdown": request_types,
        "potential_loop": detect_loop(),
        "log_file": str(get_log_path())
    }

def jupyter_display_summary() -> None:
    """Display summary in Jupyter notebook with formatting."""
    try:
        from IPython.display import HTML, display
        
        summary = get_session_summary()
        
        if not summary:
            display(HTML("<p>No API logs found yet</p>"))
            return
        
        html = f"""
        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px; font-family: monospace;">
            <h3>API Request Summary</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 5px;"><b>Metric</b></td>
                    <td style="padding: 5px;"><b>Count</b></td>
                </tr>
                <tr>
                    <td style="padding: 5px;">Tavily Requests</td>
                    <td style="padding: 5px;">{summary['tavily_requests']}</td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 5px;">Tavily Responses</td>
                    <td style="padding: 5px;">{summary['tavily_responses']}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;">OpenRouter Requests</td>
                    <td style="padding: 5px;">{summary['openrouter_requests']}</td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 5px;">OpenRouter Responses</td>
                    <td style="padding: 5px;">{summary['openrouter_responses']}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;">Errors</td>
                    <td style="padding: 5px;">{summary['errors']}</td>
                </tr>
            </table>
            
            <h4>OpenRouter Requests by Type:</h4>
            <ul>
        """
        
        for req_type, count in sorted(summary['request_type_breakdown'].items(), 
                                     key=lambda x: x[1], reverse=True):
            html += f"<li>{req_type}: {count}</li>"
        
        loop_status = "🔴 POTENTIAL LOOP DETECTED!" if summary['potential_loop'] else "✅ No loop detected"
        html += f"""
            </ul>
            <p><b>Loop Status:</b> {loop_status}</p>
            <p style="font-size: 0.9em; color: #666;">Log file: {summary['log_file']}</p>
        </div>
        """
        
        display(HTML(html))
    except ImportError:
        # Not in Jupyter, fall back to text
        print_summary()

# For use in Jupyter notebooks
if __name__ == "__main__":
    print_summary()
