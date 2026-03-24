"""
Agent Detail Page
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.auth import require_auth
from components.utils import load_agents_config, get_agent_status, read_log_tail

st.set_page_config(
    page_title="Agent Details - RRL Dashboard",
    page_icon="📊",
    layout="wide"
)

require_auth()

config = load_agents_config()
agents = config.get("agents", {})

st.title("📊 Agent Details")

# Agent selector
agent_options = {f"{v['emoji']} {v['name']}": k for k, v in agents.items()}
selected_label = st.selectbox("Select Agent", list(agent_options.keys()))
selected_agent = agent_options[selected_label]

if selected_agent:
    agent_config = agents[selected_agent]
    status = get_agent_status(selected_agent, agent_config)
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.header(f"{agent_config['emoji']} {agent_config['name']}")
        st.caption(agent_config['description'])
    
    with col2:
        health_color = status['health_color']
        health_emoji = {"green": "🟢", "red": "🔴", "gray": "⚪"}.get(health_color, "⚪")
        st.metric("Status", f"{health_emoji} {status['health_status'].upper()}")
    
    with col3:
        if status['pid']:
            st.metric("PID", status['pid'])
        else:
            st.metric("PID", "N/A")
    
    st.divider()
    
    # Configuration
    st.subheader("Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Process**")
        if agent_config.get('process_name'):
            st.code(agent_config['process_name'])
            if status['process_running']:
                st.success("✅ Running")
            else:
                st.error("❌ Stopped")
        else:
            st.info("No process configured")
        
        st.markdown("**Log File**")
        if agent_config.get('log_file'):
            st.code(agent_config['log_file'])
            st.caption(f"Last update: {status['log_age_formatted']}")
        else:
            st.info("No log file configured")
    
    with col2:
        if 'schedule' in agent_config:
            st.markdown("**Schedule**")
            for item in agent_config['schedule']:
                st.markdown(f"- {item}")
        
        if 'cron_jobs' in agent_config:
            st.markdown("**Cron Jobs**")
            for item in agent_config['cron_jobs']:
                st.markdown(f"- {item}")
        
        if 'data_sources' in agent_config:
            st.markdown("**Data Sources**")
            for source in agent_config['data_sources']:
                st.markdown(f"- {source}")
    
    st.divider()
    
    # Additional config
    if 'config' in agent_config:
        st.subheader("Settings")
        config_items = agent_config['config']
        cols = st.columns(min(len(config_items), 3))
        for i, (key, value) in enumerate(config_items.items()):
            with cols[i % 3]:
                st.metric(key.replace('_', ' ').title(), str(value))
    
    if 'projects' in agent_config:
        st.subheader("Active Projects")
        for project in agent_config['projects']:
            st.markdown(f"- {project}")
    
    if 'platforms' in agent_config:
        st.subheader("Platforms")
        for platform in agent_config['platforms']:
            st.markdown(f"- {platform}")
    
    st.divider()
    
    # Log viewer
    if agent_config.get('log_file'):
        st.subheader("Recent Logs")
        
        num_lines = st.slider("Lines to show", 10, 200, 50)
        logs = read_log_tail(agent_config['log_file'], num_lines)
        
        if logs:
            log_text = ''.join(logs)
            st.code(log_text, language='text')
        else:
            st.info("No log entries found")
    
    # Actions
    st.divider()
    st.subheader("Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()
    
    with col2:
        if agent_config.get('process_name') and not status['process_running']:
            if st.button("▶️ Start Agent", use_container_width=True, type="primary"):
                st.warning("Start functionality not yet implemented")
        elif agent_config.get('process_name') and status['process_running']:
            if st.button("⏹️ Stop Agent", use_container_width=True, type="secondary"):
                st.warning("Stop functionality not yet implemented")
    
    with col3:
        if st.button("📋 View Full Logs", use_container_width=True):
            st.switch_page("pages/2_Logs_Viewer.py")
