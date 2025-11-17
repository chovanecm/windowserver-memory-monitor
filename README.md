# WindowServer Memory Monitor

<p align="center">
  <strong>Automatically monitor and mitigate macOS WindowServer memory leaks</strong>
</p>

<p align="center">
  <a href="#the-problem">Problem</a> •
  <a href="#the-solution">Solution</a> •
  <a href="#installation">Installation</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#usage">Usage</a> •
  <a href="#troubleshooting">Troubleshooting</a>
</p>

---

## The Problem

Do you experience any of these issues on macOS?

- 🐌 System slowdowns and laggy UI after extended use
- 💾 WindowServer process consuming 4GB, 8GB, or even more RAM
- 🔄 Need to restart apps like **DockDoor**, **AltTab**, or similar window managers regularly
- 😤 Frustration with memory leaks that require manual intervention

**You're not alone.** Certain third-party apps that integrate deeply with the macOS window system can trigger memory leaks in the `WindowServer` process, leading to degraded performance over time.

## The Solution

This lightweight background service automatically:

✅ **Monitors** WindowServer memory usage (matching Activity Monitor values)  
✅ **Detects** when memory exceeds your configured threshold  
✅ **Restarts** problematic apps gracefully to reclaim memory  
✅ **Runs** automatically in the background via macOS `launchd`  
✅ **Requires** no root/sudo access—runs as your user  

### How It Works

1. **Python monitoring script** checks WindowServer memory every 10 minutes (configurable)
2. **Parses `top` output** to get accurate memory readings
3. **Gracefully quits and restarts** configured apps when threshold is exceeded
4. **Logs all activity** for transparency and debugging

## Features

- 🎯 **Configurable**: Set your own memory threshold and app list
- 🔒 **Safe**: No sudo required, user-level permissions only
- 📊 **Transparent**: Full logging to track all actions
- ⚡ **Lightweight**: Minimal resource usage, checks only every 10 minutes
- 🔧 **Easy management**: Simple `make install` and `make uninstall`

## Requirements

- macOS 10.14 or later (tested on macOS 13+)
- Python 3.6+ (pre-installed on modern macOS)
- Apps you want to monitor (e.g., DockDoor, AltTab)

## Installation

### Option 1: Interactive Wizard (Recommended)

The easiest way to get started:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/mac-windowserver-memleak-workaround.git
cd mac-windowserver-memleak-workaround

# Run the interactive installation wizard
python3 install.py
```

The wizard will:
- 🔍 Detect your current WindowServer memory usage
- 🎯 Help you set an appropriate threshold
- 🔎 Find installed apps that commonly cause leaks
- ⚙️  Configure check interval
- ✅ Install and start the service automatically

### Option 2: Quick Install (Advanced)

If you prefer to configure manually:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/mac-windowserver-memleak-workaround.git
cd mac-windowserver-memleak-workaround

# Edit config.ini with your settings
nano config.ini

# Install and start the service
make install
```

That's it! The service is now running in the background.

### What Gets Installed

- **Script**: `~/.config/windowserver_monitor/monitor_dockdoor.py`
- **Config**: `~/.config/windowserver_monitor/config.ini`
- **Launch Agent**: `~/Library/LaunchAgents/com.user.windowserver_monitor.plist`
- **Logs**: `~/Library/Logs/windowserver_monitor.out.log`

## Configuration

Edit the configuration file to customize behavior:

```bash
nano ~/.config/windowserver_monitor/config.ini
```

### Configuration Options

```ini
[settings]
# Memory threshold in gigabytes (default: 3.0)
memory_threshold_gb = 3.0

# Comma-separated list of apps to restart
# Common culprits: DockDoor, alt-tab, Rectangle, etc.
apps_to_restart = DockDoor, alt-tab
```

**After editing**, restart the service:

```bash
make uninstall && make install
```

### Adjusting Check Interval

The default check interval is 10 minutes. To change it:

1. Edit `~/Library/LaunchAgents/com.user.windowserver_monitor.plist`
2. Modify the `StartInterval` value (in seconds)
3. Reload: `launchctl unload ~/Library/LaunchAgents/com.user.windowserver_monitor.plist && launchctl load ~/Library/LaunchAgents/com.user.windowserver_monitor.plist`

## Usage

### Viewing Logs

Monitor real-time activity:

```bash
tail -f ~/Library/Logs/windowserver_monitor.out.log
```

### Manual Test Run

Test the script without installing:

```bash
python3 monitor_dockdoor.py
```

### Managing the Service

**Uninstall completely:**
```bash
make uninstall
```

**Reinstall:**
```bash
make install
```

**Check if running:**
```bash
launchctl list | grep windowserver_monitor
```

## How to Verify It's Working

1. **Check the service is loaded:**
   ```bash
   launchctl list | grep windowserver_monitor
   ```
   You should see `com.user.windowserver_monitor` in the output.

2. **View the logs:**
   ```bash
   cat ~/Library/Logs/windowserver_monitor.out.log
   ```
   You should see periodic memory checks logged.

3. **Trigger manually** (optional):
   ```bash
   launchctl start com.user.windowserver_monitor
   ```

## Troubleshooting

### The service isn't running

```bash
# Check if loaded
launchctl list | grep windowserver_monitor

# If not loaded, reinstall
make install
```

### No apps are being restarted despite high memory

- Verify app names in `config.ini` match exactly (case-sensitive)
- Check apps are actually running
- Lower the threshold temporarily to test

### Permission denied errors

This script runs as your user—no sudo needed. If you see permission errors, verify:
```bash
ls -la ~/.config/windowserver_monitor/
```

### Can't find Python

Ensure Python 3 is installed:
```bash
which python3
python3 --version
```

## Contributing

Contributions are welcome! Please feel free to:

- 🐛 Report bugs by opening an issue
- 💡 Suggest features or improvements
- 🔧 Submit pull requests

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Why This Solution?

- **No kernel extensions** or system modifications
- **No sudo required** - runs with user permissions
- **Automatic and hands-off** - set it and forget it
- **Transparent** - all actions are logged
- **Customizable** - configure for your specific needs

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by the many macOS users experiencing WindowServer memory leaks with third-party window management tools. This solution automates the manual workaround of restarting these apps.

---

**Found this helpful?** ⭐ Star the repo to help others discover it!