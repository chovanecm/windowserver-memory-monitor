# Changelog

All notable changes to WindowServer Memory Monitor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-17

### Added - Initial Release

#### Interactive Installation Wizard
- Beautiful terminal-based installation wizard (`install.py`)
- Auto-detection of current WindowServer memory usage
- Smart threshold recommendations based on system state
- Automatic discovery of installed problematic apps
- Interactive configuration for threshold, apps, and check interval
- Input validation and error handling
- Color-coded terminal output for better UX
- Review step before installation
- Automated installation process
- Integration with Makefile (`make wizard`)

#### Core Features
- Automatic monitoring of WindowServer memory usage via `top` command parsing
- Configurable memory threshold (GB)
- Support for multiple apps to restart when threshold exceeded
- Graceful quit and restart of configured applications
- macOS launchd integration for automatic background operation
- User-level service (no sudo required)

#### Configuration
- INI-based configuration file
- Configurable memory threshold
- Comma-separated list of apps to monitor
- Example configuration file included

#### Installation & Management
- Makefile with install/uninstall targets
- Automatic service installation and configuration
- Preserves existing config during upgrades
- Clean uninstall with optional log retention

#### Monitoring & Logging
- Detailed logging to `~/Library/Logs/windowserver_monitor.out.log`
- Error logging to `~/Library/Logs/windowserver_monitor.err.log`
- Timestamped log entries
- Clear status messages for all operations

#### CLI Features
- `--dry-run` mode for testing without restarting apps
- `--verbose` mode for debug output
- `--version` flag
- CLI help text with examples

#### Developer Features
- Type hints throughout codebase
- Comprehensive docstrings
- Error handling with proper exit codes
- Timeout protection on subprocess calls
- PEP 8 compliant code

#### Documentation
- Comprehensive README with problem/solution explanation
- Quick Start Guide (QUICKSTART.md)
- Troubleshooting Guide (TROUBLESHOOTING.md)
- Contributing Guidelines (CONTRIBUTING.md)
- GitHub issue templates (bug report, feature request)
- Pull request template
- MIT License

#### Project Infrastructure
- `.gitignore` for Python and macOS
- `requirements.txt` (no external dependencies)
- Example configuration file
- Makefile with help, test, status, and logs targets

### Technical Details
- Python 3.6+ compatible
- Uses only Python standard library (no external dependencies)
- Supports macOS 10.14+
- Memory parsing handles K/M/G units correctly
- Robust subprocess handling with timeouts

---

## Future Considerations

See [GitHub Issues](https://github.com/YOUR_USERNAME/mac-windowserver-memleak-workaround/issues) for planned features and enhancements.

### Ideas for Future Versions
- GUI configuration tool
- Notification center alerts when threshold exceeded
- Historical memory usage graphs
- Support for custom restart commands per app
- Web dashboard for monitoring
- Homebrew formula for easier installation
- Multiple threshold tiers with different actions
- Integration with system notification preferences

---

[1.0.0]: https://github.com/YOUR_USERNAME/mac-windowserver-memleak-workaround/releases/tag/v1.0.0
