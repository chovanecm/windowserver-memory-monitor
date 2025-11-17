#!/usr/bin/env python3
"""
WindowServer Memory Monitor - Interactive Installation Wizard

This wizard helps you configure and install the WindowServer memory monitor service.
"""

import os
import sys
import subprocess
import re
from pathlib import Path

# ANSI color codes
BOLD = '\033[1m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RED = '\033[91m'
RESET = '\033[0m'

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.ini')

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")

def print_step(number, text):
    """Print a step number and description."""
    print(f"{BOLD}{CYAN}[{number}]{RESET} {BOLD}{text}{RESET}")

def print_success(text):
    """Print a success message."""
    print(f"{GREEN}✓{RESET} {text}")

def print_warning(text):
    """Print a warning message."""
    print(f"{YELLOW}⚠{RESET}  {text}")

def print_error(text):
    """Print an error message."""
    print(f"{RED}✗{RESET} {text}")

def print_info(text):
    """Print an info message."""
    print(f"{CYAN}ℹ{RESET}  {text}")

def get_input(prompt, default=None, validator=None):
    """Get user input with optional default and validation."""
    if default:
        prompt_text = f"{prompt} [{YELLOW}{default}{RESET}]: "
    else:
        prompt_text = f"{prompt}: "
    
    while True:
        try:
            value = input(prompt_text).strip()
            if not value and default:
                value = default
            
            if validator:
                is_valid, message = validator(value)
                if not is_valid:
                    print_error(message)
                    continue
            
            return value
        except KeyboardInterrupt:
            print("\n\nInstallation cancelled by user.")
            sys.exit(0)

def get_yes_no(prompt, default='y'):
    """Get yes/no input from user."""
    default_display = 'Y/n' if default.lower() == 'y' else 'y/N'
    response = get_input(f"{prompt} ({default_display})", default=default)
    return response.lower() in ['y', 'yes']

def validate_float(value):
    """Validate float input."""
    try:
        float_val = float(value)
        if float_val <= 0:
            return False, "Value must be positive"
        return True, ""
    except ValueError:
        return False, "Please enter a valid number"

def validate_integer(value):
    """Validate integer input."""
    try:
        int_val = int(value)
        if int_val <= 0:
            return False, "Value must be positive"
        return True, ""
    except ValueError:
        return False, "Please enter a valid integer"

def get_windowserver_memory():
    """Get current WindowServer memory usage."""
    try:
        result = subprocess.run(['pgrep', '-n', 'WindowServer'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return None
        
        pid = result.stdout.strip()
        result = subprocess.run(['top', '-l', '1', '-pid', pid], 
                              capture_output=True, text=True, timeout=10)
        
        lines = result.stdout.strip().split('\n')
        header_index = next((i for i, line in enumerate(lines) 
                           if 'PID' in line and 'COMMAND' in line), -1)
        
        if header_index == -1 or header_index + 1 >= len(lines):
            return None
        
        headers = re.split(r'\s+', lines[header_index].strip())
        mem_column_index = next((i for i, h in enumerate(headers) if h == 'MEM'), -1)
        
        if mem_column_index == -1:
            return None
        
        process_line = lines[header_index + 1].strip()
        process_data = re.split(r'\s+', process_line)
        mem_str = process_data[mem_column_index]
        
        value_match = re.match(r'(\d+\.?\d*)', mem_str)
        if not value_match:
            return None
        
        value = float(value_match.group(1))
        unit = mem_str[-1].upper() if len(mem_str) > len(value_match.group(1)) else ''
        
        if unit == 'K':
            return value / 1024 / 1024  # Convert to GB
        elif unit == 'M':
            return value / 1024
        elif unit == 'G':
            return value
        else:
            return value / 1024 / 1024 / 1024
    except:
        return None

def find_common_apps():
    """Find commonly installed apps that might cause WindowServer leaks."""
    apps_to_check = [
        'DockDoor',
        'alt-tab',
        'AltTab',
        'Rectangle',
        'BetterTouchTool',
        'Magnet',
        'Raycast',
        'Hyperswitch'
    ]
    
    found_apps = []
    applications_dir = '/Applications'
    
    for app in apps_to_check:
        app_path = os.path.join(applications_dir, f"{app}.app")
        if os.path.exists(app_path):
            found_apps.append(app)
    
    return found_apps

def main():
    """Main installation wizard."""
    os.system('clear')
    
    print(f"{BOLD}{GREEN}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║                                                        ║")
    print("║     WindowServer Memory Monitor                        ║")
    print("║     Interactive Installation Wizard                    ║")
    print("║                                                        ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    print("Welcome! This wizard will help you configure and install")
    print("the WindowServer memory monitoring service.\n")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print_error(f"Python 3.6+ required. You have {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    
    # Check if running on macOS
    if sys.platform != 'darwin':
        print_error("This tool is designed for macOS only")
        sys.exit(1)
    
    print_success("Running on macOS")
    print()
    
    # Show current WindowServer memory
    current_memory = get_windowserver_memory()
    if current_memory:
        print_info(f"Current WindowServer memory usage: {BOLD}{current_memory:.2f} GB{RESET}")
        print()
    
    # Step 1: Memory Threshold
    print_header("Step 1: Memory Threshold")
    print("Set the memory threshold for WindowServer. When this limit is")
    print("exceeded, the configured apps will be restarted.\n")
    
    if current_memory:
        suggested_threshold = max(2.0, round(current_memory + 0.5, 1))
        print_info(f"Suggested threshold: {suggested_threshold:.1f} GB (current usage + 0.5 GB)")
    else:
        suggested_threshold = 3.0
    
    print("\nCommon values:")
    print(f"  • {BOLD}2.0 GB{RESET} - Aggressive monitoring (16GB systems)")
    print(f"  • {BOLD}3.0 GB{RESET} - Balanced monitoring (most systems)")
    print(f"  • {BOLD}4.0 GB{RESET} - Relaxed monitoring (32GB+ systems)")
    print()
    
    memory_threshold = get_input(
        "Memory threshold (GB)",
        default=str(suggested_threshold),
        validator=validate_float
    )
    memory_threshold_gb = float(memory_threshold)
    print_success(f"Threshold set to {memory_threshold_gb:.1f} GB")
    
    # Step 2: Apps to Monitor
    print_header("Step 2: Applications to Restart")
    print("Select which apps to restart when the threshold is exceeded.\n")
    
    found_apps = find_common_apps()
    
    if found_apps:
        print(f"Found these commonly problematic apps on your system:\n")
        for i, app in enumerate(found_apps, 1):
            print(f"  {i}. {BOLD}{app}{RESET}")
        print()
        
        if get_yes_no("Would you like to monitor all of these apps?", default='y'):
            selected_apps = found_apps
        else:
            selected_apps = []
            for app in found_apps:
                if get_yes_no(f"  Monitor {BOLD}{app}{RESET}?", default='y'):
                    selected_apps.append(app)
    else:
        print_warning("No common apps found in /Applications")
        selected_apps = []
    
    # Allow manual app entry
    print()
    if get_yes_no("Would you like to add additional apps manually?", default='n'):
        print("\nEnter app names (press Enter on empty line to finish):")
        print_info("App names must match exactly as they appear in /Applications")
        while True:
            app_name = get_input("App name (or press Enter to finish)", default="").strip()
            if not app_name:
                break
            if app_name not in selected_apps:
                selected_apps.append(app_name)
                print_success(f"Added {app_name}")
            else:
                print_warning(f"{app_name} already in list")
    
    if not selected_apps:
        print_error("\nNo apps selected! You must select at least one app to monitor.")
        if get_yes_no("Would you like to start over?", default='y'):
            main()
            return
        else:
            sys.exit(1)
    
    print()
    print_success(f"Will monitor: {', '.join(selected_apps)}")
    
    # Step 3: Check Interval
    print_header("Step 3: Check Interval")
    print("How often should WindowServer memory be checked?\n")
    print("Common intervals:")
    print(f"  • {BOLD}5 minutes{RESET}  - Frequent checks")
    print(f"  • {BOLD}10 minutes{RESET} - Balanced (recommended)")
    print(f"  • {BOLD}15 minutes{RESET} - Less frequent")
    print()
    
    interval_minutes = get_input(
        "Check interval (minutes)",
        default="10",
        validator=validate_integer
    )
    interval_seconds = int(interval_minutes) * 60
    print_success(f"Will check every {interval_minutes} minutes")
    
    # Step 4: Review Configuration
    print_header("Step 4: Review Configuration")
    print("Please review your configuration:\n")
    print(f"  {BOLD}Memory Threshold:{RESET}   {memory_threshold_gb:.1f} GB")
    print(f"  {BOLD}Apps to Monitor:{RESET}    {', '.join(selected_apps)}")
    print(f"  {BOLD}Check Interval:{RESET}     Every {interval_minutes} minutes")
    print(f"  {BOLD}Script Location:{RESET}    {SCRIPT_DIR}")
    print(f"  {BOLD}Log Location:{RESET}       ~/Library/Logs/windowserver-monitor.out.log")
    print()
    
    if not get_yes_no("Proceed with installation?", default='y'):
        print("\nInstallation cancelled.")
        sys.exit(0)
    
    # Step 5: Create Configuration
    print_header("Step 5: Installing")
    
    # Create config file
    config_content = f"""# WindowServer Memory Monitor Configuration
# Generated by installation wizard on {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}
# ==========================================

[settings]

# Memory threshold in gigabytes (GB)
memory_threshold_gb = {memory_threshold_gb}

# Comma-separated list of applications to restart
apps_to_restart = {', '.join(selected_apps)}
"""
    
    # Write config to script directory
    config_path = os.path.join(SCRIPT_DIR, 'config.ini')
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print_step(1, "Configuration file created")
    print_success("config.ini created")
    
    # Run make install
    print()
    print_step(2, "Running installation")
    print_info("This will install the service using the Makefile")
    print()
    
    try:
        # First, ensure config.ini is in place before make install
        install_result = subprocess.run(
            ['make', 'install'],
            check=True,
            text=True
        )
        
        print()
        print_step(3, "Updating check interval")
        
        # Update the plist file with custom interval
        plist_path = Path.home() / 'Library' / 'LaunchAgents' / 'cz.chovanecm.windowserver-monitor.plist'
        
        if plist_path.exists():
            with open(plist_path, 'r') as f:
                plist_content = f.read()
            
            # Replace the interval
            plist_content = re.sub(
                r'<key>StartInterval</key>\s*<integer>\d+</integer>',
                f'<key>StartInterval</key>\n    <integer>{interval_seconds}</integer>',
                plist_content
            )
            
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # Reload the service
            subprocess.run(['launchctl', 'unload', str(plist_path)], 
                         capture_output=True)
            subprocess.run(['launchctl', 'load', str(plist_path)], 
                         check=True, capture_output=True)
            
            print_success(f"Check interval set to {interval_minutes} minutes")
        
    except subprocess.CalledProcessError as e:
        print_error("Installation failed!")
        print(f"Error: {e}")
        sys.exit(1)
    
    # Success!
    print()
    print(f"{BOLD}{GREEN}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║                                                        ║")
    print("║              ✓ Installation Complete!                 ║")
    print("║                                                        ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    print("\nThe WindowServer memory monitor is now running!")
    print(f"It will check every {BOLD}{interval_minutes} minutes{RESET} and restart apps")
    print(f"when WindowServer exceeds {BOLD}{memory_threshold_gb:.1f} GB{RESET}.\n")
    
    print("📝 Useful commands:")
    print(f"  • View logs:     {CYAN}make logs{RESET}")
    print(f"  • Check status:  {CYAN}make status{RESET}")
    print(f"  • Test script:   {CYAN}python3 monitor_windowserver.py --dry-run{RESET}")
    print(f"  • Edit config:   {CYAN}nano config.ini{RESET}")
    print(f"  • Uninstall:     {CYAN}make uninstall{RESET}")
    print()
    
    if get_yes_no("Would you like to view the logs now?", default='n'):
        print()
        subprocess.run(['make', 'logs'])

if __name__ == '__main__':
    main()
