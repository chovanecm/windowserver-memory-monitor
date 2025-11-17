# Quick Start Guide

Get up and running with WindowServer Memory Monitor in 5 minutes.

## Prerequisites

- macOS 10.14 or later
- Apps you want to monitor (e.g., DockDoor, AltTab)

## Installation (2 steps)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/mac-windowserver-memleak-workaround.git
cd mac-windowserver-memleak-workaround
```

### 2. Run the Interactive Wizard

```bash
python3 install.py
# OR
make wizard
```

The wizard will guide you through:
- Setting your memory threshold
- Selecting apps to monitor
- Configuring check interval
- Installing the service

That's it! The service is now running.

### Alternative: Manual Installation

If you prefer to configure manually:

```bash
# Edit config.ini
nano config.ini

# Install
make install
```

## Verify It's Working

```bash
# Check service status
make status

# View logs
make logs
```

You should see periodic checks logged every 10 minutes.

## Testing Before Use

Want to test without actually restarting apps?

```bash
make test
```

This runs in dry-run mode showing what would happen.

## Common Configurations

### For 16GB Macs with DockDoor
```ini
memory_threshold_gb = 2.5
apps_to_restart = DockDoor
```

### For 32GB+ Macs with multiple window managers
```ini
memory_threshold_gb = 4.0
apps_to_restart = DockDoor, alt-tab, Rectangle
```

### Aggressive monitoring
```ini
memory_threshold_gb = 2.0
apps_to_restart = DockDoor
```

## What Happens Next?

1. **Every 10 minutes**, the service checks WindowServer memory
2. **If threshold exceeded**, it:
   - Logs the event
   - Gracefully quits configured apps
   - Restarts them automatically
3. **All actions logged** to `~/Library/Logs/windowserver_monitor.out.log`

## Monitoring

### Watch logs in real-time
```bash
tail -f ~/Library/Logs/windowserver_monitor.out.log
```

### Check current WindowServer memory
Open **Activity Monitor** → Find **WindowServer** → Check **Memory** column

## Customization

### Change check interval

Edit the plist file (default: 10 minutes):

```bash
nano ~/Library/LaunchAgents/com.user.windowserver_monitor.plist
```

Find `StartInterval` and change from `600` (seconds) to your preference.

Then reload:
```bash
make uninstall && make install
```

## Troubleshooting

Not working? Run through these quick checks:

```bash
# 1. Is it running?
make status

# 2. Any errors?
cat ~/Library/Logs/windowserver_monitor.err.log

# 3. Manual test
python3 monitor_dockdoor.py --dry-run --verbose
```

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Uninstall

```bash
make uninstall
```

## Next Steps

- ⭐ Star the repo if it helps!
- 📝 Adjust threshold based on your usage
- 📊 Monitor logs to see if leaks are being caught
- 🐛 Report issues or suggest improvements

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/mac-windowserver-memleak-workaround/issues)
- **Documentation**: [Full README](README.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
