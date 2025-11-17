
# WindowServer Memory Monitor

Automatically monitor and mitigate macOS WindowServer memory leaks.

---

## 🚀 Quick Start (Recommended)

```bash
git clone https://github.com/YOUR_USERNAME/mac-windowserver-memleak-workaround.git
cd mac-windowserver-memleak-workaround
make wizard      # Interactive setup (recommended)
make status      # Check service status (see below)
make logs        # View recent logs
```

## What Does This Do?

This tool runs a background check (every 10 minutes) on your Mac’s WindowServer memory usage. If it gets too high, it automatically restarts the apps you specify—no root required.

**Typical symptoms:**
- System slowdowns, laggy UI
- WindowServer using 4GB+ RAM
- Need to restart window managers (DockDoor, AltTab, etc.)

## How It Works

1. A Python script checks WindowServer memory every 10 minutes (configurable)
2. If usage exceeds your threshold, it restarts the apps you list in `config.ini`
3. All actions are logged for transparency
4. Managed by macOS `launchd` (user-level, no sudo)

## Requirements

- macOS 10.14 or later (tested on macOS 13+)
- Python 3.6+ (pre-installed on most Macs)

## Installation & Configuration

### Option 1: Interactive Wizard (Recommended)

```bash
make wizard
# Follows prompts to set up config.ini and install the service
```

### Option 2: Manual Setup

```bash
cp config.example.ini config.ini
nano config.ini   # Edit threshold and app list
make install
```

Your `config.ini` is gitignored and stays local to your machine.

#### Example config.ini
```ini
[settings]
memory_threshold_gb = 3.0
apps_to_restart = DockDoor, alt-tab
```

## Usage & Management

```bash
make status      # Check if service is installed (see note below)
make logs        # Show last 30 lines of logs
make test        # Run a dry test (no apps restarted)
make uninstall   # Remove the service
make reload      # Reload config after editing config.ini
```

### ⚠️ Service Status Explained

This tool runs **periodically** (every 10 minutes) and then exits. `make status` checks if the launchd job is installed—not if it’s running right now. If you see:

- `Service is RUNNING`: The launchd job is installed and will run as scheduled.
- `Service is NOT running`: The job may be installed but not currently executing (normal for periodic jobs). If you just installed, wait up to 10 minutes for the first run.

## Updating Configuration

1. Edit `config.ini` (change threshold or app list)
2. Run `make reload` to apply changes

## Troubleshooting

- **Apps not restarting?**
	- App names must match exactly (case-sensitive, as in /Applications)
	- Lower the threshold to test
	- Check logs with `make logs`
- **Service not running?**
	- Run `make install` or `make wizard` again
	- Wait up to 10 minutes for the first run
- **Manual test:**
	- `python3 monitor_windowserver.py --dry-run --verbose`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Found this helpful?** ⭐ Star the repo to help others discover it!