#!/usr/bin/env python3
"""Utility script to check and analyze API request logs.

Usage:
    python check_api_logs.py              # Show summary
    python check_api_logs.py --tail 50    # Show last 50 lines
    python check_api_logs.py --grep ERROR # Find error lines
    python check_api_logs.py --summary    # Show detailed summary
"""

import argparse
from pathlib import Path
from collections import Counter

def get_log_file():
    """Get the API log file path."""
    log_dir = Path(__file__).parent / "logs"
    log_file = log_dir / "api_requests.log"
    return log_file

def show_summary():
    """Show summary of API calls."""
    log_file = get_log_file()
    
    if not log_file.exists():
        print("No API log file found yet")
        return
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        print("Log file is empty")
        return
    
    # Count different types of requests
    tavily_requests = sum(1 for line in lines if "[TAVILY] REQUEST" in line)
    tavily_responses = sum(1 for line in lines if "[TAVILY] RESPONSE" in line)
    tavily_errors = sum(1 for line in lines if "[TAVILY] ERROR" in line)
    openrouter_requests = sum(1 for line in lines if "[OPENROUTER] REQUEST" in line)
    openrouter_responses = sum(1 for line in lines if "[OPENROUTER] RESPONSE" in line)
    openrouter_errors = sum(1 for line in lines if "[OPENROUTER] ERROR" in line)
    agent_logs = sum(1 for line in lines if "[AGENT]" in line)
    
    print(f"\n{'='*50}")
    print(f"API Request Summary")
    print(f"{'='*50}")
    print(f"Tavily Requests:      {tavily_requests}")
    print(f"Tavily Responses:     {tavily_responses}")
    print(f"Tavily Errors:        {tavily_errors}")
    print(f"\nOpenRouter Requests:  {openrouter_requests}")
    print(f"OpenRouter Responses: {openrouter_responses}")
    print(f"OpenRouter Errors:    {openrouter_errors}")
    print(f"\nAgent Iterations:     {agent_logs}")
    print(f"\nTotal Lines: {len(lines)}")
    print(f"Log file: {log_file}")
    print(f"{'='*50}\n")

def show_tail(num_lines=30):
    """Show last N lines of the log."""
    log_file = get_log_file()
    
    if not log_file.exists():
        print("No API log file found yet")
        return
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        print("Log file is empty")
        return
    
    print(f"\n{'='*80}")
    print(f"Last {min(num_lines, len(lines))} API Log Entries")
    print(f"{'='*80}\n")
    
    for line in lines[-num_lines:]:
        print(line.rstrip())
    
    print(f"\n{'='*80}\n")

def grep_logs(pattern):
    """Find lines matching a pattern."""
    log_file = get_log_file()
    
    if not log_file.exists():
        print("No API log file found yet")
        return
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    matching = [line for line in lines if pattern.lower() in line.lower()]
    
    print(f"\n{'='*80}")
    print(f"Lines matching '{pattern}' ({len(matching)} found)")
    print(f"{'='*80}\n")
    
    for line in matching:
        print(line.rstrip())
    
    print(f"\n{'='*80}\n")

def show_detailed_summary():
    """Show detailed analysis of API calls."""
    log_file = get_log_file()
    
    if not log_file.exists():
        print("No API log file found yet")
        return
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        print("Log file is empty")
        return
    
    # Count request types
    request_types = []
    for line in lines:
        if "[OPENROUTER] REQUEST" in line:
            # Extract request type
            if "type=" in line:
                start = line.find("type=") + 5
                end = line.find(" |", start)
                if end > start:
                    request_types.append(line[start:end])
    
    print(f"\n{'='*80}")
    print(f"Detailed API Call Summary")
    print(f"{'='*80}\n")
    
    # Show basic stats
    tavily_requests = sum(1 for line in lines if "[TAVILY] REQUEST" in line)
    openrouter_requests = sum(1 for line in lines if "[OPENROUTER] REQUEST" in line)
    
    print(f"Total Tavily Search Requests: {tavily_requests}")
    print(f"Total OpenRouter LLM Requests: {openrouter_requests}")
    
    # Show OpenRouter request type breakdown
    if request_types:
        print(f"\nOpenRouter Requests by Type:")
        type_counter = Counter(request_types)
        for req_type, count in sorted(type_counter.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {req_type}: {count}")
    
    # Check for errors
    errors = [line for line in lines if "ERROR" in line]
    if errors:
        print(f"\nErrors Found: {len(errors)}")
        for line in errors[:5]:  # Show first 5 errors
            print(f"  {line.rstrip()}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    else:
        print(f"\nNo errors found")
    
    print(f"\n{'='*80}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Check and analyze API request logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check_api_logs.py              # Show summary
  python check_api_logs.py --tail 50    # Show last 50 lines
  python check_api_logs.py --grep ERROR # Find error lines
  python check_api_logs.py --summary    # Show detailed summary
        """
    )
    
    parser.add_argument('--tail', type=int, metavar='N', 
                       help='Show last N lines of logs')
    parser.add_argument('--grep', metavar='PATTERN',
                       help='Find lines matching pattern')
    parser.add_argument('--summary', action='store_true',
                       help='Show detailed summary')
    
    args = parser.parse_args()
    
    if args.tail:
        show_tail(args.tail)
    elif args.grep:
        grep_logs(args.grep)
    elif args.summary:
        show_detailed_summary()
    else:
        show_summary()

if __name__ == "__main__":
    main()
