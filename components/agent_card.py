"""
Agent card component for RRL Dashboard
"""
import streamlit as st

def render_agent_card(agent_status: dict, on_click=None):
    """Render an agent status card"""
    agent_id = agent_status["id"]
    name = agent_status["name"]
    emoji = agent_status["emoji"]
    description = agent_status["description"]
    health_status = agent_status["health_status"]
    health_color = agent_status["health_color"]
    process_running = agent_status["process_running"]
    pid = agent_status["pid"]
    log_age = agent_status["log_age_formatted"]
    
    # Status indicator
    status_emoji = {
        "healthy": "🟢",
        "unhealthy": "🔴",
        "unknown": "⚪",
        "no_data": "⚫"
    }.get(health_status, "⚪")
    
    # Process status text
    if process_running is True:
        process_text = f"🟢 Running (PID: {pid})"
    elif process_running is False:
        process_text = "🔴 Stopped"
    else:
        process_text = "⚪ N/A"
    
    # Card HTML
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid {agent_status['color']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        cursor: pointer;
        transition: transform 0.2s;
    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h3 style="margin: 0; color: white; font-size: 1.3rem;">
                    {emoji} {name}
                </h3>
                <p style="margin: 0.5rem 0 0 0; color: #aaa; font-size: 0.9rem;">
                    {description}
                </p>
            </div>
            <div style="font-size: 1.5rem;">
                {status_emoji}
            </div>
        </div>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #444;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #888;">
                <span>{process_text}</span>
                <span>📝 {log_age}</span>
            </div>
        </div>
    </div>
    """
    
    return card_html

def render_agent_grid(agents_status: list, cols: int = 3):
    """Render agents in a grid layout"""
    # Create columns
    columns = st.columns(cols)
    
    for i, agent in enumerate(agents_status):
        col_idx = i % cols
        with columns[col_idx]:
            card_html = render_agent_card(agent)
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Add a button for details
            if st.button(f"View Details →", key=f"btn_{agent['id']}", use_container_width=True):
                st.session_state.selected_agent = agent['id']
                st.switch_page("pages/1_Agent_Detail.py")
