# WindowServer Memory Monitor

**Automatically monitor and mitigate macOS WindowServer memory leaks**

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

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/mac-windowserver-memleak-workaround.git
cd mac-windowserver-memleak-workaround

# Option 1: Run the interactive wizard (recommended)
python3 install.py

# Option 2: Manual configuration
cp config.example.ini config.ini
nano config.ini
make install
```

Your `config.ini` is gitignored and stays local to your machine.

## Configuration

```bash
nano ~/.config/windowserver_monitor/config.ini
```

```ini
[settings]
memory_threshold_gb = 3.0
apps_to_restart = DockDoor, alt-tab
```

After editing: `make uninstall && make install`

## Usage

```bash
make logs          # View logs
make status        # Check if running
make test          # Test without installing
make uninstall     # Remove service
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed help with common issues.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Created to help macOS users experiencing WindowServer memory leaks from third-party window management and preview tools.

---

**Found this helpful?** ⭐ Star the repo to help others discover it!