"""
Logs Viewer Page
"""
import streamlit as st
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.auth import require_auth
from components.utils import load_agents_config, read_log_tail

st.set_page_config(
    page_title="Logs Viewer - RRL Dashboard",
    page_icon="📋",
    layout="wide"
)

require_auth()

config = load_agents_config()
agents = config.get("agents", {})

st.title("📋 Logs Viewer")

# Log file selector
log_files = {}
for agent_id, agent_config in agents.items():
    if agent_config.get('log_file'):
        log_files[f"{agent_config['emoji']} {agent_config['name']}"] = agent_config['log_file']

# Add system logs
log_files["🔄 Cron Auto-Send"] = "/home/dandysetiawan/.openclaw/workspace/cron_autosend.log"

selected_label = st.selectbox("Select Log Source", list(log_files.keys()))
selected_log = log_files.get(selected_label)

if selected_log:
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.code(selected_log)
    
    with col2:
        if os.path.exists(selected_log):
            file_size = os.path.getsize(selected_log)
            st.metric("File Size", f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} B")
        else:
            st.error("File not found")
    
    with col3:
        if os.path.exists(selected_log):
            mtime = os.path.getmtime(selected_log)
            from datetime import datetime
            st.metric("Modified", datetime.fromtimestamp(mtime).strftime("%H:%M:%S"))
    
    # Display options
    st.divider()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        num_lines = st.number_input("Lines", min_value=10, max_value=1000, value=100, step=10)
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=False)
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
    
    with col2:
        # Search/filter
        search_term = st.text_input("Search (optional)", placeholder="Filter logs...")
    
    # Display logs
    st.divider()
    
    if os.path.exists(selected_log):
        logs = read_log_tail(selected_log, num_lines)
        
        if search_term:
            logs = [line for line in logs if search_term.lower() in line.lower()]
        
        if logs:
            log_text = ''.join(logs)
            
            # Color coding for different log levels
            import re
            
            # Simple syntax highlighting
            highlighted = log_text
            highlighted = re.sub(r'(ERROR|CRITICAL|FATAL)', r'🔴 **\1**', highlighted, flags=re.IGNORECASE)
            highlighted = re.sub(r'(WARNING|WARN)', r'🟡 **\1**', highlighted, flags=re.IGNORECASE)
            highlighted = re.sub(r'(INFO)', r'🟢 **\1**', highlighted, flags=re.IGNORECASE)
            highlighted = re.sub(r'(DEBUG)', r'⚪ **\1**', highlighted, flags=re.IGNORECASE)
            
            st.markdown(f"""
            <div style="
                background: #1e1e1e;
                border-radius: 8px;
                padding: 1rem;
                font-family: 'Courier New', monospace;
                font-size: 0.85rem;
                line-height: 1.5;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
            ">{highlighted}</div>
            """, unsafe_allow_html=True)
            
            # Download button
            st.download_button(
                label="📥 Download Full Log",
                data=open(selected_log, 'rb').read(),
                file_name=os.path.basename(selected_log),
                mime='text/plain'
            )
        else:
            if search_term:
                st.info(f"No lines matching '{search_term}'")
            else:
                st.info("Log file is empty")
    else:
        st.error(f"Log file not found: {selected_log}")
    
    # Auto-refresh
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()
else:
    st.info("No log file selected")
