import psutil
import platform
import time

TOOL = {
    "name": "system_status",
    "description": "Returns real-time system metrics: CPU usage, RAM, GPU load, CPU temperature, uptime, and process count.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    }
}

class SystemMonitor:
    def __init__(self):
        self.last_check = 0.0

    def check(self) -> str:
        """Checks for high resource utilization and returns warning alerts if any."""
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            if cpu > 90.0:
                return f"High CPU usage at {cpu}%"
            if ram > 92.0:
                return f"High RAM usage at {ram}%"
        except Exception:
            pass
        return ""

def get_system_status() -> str:
    """Retrieves current CPU, RAM, and system stats as a formatted string."""
    try:
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        
        battery = psutil.sensors_battery()
        battery_status = f"{battery.percent}%" if battery else "N/A"
        
        status_msg = f"CPU Usage: {cpu_usage}%, RAM Usage: {ram_usage}%, Battery: {battery_status}"
        return status_msg
    except Exception as e:
        return f"Failed to retrieve system status: {str(e)}"

def run(args, context=None):
    return get_system_status()