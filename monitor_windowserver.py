#!/usr/bin/env python3
"""
WindowServer Memory Monitor

Monitors the macOS WindowServer process for excessive memory usage and
automatically restarts configured applications to mitigate memory leaks.

Author: WindowServer Memory Monitor Contributors
License: MIT
"""

import subprocess
import sys
import time
import re
import configparser
import os
import argparse
import logging
from typing import Optional, List

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.ini')
PROCESS_NAME = "WindowServer"
VERSION = "1.0.0"
# -------------------

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=log_level
    )
    return logging.getLogger(__name__)

logger = logging.getLogger(__name__)

def read_config() -> tuple[float, List[str]]:
    """
    Reads configuration from config.ini in the script's directory.
    
    Returns:
        Tuple of (memory_threshold_gb, apps_to_restart)
    
    Raises:
        SystemExit: If config file not found or invalid
    """
    config = configparser.ConfigParser()
    
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"Configuration file not found: {CONFIG_FILE}")
        logger.error("Please create config.ini or run 'make install' to set up the service.")
        sys.exit(1)
    
    try:
        config.read(CONFIG_FILE)
        memory_threshold_gb = config.getfloat('settings', 'memory_threshold_gb', fallback=4.0)
        apps_str = config.get('settings', 'apps_to_restart', fallback='DockDoor')
        apps_to_restart = [app.strip() for app in apps_str.split(',') if app.strip()]
        
        if memory_threshold_gb <= 0:
            logger.error(f"Invalid memory threshold: {memory_threshold_gb}. Must be positive.")
            sys.exit(1)
        
        if not apps_to_restart:
            logger.warning("No apps configured to restart. Check config.ini.")
        
        return memory_threshold_gb, apps_to_restart
    
    except (ValueError, configparser.Error) as e:
        logger.error(f"Error reading configuration: {e}")
        sys.exit(1)

def get_process_pid(process_name: str) -> Optional[str]:
    """
    Gets the PID of a process using pgrep.
    
    Args:
        process_name: Name of the process to find
    
    Returns:
        PID as string, or None if not found
    """
    try:
        result = subprocess.run(
            ['pgrep', '-n', process_name],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        pid = result.stdout.strip()
        logger.debug(f"Found {process_name} with PID: {pid}")
        return pid
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout while searching for process '{process_name}'")
        return None
    except subprocess.CalledProcessError:
        logger.warning(f"Process '{process_name}' not found.")
        return None
    except FileNotFoundError:
        logger.error("'pgrep' command not found. This script requires macOS.")
        sys.exit(1)

def get_memory_from_top(pid: str) -> Optional[int]:
    """
    Gets the memory usage in bytes for a given PID by parsing 'top'.
    
    Args:
        pid: Process ID to check
    
    Returns:
        Memory usage in bytes, or None if unable to determine
    """
    try:
        result = subprocess.run(
            ['top', '-l', '1', '-pid', pid],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        lines = result.stdout.strip().split('\n')
        
        # Find header row containing column names
        header_index = next(
            (i for i, line in enumerate(lines) if 'PID' in line and 'COMMAND' in line),
            -1
        )
        
        if header_index == -1:
            logger.error("Could not find header row in 'top' output.")
            return None

        headers = re.split(r'\s+', lines[header_index].strip())
        mem_column_index = next(
            (i for i, header in enumerate(headers) if header == 'MEM'),
            -1
        )
        
        if mem_column_index == -1:
            logger.error("Could not find 'MEM' column in 'top' output.")
            return None

        if header_index + 1 >= len(lines):
            logger.error("No process data found in 'top' output.")
            return None

        process_line = lines[header_index + 1].strip()
        process_data = re.split(r'\s+', process_line)
        
        if mem_column_index >= len(process_data):
            logger.error(f"Memory column index out of range: {mem_column_index}")
            return None
        
        mem_str = process_data[mem_column_index]
        
        # Parse memory value (e.g., "2.5G", "512M", "1024K")
        value_match = re.match(r'(\d+\.?\d*)', mem_str)
        if not value_match:
            logger.error(f"Could not parse memory value from '{mem_str}'.")
            return None
        
        value = float(value_match.group(1))
        unit = mem_str[-1].upper() if len(mem_str) > len(value_match.group(1)) else ''

        # Convert to bytes
        if unit == 'K':
            return int(value * 1024)
        elif unit == 'M':
            return int(value * 1024**2)
        elif unit == 'G':
            return int(value * 1024**3)
        else:
            return int(value)

    except subprocess.TimeoutExpired:
        logger.error("Timeout while running 'top' command.")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running 'top': {e}")
        return None
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing 'top' output: {e}")
        return None
    except FileNotFoundError:
        logger.error("'top' command not found. This script requires macOS.")
        sys.exit(1)

def restart_apps(app_names: List[str], dry_run: bool = False) -> None:
    """
    Gracefully quit and then restart a list of macOS applications.
    
    Args:
        app_names: List of application names to restart
        dry_run: If True, only simulate actions without executing
    """
    for app_name in app_names:
        logger.info(f"--- Processing '{app_name}' ---")
        
        if dry_run:
            logger.info(f"[DRY RUN] Would quit and restart '{app_name}'")
            continue
        
        try:
            # Try to quit the app gracefully
            quit_command = f'quit app "{app_name}"'
            result = subprocess.run(
                ['osascript', '-e', quit_command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Sent quit command to '{app_name}'")
            else:
                logger.debug(f"Quit command returned code {result.returncode} (app may not be running)")
            
            time.sleep(3)  # Give app time to quit

            # Try to start the app
            subprocess.run(
                ['open', '-a', app_name],
                check=True,
                capture_output=True,
                timeout=10
            )
            logger.info(f"✓ Successfully restarted '{app_name}'")

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while processing '{app_name}'")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Application '{app_name}' not found or could not be started. Skipping.")
            logger.debug(f"Error details: {e}")
        except FileNotFoundError:
            logger.error("'osascript' or 'open' command not found. This script requires macOS.")
            break

def main(dry_run: bool = False, verbose: bool = False) -> int:
    """
    Main monitoring function.
    
    Args:
        dry_run: If True, only simulate actions without executing
        verbose: If True, enable debug logging
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    global logger
    logger = setup_logging(verbose)
    
    logger.info(f"WindowServer Memory Monitor v{VERSION}")
    logger.info("=" * 60)
    
    try:
        memory_threshold_gb, apps_to_restart = read_config()
    except SystemExit:
        return 1
    
    memory_threshold_bytes = memory_threshold_gb * 1024**3

    logger.info(f"Memory threshold: {memory_threshold_gb:.1f} GB")
    logger.info(f"Apps to monitor: {', '.join(apps_to_restart)}")
    
    if dry_run:
        logger.info("DRY RUN MODE - No apps will be restarted")
    
    logger.info("-" * 60)
    
    # Get WindowServer PID
    pid = get_process_pid(PROCESS_NAME)
    if not pid:
        logger.error(f"Could not find '{PROCESS_NAME}' process. Exiting.")
        return 1

    # Get memory usage
    memory_usage_bytes = get_memory_from_top(pid)
    if memory_usage_bytes is None:
        logger.error(f"Could not determine memory usage for '{PROCESS_NAME}'. Exiting.")
        return 1

    memory_usage_gb = memory_usage_bytes / (1024**3)
    logger.info(f"'{PROCESS_NAME}' memory usage: {memory_usage_gb:.2f} GB")

    # Check threshold and take action
    if memory_usage_bytes > memory_threshold_bytes:
        logger.warning(f"⚠️  ALERT: Memory usage ({memory_usage_gb:.2f} GB) exceeds threshold ({memory_threshold_gb:.1f} GB)")
        restart_apps(apps_to_restart, dry_run)
        logger.info("=" * 60)
        logger.info("Check complete - Actions taken")
        return 0
    else:
        logger.info(f"✓ Memory usage is within acceptable limit (under {memory_threshold_gb:.1f} GB)")
        logger.info("=" * 60)
        logger.info("Check complete - No action needed")
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Monitor WindowServer memory and restart apps when threshold exceeded",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Normal operation
  %(prog)s --dry-run          # Test without restarting apps
  %(prog)s --verbose          # Show debug information
  %(prog)s -v --dry-run       # Test with debug output
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate actions without actually restarting apps'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose (debug) logging'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {VERSION}'
    )
    
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run, verbose=args.verbose))
