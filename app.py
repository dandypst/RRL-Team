"""
RRL-Team Dashboard - Main Application
"""
import streamlit as st
import sys
from pathlib import Path

# Add components to path
sys.path.insert(0, str(Path(__file__).parent))

from components.auth import require_auth, logout
from components.utils import load_agents_config, get_agent_status, get_system_info
from components.agent_card import render_agent_grid

# Page config
st.set_page_config(
    page_title="RRL-Team Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Require authentication
require_auth()

# Load configuration
config = load_agents_config()
agents = config.get("agents", {})
system = config.get("system", {})

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2>🚀 RRL-Team</h2>
        <p style="color: #666; font-size: 0.8rem;">Monitoring Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation
    st.subheader("Navigation")
    if st.button("🏠 Dashboard", use_container_width=True):
        st.rerun()
    if st.button("📊 Agent Details", use_container_width=True):
        st.switch_page("pages/1_Agent_Detail.py")
    if st.button("📋 Logs Viewer", use_container_width=True):
        st.switch_page("pages/2_Logs_Viewer.py")
    
    st.divider()
    
    # System info
    st.subheader("System Status")
    sys_info = get_system_info()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("CPU", f"{sys_info['cpu_percent']:.1f}%")
    with col2:
        st.metric("RAM", f"{sys_info['memory_percent']:.1f}%")
    
    st.caption(f"Disk: {sys_info['disk_percent']:.1f}% used")
    st.caption(f"Boot: {sys_info['boot_time']}")
    
    st.divider()
    
    # Gateway status
    st.subheader("Gateway")
    gateway = system.get("gateway", {})
    st.caption(f"WA: {gateway.get('wa_number', 'N/A')}")
    
    st.divider()
    
    # Logout
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        logout()

# Main content
st.title("🚀 RRL-Team Dashboard")
st.caption(f"Welcome, {st.session_state.get('username', 'Admin')} | {st.session_state.get('login_time', 'Unknown')}")

# Summary metrics
st.subheader("Overview")

# Get all agent statuses
agents_status = []
healthy_count = 0
unhealthy_count = 0
no_data_count = 0

for agent_id, agent_config in agents.items():
    status = get_agent_status(agent_id, agent_config)
    agents_status.append(status)
    
    if status["health_status"] == "healthy":
        healthy_count += 1
    elif status["health_status"] == "unhealthy":
        unhealthy_count += 1
    else:
        no_data_count += 1

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Agents", len(agents))
with col2:
    st.metric("🟢 Healthy", healthy_count)
with col3:
    st.metric("🔴 Unhealthy", unhealthy_count)
with col4:
    st.metric("⚪ No Data", no_data_count)

st.divider()

# Agent grid
st.subheader("Agent Status")
render_agent_grid(agents_status, cols=3)

# Footer
st.divider()
st.caption("RRL-Team Dashboard v1.0 | Built with Streamlit")
