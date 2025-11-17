.PHONY: install uninstall test status logs help wizard reload

# --- Configuration ---
SCRIPT_DIR := $(shell pwd)
PLIST_NAME = cz.chovanecm.windowserver-monitor.plist
PLIST_DEST = $(HOME)/Library/LaunchAgents/$(PLIST_NAME)
PYTHON_PATH := $(shell which python3)
SCRIPT_PATH = $(SCRIPT_DIR)/monitor_windowserver.py
CONFIG_PATH = $(SCRIPT_DIR)/config.ini
LOG_FILE = $(HOME)/Library/Logs/windowserver-monitor.out.log
ERR_LOG_FILE = $(HOME)/Library/Logs/windowserver-monitor.err.log

# --- Targets ---

.DEFAULT_GOAL := help

help:
	@echo "WindowServer Memory Monitor - Makefile Commands"
	@echo "================================================"
	@echo ""
	@echo "  make wizard     - Run interactive installation wizard (RECOMMENDED)"
	@echo "  make install    - Install and start the service (manual)"
	@echo "  make reload     - Reload config after editing config.ini"
	@echo "  make uninstall  - Stop and remove the service"
	@echo "  make test       - Test the script without installing"
	@echo "  make status     - Check if service is installed (see README for periodic status explanation)"
	@echo "  make logs       - Show recent logs"
	@echo "  make help       - Show this help message"
	@echo ""
reload:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║   Reloading WindowServer Monitor Config               ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@launchctl unload $(PLIST_DEST) 2>/dev/null || true
	@launchctl load $(PLIST_DEST)
	@echo "✓ Config reloaded. Next run will use updated config.ini."
	@echo ""

install:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║   WindowServer Memory Monitor - Installation          ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@if [ -z "$(PYTHON_PATH)" ]; then \
		echo "❌ Error: Python 3 not found. Please install Python 3."; \
		echo "   Install via: xcode-select --install"; \
		exit 1; \
	fi
	@echo "✓ Found Python 3 at: $(PYTHON_PATH)"
	@echo ""
	@echo "1️⃣  Checking configuration..."
	@if [ ! -f "$(CONFIG_PATH)" ]; then \
		if [ -f "config.example.ini" ]; then \
			cp config.example.ini $(CONFIG_PATH); \
			echo "   → Created config.ini from config.example.ini"; \
			echo "   ⚠️  Please edit config.ini before proceeding"; \
			exit 1; \
		else \
			echo "❌ Neither config.ini nor config.example.ini found"; \
			exit 1; \
		fi; \
	fi
	@chmod +x $(SCRIPT_PATH)
	@echo "   → Using config at: $(CONFIG_PATH)"
	@echo ""
	@echo "2️⃣  Generating launchd agent..."
	@echo '<?xml version="1.0" encoding="UTF-8"?>' > $(PLIST_DEST)
	@echo '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">' >> $(PLIST_DEST)
	@echo '<plist version="1.0">' >> $(PLIST_DEST)
	@echo '<dict>' >> $(PLIST_DEST)
	@echo '    <key>Label</key>' >> $(PLIST_DEST)
	@echo '    <string>cz.chovanecm.windowserver-monitor</string>' >> $(PLIST_DEST)
	@echo '    <key>ProgramArguments</key>' >> $(PLIST_DEST)
	@echo '    <array>' >> $(PLIST_DEST)
	@echo '        <string>$(PYTHON_PATH)</string>' >> $(PLIST_DEST)
	@echo '        <string>$(SCRIPT_PATH)</string>' >> $(PLIST_DEST)
	@echo '    </array>' >> $(PLIST_DEST)
	@echo '    <key>RunAtLoad</key>' >> $(PLIST_DEST)
	@echo '    <true/>' >> $(PLIST_DEST)
	@echo '    <key>StartInterval</key>' >> $(PLIST_DEST)
	@echo '    <integer>600</integer>' >> $(PLIST_DEST)
	@echo '    <key>StandardOutPath</key>' >> $(PLIST_DEST)
	@echo '    <string>$(LOG_FILE)</string>' >> $(PLIST_DEST)
	@echo '    <key>StandardErrorPath</key>' >> $(PLIST_DEST)
	@echo '    <string>$(ERR_LOG_FILE)</string>' >> $(PLIST_DEST)
	@echo '</dict>' >> $(PLIST_DEST)
	@echo '</plist>' >> $(PLIST_DEST)
	@echo "   → $(PLIST_DEST)"
	@echo ""
	@echo "3️⃣  Installing and loading agent..."
	@mkdir -p $(HOME)/Library/LaunchAgents
	@mkdir -p $(HOME)/Library/Logs
	@launchctl unload $(PLIST_DEST) 2>/dev/null || true
	@launchctl load $(PLIST_DEST)
	@echo "   → Agent loaded successfully"
	@echo ""
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║              ✓ Installation Complete!                 ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "The service is now active and will check every 10 minutes."
	@echo ""
	@echo "📝 Configuration: $(CONFIG_PATH)"
	@echo "📊 Logs:          $(LOG_FILE)"
	@echo ""
	@echo "Next steps:"
	@echo "  • Edit config:  nano config.ini"
	@echo "  • View logs:    make logs"
	@echo "  • Check status: make status"
	@echo "  • Test script:  make test"
	@echo ""

uninstall:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║   WindowServer Memory Monitor - Uninstallation        ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "1️⃣  Unloading and removing agent..."
	@if launchctl list | grep -q "$(basename $(PLIST_NAME) .plist)"; then \
		launchctl unload $(PLIST_DEST) 2>/dev/null || true; \
		echo "   → Agent unloaded"; \
	else \
		echo "   → Agent was not loaded"; \
	fi
	@rm -f $(PLIST_DEST)
	@echo "   → Agent file removed"
	@echo ""
	@echo "Note: config.ini in your project directory is preserved."
	@echo ""
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║           ✓ Uninstallation Complete!                  ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Note: Log files preserved at ~/Library/Logs/"
	@echo "To remove logs: rm ~/Library/Logs/windowserver_monitor.*"
	@echo ""

test:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║        Testing WindowServer Memory Monitor            ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@if [ -z "$(PYTHON_PATH)" ]; then \
		echo "❌ Error: Python 3 not found."; \
		exit 1; \
	fi
	@echo "Running test with --dry-run and --verbose..."
	@echo ""
	@$(PYTHON_PATH) monitor_windowserver.py --dry-run --verbose
	@echo ""
	@echo "✓ Test complete (no apps were restarted)"
	@echo ""

status:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║            Service Status Check                       ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@if [ -f "$$HOME/Library/LaunchAgents/cz.chovanecm.windowserver-monitor.plist" ]; then \
		launchctl list | grep -q cz.chovanecm.windowserver-monitor && \
			echo "Service is RUNNING" || \
			echo "Service is INSTALLED but NOT LOADED (run 'make install' to load)"; \
	else \
		echo "Service is NOT INSTALLED (launchd job missing)"; \
	fi
	@echo ""
	@if [ -f "$(CONFIG_PATH)" ]; then \
		echo "Configuration:"; \
		grep -E "^(memory_threshold_gb|apps_to_restart)" $(CONFIG_PATH) | sed 's/^/  /'; \
	fi
	@echo ""

logs:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║              Recent Logs (last 30 lines)              ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@if [ -f "$(LOG_FILE)" ]; then \
		tail -30 $(LOG_FILE); \
	else \
		echo "No logs found at $(LOG_FILE)"; \
		echo "The service may not have run yet."; \
	fi
	@echo ""
	@echo "To follow logs in real-time: tail -f $(LOG_FILE)"
	@echo ""

wizard:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║        Starting Interactive Installation Wizard       ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@if [ -z "$(PYTHON_PATH)" ]; then \
		echo "❌ Error: Python 3 not found."; \
		exit 1; \
	fi
	@$(PYTHON_PATH) install.py