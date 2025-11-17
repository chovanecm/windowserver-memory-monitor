import subprocess
import time
import re
import configparser
import os

# --- Configuration ---
# The script will find its config file in its own directory.
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.ini')
PROCESS_NAME = "WindowServer"
# -------------------

def read_config():
    """Reads configuration from config.ini in the script's directory."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file '{CONFIG_FILE}' not found.")
        exit(1)
    config.read(CONFIG_FILE)
    
    memory_threshold_gb = config.getfloat('settings', 'memory_threshold_gb', fallback=4.0)
    apps_str = config.get('settings', 'apps_to_restart', fallback='DockDoor')
    apps_to_restart = [app.strip() for app in apps_str.split(',') if app.strip()]
    
    return memory_threshold_gb, apps_to_restart

def get_process_pid(process_name: str) -> str | None:
    """Gets the PID of a process using pgrep."""
    try:
        result = subprocess.run(['pgrep', '-n', process_name], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"Warning: Could not find process '{process_name}'.")
        return None

def get_memory_from_top(pid: str) -> int | None:
    """Gets the memory usage in bytes for a given PID by parsing 'top'."""
    try:
        result = subprocess.run(['top', '-l', '1', '-pid', pid], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        header_index = next((i for i, line in enumerate(lines) if 'PID' in line and 'COMMAND' in line), -1)
        
        if header_index == -1:
            print("Warning: Could not find header row in 'top' output.")
            return None

        headers = re.split(r'\s+', lines[header_index].strip())
        mem_column_index = next((i for i, header in enumerate(headers) if header == 'MEM'), -1)
        
        if mem_column_index == -1:
            print("Warning: Could not find 'MEM' column in 'top' output.")
            return None

        process_line = lines[header_index + 1].strip()
        process_data = re.split(r'\s+', process_line)
        mem_str = process_data[mem_column_index]
        
        value_str = re.match(r'(\d+\.?\d*)', mem_str)
        if not value_str:
            print(f"Warning: Could not parse memory value from '{mem_str}'.")
            return None
        
        value = float(value_str.group(1))
        unit = mem_str[-1].upper() if mem_str else ''

        if unit == 'K': return int(value * 1024)
        if unit == 'M': return int(value * 1024**2)
        if unit == 'G': return int(value * 1024**3)
        return int(value)

    except (subprocess.CalledProcessError, FileNotFoundError, ValueError, IndexError) as e:
        print(f"Error parsing 'top' output: {e}")
        return None

def restart_apps(app_names: list[str]):
    """Gracefully quit and then restart a list of macOS applications."""
    for app_name in app_names:
        print(f"--- Processing '{app_name}' ---")
        try:
            # Try to quit the app. Don't check for errors, as it might not be running.
            quit_command = f'quit app "{app_name}"'
            subprocess.run(['osascript', '-e', quit_command], capture_output=True, text=True)
            print(f"Quit command sent to '{app_name}' (if it was running).")
            time.sleep(3) # Give app time to quit

            # Try to start the app. This will fail if it's not installed.
            subprocess.run(['open', '-a', app_name], check=True, capture_output=True)
            print(f"Successfully started '{app_name}'.")

        except subprocess.CalledProcessError:
            # This specifically catches the error from `open -a` if the app doesn't exist.
            print(f"Warning: Application '{app_name}' not found. Skipping restart.")
        except FileNotFoundError:
            # This catches if 'osascript' or 'open' aren't found on the system.
            print(f"Error: 'osascript' or 'open' command not found. This script is for macOS.")
            break # No point continuing if the core commands are missing.

def main():
    """Main monitoring function."""
    memory_threshold_gb, apps_to_restart = read_config()
    memory_threshold_bytes = memory_threshold_gb * 1024**3

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running check...")
    print(f"Threshold: {memory_threshold_gb} GB. Apps to restart: {', '.join(apps_to_restart)}")
    
    pid = get_process_pid(PROCESS_NAME)
    if not pid:
        return

    memory_usage_bytes = get_memory_from_top(pid)
    if memory_usage_bytes is None:
        print(f"Warning: Could not get memory usage for '{PROCESS_NAME}' (PID: {pid}).")
        return

    memory_usage_gb = memory_usage_bytes / (1024**3)
    print(f"'{PROCESS_NAME}' memory usage: {memory_usage_gb:.2f} GB.")

    if memory_usage_bytes > memory_threshold_bytes:
        print(f"ALERT: Memory usage ({memory_usage_gb:.2f} GB) exceeds threshold of {memory_threshold_gb} GB.")
        restart_apps(apps_to_restart)
    else:
        print(f"Memory usage is within the acceptable limit.")

if __name__ == "__main__":
    main()
