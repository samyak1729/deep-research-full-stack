"""Streamlit frontend for Deep Research application.

Provides user interface for submitting research queries and viewing results.
"""

import os
from pathlib import Path

# Load environment variables from .env file
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

import streamlit as st
import requests
import time
from datetime import datetime
import json

# ===== PAGE CONFIGURATION =====

st.set_page_config(
    page_title="Deep Research",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== STYLES =====

st.markdown("""
<style>
    .research-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .status-badge {
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    .status-pending {
        background-color: #FFA500;
        color: white;
    }
    .status-running {
        background-color: #0099FF;
        color: white;
    }
    .status-completed {
        background-color: #00AA00;
        color: white;
    }
    .status-failed {
        background-color: #FF0000;
        color: white;
    }
    .research-result {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ===== CONFIGURATION =====

API_BASE_URL = "http://localhost:8000"
POLL_INTERVAL = 2  # seconds

# ===== HELPER FUNCTIONS =====

def get_api_health():
    """Check if API is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def submit_research(query: str, research_type: str) -> dict | None:
    """Submit a research request to the backend.
    
    Args:
        query: Research query
        research_type: Type of research ('supervisor' or 'researcher')
    
    Returns:
        Research response dict or None if failed
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/research",
            json={"query": query, "research_type": research_type},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to submit research: {str(e)}")
        return None

def get_research_status(research_id: str) -> dict | None:
    """Get the status of a research task.
    
    Args:
        research_id: Research task ID
    
    Returns:
        Research response dict or None if failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/research/{research_id}",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch research status: {str(e)}")
        return None

def get_status_badge_class(status: str) -> str:
    """Get CSS class for status badge."""
    return f"status-badge status-{status}"

# ===== MAIN APP =====

def main():
    """Main application logic."""
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div class='research-header'>🔬 Deep Research</div>", unsafe_allow_html=True)
    
    with col2:
        api_status = "✅ API Connected" if get_api_health() else "❌ API Offline"
        st.markdown(f"**{api_status}**")
    
    st.markdown("""
    Deep Research is an advanced AI-powered research tool that uses multi-agent systems
    to conduct comprehensive research on any topic. Powered by LangGraph and OpenAI.
    """)
    
    # ===== SIDEBAR =====
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        research_type = st.radio(
            "Research Type",
            options=["supervisor", "researcher"],
            format_func=lambda x: {
                "supervisor": "🤝 Multi-Agent (Supervisor)",
                "researcher": "🔍 Single Agent"
            }[x],
            help="Supervisor uses multiple agents for comprehensive research. Single agent is faster but less thorough."
        )
        
        st.divider()
        
        st.header("📋 History")
        if st.button("Clear History", key="clear_history"):
            st.session_state.research_history = []
            st.success("History cleared")
        
        if st.session_state.get("research_history"):
            for item in st.session_state.research_history:
                with st.expander(f"📌 {item['query'][:50]}..."):
                    st.caption(f"ID: {item['research_id']}")
                    st.caption(f"Status: {item['status']}")
                    st.caption(f"Time: {item['timestamp']}")
    
    # ===== MAIN CONTENT =====
    
    st.header("🔎 New Research")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_area(
            "Enter your research query",
            placeholder="e.g., Write a paper on the latest advancements in quantum computing and their practical applications...",
            height=100,
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("")  # spacing
        submit_button = st.button("🚀 Start Research", use_container_width=True, type="primary")
    
    # ===== RESEARCH SUBMISSION AND POLLING =====
    
    if submit_button:
        if not query.strip():
            st.error("Please enter a research query")
            return
        
        if not get_api_health():
            st.error("❌ API is offline. Please start the backend with: `python app/backend/main.py`")
            return
        
        # Submit research
        research_response = submit_research(query, research_type)
        if not research_response:
            return
        
        research_id = research_response["research_id"]
        
        # Add to history
        if "research_history" not in st.session_state:
            st.session_state.research_history = []
        
        st.session_state.research_history.append({
            "research_id": research_id,
            "query": query,
            "status": "pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Create placeholder for status updates
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        result_placeholder = st.empty()
        
        # Poll for completion
        start_time = time.time()
        max_wait_time = 300  # 5 minutes timeout
        
        while True:
            research_data = get_research_status(research_id)
            if not research_data:
                break
            
            status = research_data["status"]
            
            # Update status display
            with status_placeholder.container():
                if status == "pending":
                    st.info("⏳ Queued - waiting to start...")
                elif status == "running":
                    elapsed = int(time.time() - start_time)
                    st.info(f"🔄 Research in progress... ({elapsed}s elapsed)")
                elif status == "completed":
                    st.success("✅ Research completed!")
                    break
                elif status == "failed":
                    st.error(f"❌ Research failed: {research_data.get('error', 'Unknown error')}")
                    break
            
            # Check timeout
            if time.time() - start_time > max_wait_time:
                st.warning("⏱️ Research is taking longer than expected. You can check back later.")
                st.info(f"Research ID: `{research_id}`")
                break
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL)
        
        # Display results
        if research_data and research_data["status"] == "completed":
            result = research_data.get("result", {})
            
            with result_placeholder.container():
                st.markdown("---")
                st.subheader("📊 Research Results")
                
                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["📝 Summary", "📖 Raw Notes", "📄 Full Report"])
                
                with tab1:
                    compressed = result.get("compressed_research", "No summary available")
                    st.markdown(compressed)
                
                with tab2:
                    raw_notes = result.get("raw_notes", [])
                    if raw_notes:
                        for i, note in enumerate(raw_notes, 1):
                            st.markdown(f"**Note {i}:**")
                            st.markdown(note)
                            st.divider()
                    else:
                        st.info("No raw notes available")
                
                with tab3:
                    draft_report = result.get("draft_report", "")
                    if draft_report:
                        st.markdown(draft_report)
                    else:
                        st.info("No draft report available")
                
                # Download options
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    summary_json = json.dumps({
                        "query": query,
                        "research_id": research_id,
                        "summary": result.get("compressed_research", "")
                    }, indent=2)
                    st.download_button(
                        "📥 Download Summary",
                        summary_json,
                        file_name=f"research_{research_id}_summary.json",
                        mime="application/json"
                    )
                
                with col2:
                    full_report = f"# Research Report\n\n**Query:** {query}\n\n## Summary\n{result.get('compressed_research', '')}\n\n## Raw Notes\n{chr(10).join(result.get('raw_notes', []))}"
                    st.download_button(
                        "📥 Download Report (MD)",
                        full_report,
                        file_name=f"research_{research_id}_report.md",
                        mime="text/markdown"
                    )
                
                with col3:
                    st.info(f"Research ID: `{research_id}`")
    
    # ===== SELECTED RESEARCH VIEW =====
    
    if st.session_state.get("selected_research"):
        selected_id = st.session_state.selected_research
        st.markdown("---")
        st.header("📊 View Research Results")
        
        research_data = get_research_status(selected_id)
        if research_data and research_data["status"] == "completed":
            result = research_data.get("result", {})
            
            st.markdown(f"**Query:** {research_data['query']}")
            st.markdown(f"**Research ID:** {selected_id}")
            st.markdown(f"**Status:** {research_data['status']}")
            
            st.markdown("---")
            
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📝 Summary", "📖 Raw Notes", "📄 Full Report"])
            
            with tab1:
                compressed = result.get("compressed_research", "No summary available")
                st.markdown(compressed)
            
            with tab2:
                raw_notes = result.get("raw_notes", [])
                if raw_notes:
                    for i, note in enumerate(raw_notes, 1):
                        st.markdown(f"**Note {i}:**")
                        st.markdown(note)
                        st.divider()
                else:
                    st.info("No raw notes available")
            
            with tab3:
                draft_report = result.get("draft_report", "")
                if draft_report:
                    st.markdown(draft_report)
                else:
                    st.info("No draft report available")
            
            # Download options
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                summary_json = json.dumps({
                    "query": research_data['query'],
                    "research_id": selected_id,
                    "summary": result.get("compressed_research", "")
                }, indent=2)
                st.download_button(
                    "📥 Download Summary",
                    summary_json,
                    file_name=f"research_{selected_id}_summary.json",
                    mime="application/json"
                )
            
            with col2:
                full_report = f"# Research Report\n\n**Query:** {research_data['query']}\n\n## Summary\n{result.get('compressed_research', '')}\n\n## Raw Notes\n{chr(10).join(result.get('raw_notes', []))}"
                st.download_button(
                    "📥 Download Report (MD)",
                    full_report,
                    file_name=f"research_{selected_id}_report.md",
                    mime="text/markdown"
                )
            
            with col3:
                if st.button("← Back to Research List"):
                    st.session_state.selected_research = None
                    st.rerun()
        else:
            st.warning("Research not completed or data unavailable")
            if st.button("← Back to Research List"):
                st.session_state.selected_research = None
                st.rerun()
    
    # ===== BROWSE PAST RESEARCH =====
    
    if not st.session_state.get("selected_research"):
         st.header("📚 Browse Research")
         
         try:
             response = requests.get(f"{API_BASE_URL}/research", timeout=5)
             response.raise_for_status()
             all_research = response.json()
             
             if all_research:
                 # Filter and sort
                 col1, col2 = st.columns(2)
                 with col1:
                     status_filter = st.multiselect(
                         "Filter by status",
                         options=["pending", "running", "completed", "failed"],
                         default=["completed"]
                     )
                 
                 # Display research items
                 filtered_research = [r for r in all_research if r["status"] in status_filter]
                 
                 if filtered_research:
                     for research in sorted(filtered_research, key=lambda x: x["research_id"], reverse=True):
                         with st.expander(
                             f"{'✅' if research['status'] == 'completed' else '⏳'} {research['query'][:60]}... - {research['research_id']}"
                         ):
                             col1, col2 = st.columns(2)
                             with col1:
                                 st.caption(f"**Status:** {research['status']}")
                                 st.caption(f"**Research ID:** {research['research_id']}")
                             
                             with col2:
                                 if research["status"] == "completed" and research.get("result"):
                                     st.success("Results available")
                                     if st.button("View Results", key=f"view_{research['research_id']}"):
                                         st.session_state.selected_research = research['research_id']
                                         st.rerun()
                             
                             if research.get("error"):
                                 st.error(f"Error: {research['error']}")
                 else:
                     st.info("No research found matching the selected filters")
             else:
                 st.info("No research tasks yet. Start a new research to get began!")
         
         except requests.exceptions.RequestException:
             st.warning("Could not fetch research history")

if __name__ == "__main__":
    if "research_history" not in st.session_state:
        st.session_state.research_history = []
    
    main()
