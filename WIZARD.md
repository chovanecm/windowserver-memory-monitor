# Installation Wizard Guide

The interactive installation wizard (`install.py`) provides a user-friendly way to configure and install the WindowServer Memory Monitor.

## Features

### 🎯 Smart Detection
- **Current Memory Usage**: Shows your current WindowServer memory usage
- **Suggested Threshold**: Recommends a threshold based on current usage
- **Auto-discover Apps**: Automatically finds installed apps that commonly cause leaks

### 🎨 User-Friendly Interface
- **Color-coded Output**: Easy-to-read colored terminal output
- **Step-by-step Guidance**: Clear progression through configuration
- **Validation**: Input validation to prevent configuration errors
- **Defaults**: Sensible defaults for quick setup

### ⚙️ Configuration Options

The wizard helps you configure:
1. **Memory Threshold** - When to trigger app restarts
2. **Applications** - Which apps to restart
3. **Check Interval** - How often to check memory
4. **Review** - Confirm before installation

## Running the Wizard

### Method 1: Direct Python
```bash
python3 install.py
```

### Method 2: Via Makefile
```bash
make wizard
```

### Method 3: Executable
```bash
./install.py
```

## What to Expect

### Step 1: Memory Threshold
```
═══════════════════════════════════════════════════
              Step 1: Memory Threshold
═══════════════════════════════════════════════════

Set the memory threshold for WindowServer. When this limit is
exceeded, the configured apps will be restarted.

ℹ  Current WindowServer memory usage: 2.31 GB
ℹ  Suggested threshold: 2.8 GB (current usage + 0.5 GB)

Common values:
  • 2.0 GB - Aggressive monitoring (16GB systems)
  • 3.0 GB - Balanced monitoring (most systems)
  • 4.0 GB - Relaxed monitoring (32GB+ systems)

Memory threshold (GB) [2.8]:
```

### Step 2: App Selection
```
═══════════════════════════════════════════════════
         Step 2: Applications to Restart
═══════════════════════════════════════════════════

Select which apps to restart when the threshold is exceeded.

Found these commonly problematic apps on your system:

  1. DockDoor
  2. alt-tab
  3. Rectangle

Would you like to monitor all of these apps? (Y/n):
```

### Step 3: Check Interval
```
═══════════════════════════════════════════════════
              Step 3: Check Interval
═══════════════════════════════════════════════════

How often should WindowServer memory be checked?

Common intervals:
  • 5 minutes  - Frequent checks
  • 10 minutes - Balanced (recommended)
  • 15 minutes - Less frequent

Check interval (minutes) [10]:
```

### Step 4: Review & Confirm
```
═══════════════════════════════════════════════════
            Step 4: Review Configuration
═══════════════════════════════════════════════════

Please review your configuration:

  Memory Threshold:   2.8 GB
  Apps to Monitor:    DockDoor, alt-tab, Rectangle
  Check Interval:     Every 10 minutes
  Install Location:   ~/.config/windowserver_monitor
  Log Location:       ~/Library/Logs/windowserver_monitor.out.log

Proceed with installation? (Y/n):
```

### Step 5: Installation
```
═══════════════════════════════════════════════════
                  Step 5: Installing
═══════════════════════════════════════════════════

[1] Configuration file created
✓ config.ini created

[2] Running installation
ℹ  This will install the service using the Makefile

╔════════════════════════════════════════════════════════╗
║   WindowServer Memory Monitor - Installation          ║
╚════════════════════════════════════════════════════════╝

✓ Found Python 3 at: /usr/bin/python3
...
```

### Success!
```
╔════════════════════════════════════════════════════════╗
║                                                        ║
║              ✓ Installation Complete!                 ║
║                                                        ║
╚════════════════════════════════════════════════════════╝

The WindowServer memory monitor is now running!
It will check every 10 minutes and restart apps
when WindowServer exceeds 2.8 GB.

📝 Useful commands:
  • View logs:     make logs
  • Check status:  make status
  • Test script:   python3 monitor_dockdoor.py --dry-run
  • Edit config:   nano ~/.config/windowserver_monitor/config.ini
  • Uninstall:     make uninstall

Would you like to view the logs now? (y/N):
```

## Wizard Features in Detail

### Automatic App Discovery
The wizard scans `/Applications` for these commonly problematic apps:
- DockDoor
- alt-tab / AltTab
- Rectangle
- BetterTouchTool
- Magnet
- Raycast
- Hyperswitch

### Smart Defaults
- **Memory Threshold**: Current usage + 0.5 GB (or 3.0 GB if detection fails)
- **Check Interval**: 10 minutes (balanced)
- **App Selection**: All detected apps enabled by default

### Input Validation
- Memory threshold must be positive number
- Check interval must be positive integer
- At least one app must be selected
- App names are preserved exactly as entered

### Error Handling
- Graceful handling of Ctrl+C (cancels installation)
- Validates Python version (3.6+ required)
- Checks for macOS (platform validation)
- Provides helpful error messages

### Customization Options
After auto-detection, you can:
- Select/deselect specific apps
- Add apps not automatically detected
- Override suggested threshold
- Change check interval

## Advantages Over Manual Configuration

| Feature | Manual Config | Wizard |
|---------|--------------|--------|
| Current memory detection | ❌ Manual check | ✅ Automatic |
| App discovery | ❌ Manual search | ✅ Automatic scan |
| Threshold suggestion | ❌ Guess | ✅ Smart calculation |
| Input validation | ❌ None | ✅ Built-in |
| Confirmation step | ❌ No | ✅ Review before install |
| Error prevention | ⚠️ Easy to misconfigure | ✅ Validated |

## Tips for Using the Wizard

1. **Let it detect**: The wizard's auto-detection is usually accurate
2. **Use suggested threshold**: Based on your current usage + buffer
3. **Start with recommended interval**: 10 minutes works for most users
4. **Review carefully**: Check the summary before confirming
5. **View logs after**: Optionally view logs to confirm it's working

## Re-running the Wizard

You can re-run the wizard to reconfigure:

```bash
# Uninstall current setup
make uninstall

# Run wizard again
python3 install.py
```

The wizard will overwrite `config.ini` but won't affect any logs.

## Troubleshooting

### "Python 3 not found"
Install Python 3 or Xcode Command Line Tools:
```bash
xcode-select --install
```

### "No apps found"
The wizard looks in `/Applications`. If your apps are elsewhere:
- Use manual app entry option in wizard
- Or edit `~/.config/windowserver_monitor/config.ini` after installation

### "Installation failed"
Check that you have write permissions:
```bash
ls -la ~/Library/LaunchAgents/
```

### Colors not working
Some terminals don't support ANSI colors. The wizard still works, just without colors.

## Manual Override

If you prefer not to use the wizard, you can still:
1. Edit `config.ini` manually
2. Run `make install`
3. Manually edit the plist for custom interval

The wizard is optional but recommended for first-time users!
