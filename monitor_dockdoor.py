import subprocess
import time
import re

# --- Configuration ---
PROCESS_NAME = "WindowServer"
APP_NAME = "DockDoor"
MEMORY_THRESHOLD_GB = 4.0
# -------------------

MEMORY_THRESHOLD_BYTES = MEMORY_THRESHOLD_GB * 1024**3

def get_process_pid(process_name: str) -> str | None:
    """Gets the PID of a process using pgrep."""
    try:
        result = subprocess.run(['pgrep', '-n', process_name], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"Warning: Could not find process '{process_name}'.")
        return None

def get_memory_from_top(pid: str) -> int | None:
    """
    Gets the memory usage in bytes for a given PID by parsing 'top'.
    This is complex because top's output is designed for humans.
    """
    try:
        result = subprocess.run(['top', '-l', '1', '-pid', pid], capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\n')
        header_index = -1
        for i, line in enumerate(lines):
            if 'PID' in line and 'COMMAND' in line:
                header_index = i
                break
        
        if header_index == -1:
            print("Warning: Could not find header row in 'top' output.")
            return None

        headers = re.split(r'\s+', lines[header_index].strip())
        mem_column_index = -1
        for i, header in enumerate(headers):
            if header == 'MEM':
                mem_column_index = i
                break
        
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
        unit = mem_str[-1].upper()

        if unit == 'K':
            return int(value * 1024)
        elif unit == 'M':
            return int(value * 1024**2)
        elif unit == 'G':
            return int(value * 1024**3)
        else:
            return int(value)

    except (subprocess.CalledProcessError, FileNotFoundError, ValueError, IndexError) as e:
        print(f"Error parsing 'top' output: {e}")
        return None

def restart_app(app_name: str):
    """Gracefully quit and then restart a macOS application."""
    print(f"Attempting to restart '{app_name}'...")
    try:
        quit_command = f'quit app "{app_name}"'
        subprocess.run(['osascript', '-e', quit_command], check=True, capture_output=True)
        print(f"Successfully sent quit command to '{app_name}'.")
        time.sleep(5)
        subprocess.run(['open', '-a', app_name], check=True)
        print(f"Successfully started '{app_name}'.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error while trying to restart '{app_name}': {e}")

def main():
    """Main monitoring function."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running check using 'top' command...")
    
    pid = get_process_pid(PROCESS_NAME)
    if not pid:
        return

    memory_usage_bytes = get_memory_from_top(pid)
    if memory_usage_bytes is None:
        print(f"Warning: Could not get memory usage for '{PROCESS_NAME}' (PID: {pid}).")
        return

    memory_usage_gb = memory_usage_bytes / (1024**3)
    print(f"'{PROCESS_NAME}' memory usage: {memory_usage_gb:.2f} GB (matches Activity Monitor).")

    if memory_usage_bytes > MEMORY_THRESHOLD_BYTES:
        print(f"ALERT: Memory usage ({memory_usage_gb:.2f} GB) exceeds threshold of {MEMORY_THRESHOLD_GB} GB.")
        restart_app(APP_NAME)
    else:
        print(f"Memory usage is within the acceptable limit ({MEMORY_THRESHOLD_GB} GB).")

if __name__ == "__main__":
    main()
