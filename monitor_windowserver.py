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
from common_utils import get_process_pid, get_memory_from_top

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

def get_process_memory(process_name: str) -> Optional[int]:
    """
    Gets the memory usage in bytes for a named process.
    
    Args:
        process_name: Name of the process to check
    
    Returns:
        Memory usage in bytes, or None if unable to determine
    """
    pid = get_process_pid(process_name)
    if not pid:
        logger.warning(f"Process '{process_name}' not found.")
        return None
    
    logger.debug(f"Found {process_name} with PID: {pid}")
    
    memory_bytes = get_memory_from_top(pid)
    if memory_bytes is None:
        logger.error(f"Could not determine memory usage for '{process_name}'.")
    
    return memory_bytes

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
        
        # Step 1: Try to quit the app
        quit_succeeded = False
        try:
            quit_command = f'quit app "{app_name}"'
            result = subprocess.run(
                ['osascript', '-e', quit_command],
                capture_output=True,
                text=True,
                timeout=30  # Increased timeout for quit
            )
            
            if result.returncode == 0:
                logger.info(f"Sent quit command to '{app_name}'")
                quit_succeeded = True
            else:
                logger.debug(f"Quit command returned code {result.returncode} (app may not be running)")
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout waiting for '{app_name}' to quit (continuing with restart anyway)")
        except FileNotFoundError:
            logger.error("'osascript' command not found. This script requires macOS.")
            break
        
        # Wait for app to fully quit
        time.sleep(5)
        
        # Step 2: Try to start the app (always attempt, even if quit failed/timed out)
        # Use launchctl asuser to ensure we run in user GUI context (needed for launchd)
        try:
            # Get the user ID for launchctl asuser
            uid = os.getuid()
            
            # Try using launchctl asuser first (works better from launchd)
            result = subprocess.run(
                ['launchctl', 'asuser', str(uid), 'open', '-a', app_name],
                capture_output=True,
                timeout=20
            )
            
            # If launchctl asuser fails, fall back to direct open
            if result.returncode != 0:
                subprocess.run(
                    ['open', '-a', app_name],
                    check=True,
                    capture_output=True,
                    timeout=20
                )
            
            logger.info(f"✓ Successfully restarted '{app_name}'")
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout waiting for '{app_name}' to launch")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Application '{app_name}' not found or could not be started. Skipping.")
            logger.debug(f"Error details: {e}")
        except FileNotFoundError:
            logger.error("'open' command not found. This script requires macOS.")
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
    
    try:
        memory_threshold_gb, apps_to_restart = read_config()
    except SystemExit:
        return 1
    
    memory_threshold_bytes = memory_threshold_gb * 1024**3
    
    # Get memory usage
    memory_usage_bytes = get_process_memory(PROCESS_NAME)
    if memory_usage_bytes is None:
        logger.error(f"Could not determine memory usage for '{PROCESS_NAME}'. Exiting.")
        return 1

    memory_usage_gb = memory_usage_bytes / (1024**3)
    threshold_exceeded = memory_usage_bytes > memory_threshold_bytes

    # Log banner and details when verbose OR when action is needed
    if verbose or threshold_exceeded:
        logger.info(f"WindowServer Memory Monitor v{VERSION}")
        logger.info("=" * 60)
        logger.info(f"Memory threshold: {memory_threshold_gb:.1f} GB")
        logger.info(f"Apps to monitor: {', '.join(apps_to_restart)}")
        if dry_run:
            logger.info("DRY RUN MODE - No apps will be restarted")
        logger.info("-" * 60)
        logger.info(f"'{PROCESS_NAME}' memory usage: {memory_usage_gb:.2f} GB")

    # Check threshold and take action
    if threshold_exceeded:
        logger.warning(f"⚠️  ALERT: WindowServer memory ({memory_usage_gb:.2f} GB) exceeds threshold ({memory_threshold_gb:.1f} GB)")
        restart_apps(apps_to_restart, dry_run)
        logger.info("=" * 60)
        logger.info("Check complete - Actions taken")
        return 0
    else:
        # Silent success - no action needed
        if verbose:
            logger.info(f"✓ Memory usage is within acceptable limit (under {memory_threshold_gb:.1f} GB)")
            logger.info("=" * 60)
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
