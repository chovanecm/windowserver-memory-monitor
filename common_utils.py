#!/usr/bin/env python3
"""
Common utilities shared between WindowServer monitoring scripts.
"""

import subprocess
import re
from typing import Optional


def get_process_pid(process_name: str, timeout: int = 5) -> Optional[str]:
    """
    Gets the PID of a process using pgrep.
    
    Args:
        process_name: Name of the process to find
        timeout: Command timeout in seconds
    
    Returns:
        PID as string, or None if not found
    """
    try:
        result = subprocess.run(
            ['pgrep', '-n', process_name],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return None


def parse_memory_from_top_output(lines: list[str]) -> Optional[int]:
    """
    Parse memory usage from 'top' command output.
    
    Args:
        lines: Output lines from 'top' command
    
    Returns:
        Memory usage in bytes, or None if unable to parse
    """
    # Find header row containing column names
    header_index = next(
        (i for i, line in enumerate(lines) if 'PID' in line and 'COMMAND' in line),
        -1
    )
    
    if header_index == -1 or header_index + 1 >= len(lines):
        return None

    headers = re.split(r'\s+', lines[header_index].strip())
    mem_column_index = next(
        (i for i, header in enumerate(headers) if header == 'MEM'),
        -1
    )
    
    if mem_column_index == -1:
        return None

    process_line = lines[header_index + 1].strip()
    process_data = re.split(r'\s+', process_line)
    
    if mem_column_index >= len(process_data):
        return None
    
    mem_str = process_data[mem_column_index]
    
    # Parse memory value (e.g., "2.5G", "512M", "1024K")
    value_match = re.match(r'(\d+\.?\d*)', mem_str)
    if not value_match:
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


def get_memory_from_top(pid: str, timeout: int = 10) -> Optional[int]:
    """
    Gets the memory usage in bytes for a given PID by parsing 'top'.
    
    Args:
        pid: Process ID to check
        timeout: Command timeout in seconds
    
    Returns:
        Memory usage in bytes, or None if unable to determine
    """
    try:
        result = subprocess.run(
            ['top', '-l', '1', '-pid', pid],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        lines = result.stdout.strip().split('\n')
        return parse_memory_from_top_output(lines)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
            FileNotFoundError, ValueError, IndexError):
        return None
