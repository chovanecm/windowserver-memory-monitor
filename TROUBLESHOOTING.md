# Troubleshooting Guide

This guide helps resolve common issues with WindowServer Memory Monitor.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Service Not Running](#service-not-running)
- [Apps Not Restarting](#apps-not-restarting)
- [Memory Detection Issues](#memory-detection-issues)
- [Permission Problems](#permission-problems)
- [General Debugging](#general-debugging)

---

## Installation Issues

### "make: command not found"

**Solution**: `make` is not installed. Install Xcode Command Line Tools:
```bash
xcode-select --install
```

### "Permission denied" during installation

**Solution**: The installation runs as your user—no sudo needed. Check directory permissions:
```bash
ls -la ~/.config/
mkdir -p ~/.config/windowserver_monitor
```

---

## Service Not Running

### Check if the service is loaded

```bash
launchctl list | grep windowserver_monitor
```

**Expected output**: You should see `com.user.windowserver_monitor`

**If not listed**: Reinstall the service:
```bash
make uninstall
make install
```

### Service crashes immediately

Check error logs:
```bash
cat ~/Library/Logs/windowserver_monitor.err.log
```

Common causes:
- Python not found: Verify with `which python3`
- Config file missing: Check `~/.config/windowserver_monitor/config.ini`
- Invalid config syntax: Review config file format

---

## Apps Not Restarting

### App names don't match

App names are **case-sensitive** and must match exactly.

**Check app name**:
```bash
ls /Applications/ | grep -i dockdoor
```

**Correct examples**:
- `DockDoor` ✓
- `alt-tab` ✓ (note lowercase)
- `Rectangle` ✓

**Incorrect examples**:
- `dockdoor` ✗ (wrong case)
- `Alt-Tab` ✗ (wrong case)
- `AltTab` ✗ (no hyphen)

### App is not installed

The script will skip apps that aren't found. Check logs:
```bash
tail -20 ~/Library/Logs/windowserver_monitor.out.log
```

Look for: `Application 'AppName' not found. Skipping restart.`

### Threshold never reached

Your threshold might be too high. Check current WindowServer memory:

1. Open **Activity Monitor**
2. Find **WindowServer** process
3. Look at **Memory** column (not CPU)
4. Compare with your threshold in `config.ini`

**Adjust threshold**:
```bash
nano ~/.config/windowserver_monitor/config.ini
# Lower the memory_threshold_gb value
# Then reload:
make uninstall && make install
```

---

## Memory Detection Issues

### Memory readings seem incorrect

**Test manually**:
```bash
python3 ~/.config/windowserver_monitor/monitor_dockdoor.py --verbose
```

This shows detailed memory parsing. Compare with Activity Monitor.

### "Could not find WindowServer"

WindowServer should always be running. This error suggests:
- System issue: Try restarting your Mac
- Script error: File a bug report

---

## Permission Problems

### "Operation not permitted"

The script should NOT need sudo. If you see this:

1. **Don't run with sudo** - this can cause permission conflicts
2. Check the script is in your home directory: `~/.config/windowserver_monitor/`
3. Verify the launchd agent runs as your user

### App won't quit/restart

Some apps may require accessibility permissions. Grant them:

1. **System Settings** → **Privacy & Security** → **Accessibility**
2. Add your **Terminal** or **Python** (if prompted)

---

## General Debugging

### Enable verbose logging

Run the script manually with debug output:
```bash
python3 ~/.config/windowserver_monitor/monitor_dockdoor.py --verbose
```

### Test without actually restarting apps

Use dry-run mode to see what would happen:
```bash
python3 ~/.config/windowserver_monitor/monitor_dockdoor.py --dry-run --verbose
```

### Check all logs

```bash
# Standard output log
cat ~/Library/Logs/windowserver_monitor.out.log

# Error log
cat ~/Library/Logs/windowserver_monitor.err.log

# System log (advanced)
log show --predicate 'process == "launchd"' --last 1h | grep windowserver_monitor
```

### Verify configuration

```bash
cat ~/.config/windowserver_monitor/config.ini
```

Ensure:
- `memory_threshold_gb` is a positive number
- `apps_to_restart` has at least one app
- No syntax errors (equal signs, brackets, etc.)

### Manually trigger a check

```bash
launchctl start com.user.windowserver_monitor
```

Then check the logs immediately:
```bash
tail -f ~/Library/Logs/windowserver_monitor.out.log
```

---

## Still Having Issues?

### Gather diagnostic information

```bash
# System info
sw_vers

# Python version
python3 --version

# Service status
launchctl list | grep windowserver_monitor

# Recent logs
tail -50 ~/Library/Logs/windowserver_monitor.out.log

# Config file
cat ~/.config/windowserver_monitor/config.ini

# Manual test run
python3 ~/.config/windowserver_monitor/monitor_dockdoor.py --dry-run --verbose
```

### Report a bug

Create an issue on GitHub with:
- All diagnostic information above
- Description of the problem
- Expected vs. actual behavior
- Steps you've already tried

---

## Tips for Success

1. **Start conservative**: Use a higher threshold (4-5 GB) initially
2. **Monitor logs**: Check logs after installation to ensure it's working
3. **Test manually first**: Run the script with `--dry-run` to verify detection
4. **One app at a time**: Start with one app in config, then add more
5. **Check Activity Monitor**: Understand your typical WindowServer usage patterns

---

## Common Workflows

### I want to test if it's working

```bash
# 1. Check service is running
launchctl list | grep windowserver_monitor

# 2. View recent activity
tail -20 ~/Library/Logs/windowserver_monitor.out.log

# 3. Manually trigger (doesn't wait 10 minutes)
launchctl start com.user.windowserver_monitor

# 4. Watch the logs live
tail -f ~/Library/Logs/windowserver_monitor.out.log
```

### I want to change the threshold

```bash
# 1. Edit config
nano ~/.config/windowserver_monitor/config.ini

# 2. Reload service
make uninstall && make install

# 3. Verify new setting
tail -5 ~/Library/Logs/windowserver_monitor.out.log
```

### I want to completely remove it

```bash
# Uninstall everything
make uninstall

# Remove logs (optional)
rm ~/Library/Logs/windowserver_monitor.*

# Remove installed files (optional)
rm -rf ~/.config/windowserver_monitor/
```
