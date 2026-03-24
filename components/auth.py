"""
Authentication module for RRL Dashboard
"""
import streamlit as st
import hashlib
import time

def get_default_password():
    """Get default password from secrets or fallback"""
    try:
        return st.secrets.get("DASHBOARD_PASSWORD", "password")
    except:
        return "password"

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username: str, password: str) -> bool:
    """Check if credentials are valid"""
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD_HASH = hash_password(get_default_password())
    
    if username == DEFAULT_USERNAME:
        return hash_password(password) == DEFAULT_PASSWORD_HASH
    return False

def login_page():
    """Display login page"""
    st.set_page_config(
        page_title="RRL Dashboard - Login",
        page_icon="🚀",
        layout="centered"
    )
    
    # Centered login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🚀 RRL-Team Dashboard</h1>
            <p style="color: #666;">Monitoring & Control Center</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if check_credentials(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_time = time.time()
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

def require_auth():
    """Check if user is authenticated, show login if not"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        login_page()
        st.stop()
    
    # Check session timeout (8 hours)
    if "login_time" in st.session_state:
        if time.time() - st.session_state.login_time > 8 * 3600:
            st.session_state.authenticated = False
            st.warning("Session expired. Please login again.")
            st.rerun()

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    if "username" in st.session_state:
        del st.session_state.username
    if "login_time" in st.session_state:
        del st.session_state.login_time
    st.rerun()
