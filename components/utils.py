"""
Utility functions for RRL Dashboard
"""
import os
import psutil
import yaml
from datetime import datetime, timedelta
from pathlib import Path

def load_agents_config():
    """Load agent configuration from YAML"""
    config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def check_process_running(process_name: str) -> bool:
    """Check if a process is running by name"""
    if not process_name:
        return None
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if process_name in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def get_process_pid(process_name: str) -> int:
    """Get PID of a process by name"""
    if not process_name:
        return None
    
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if process_name in cmdline:
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None

def read_log_tail(log_file: str, lines: int = 50) -> list:
    """Read last N lines from log file"""
    if not log_file or not os.path.exists(log_file):
        return []
    
    try:
        with open(log_file, 'r') as f:
            # Read all lines and get last N
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except Exception as e:
        return [f"Error reading log: {e}"]

def get_log_file_age(log_file: str) -> timedelta:
    """Get age of log file"""
    if not log_file or not os.path.exists(log_file):
        return None
    
    mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
    return datetime.now() - mtime

def format_timedelta(td: timedelta) -> str:
    """Format timedelta to human readable string"""
    if td is None:
        return "N/A"
    
    total_seconds = int(td.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}s ago"
    elif total_seconds < 3600:
        return f"{total_seconds // 60}m ago"
    elif total_seconds < 86400:
        return f"{total_seconds // 3600}h ago"
    else:
        return f"{total_seconds // 86400}d ago"

def get_system_info():
    """Get system information"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    }

def get_agent_status(agent_id: str, agent_config: dict) -> dict:
    """Get comprehensive status for an agent"""
    status = {
        "id": agent_id,
        "name": agent_config.get("name", agent_id),
        "description": agent_config.get("description", ""),
        "emoji": agent_config.get("emoji", "🤖"),
        "color": agent_config.get("color", "#666"),
        "process_running": None,
        "pid": None,
        "log_age": None,
        "log_age_formatted": "N/A",
        "health_status": "unknown",
        "health_color": "gray",
        "last_lines": []
    }
    
    # Check process
    process_name = agent_config.get("process_name")
    if process_name:
        status["process_running"] = check_process_running(process_name)
        status["pid"] = get_process_pid(process_name)
    
    # Check log file
    log_file = agent_config.get("log_file")
    if log_file:
        log_age = get_log_file_age(log_file)
        status["log_age"] = log_age
        status["log_age_formatted"] = format_timedelta(log_age)
        status["last_lines"] = read_log_tail(log_file, 20)
    
    # Determine health status
    health_checks = agent_config.get("health_checks", [])
    if health_checks:
        all_healthy = True
        for check in health_checks:
            check_type = check.get("type")
            
            if check_type == "pid":
                if not status["process_running"]:
                    all_healthy = False
                    break
            
            elif check_type == "log_age":
                max_minutes = check.get("max_minutes", 5)
                if status["log_age"] and status["log_age"].total_seconds() > max_minutes * 60:
                    all_healthy = False
                    break
        
        if all_healthy:
            status["health_status"] = "healthy"
            status["health_color"] = "green"
        else:
            status["health_status"] = "unhealthy"
            status["health_color"] = "red"
    elif process_name and status["process_running"]:
        status["health_status"] = "healthy"
        status["health_color"] = "green"
    elif not process_name and not log_file:
        # No health checks defined
        status["health_status"] = "no_data"
        status["health_color"] = "gray"
    
    return status
