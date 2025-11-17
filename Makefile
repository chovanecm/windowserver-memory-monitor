.PHONY: install uninstall test status logs help wizard

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
	@echo "  make wizard     - Run interactive installation wizard (recommended)"
	@echo "  make install    - Install and start the service"
	@echo "  make uninstall  - Stop and remove the service"
	@echo "  make test       - Test the script without installing"
	@echo "  make status     - Check if service is running"
	@echo "  make logs       - Show recent logs"
	@echo "  make help       - Show this help message"
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
		echo "❌ config.ini not found. Please create it first."; \
		exit 1; \
	fi
	@chmod +x $(SCRIPT_PATH)
	@echo "   → Using config at: $(CONFIG_PATH)"
	@echo ""
	@echo "2️⃣  Generating launchd agent..."
	@echo '<?xml version="1.0" encoding="UTF-8"?>' > $(PLIST_NAME)
	@echo '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">' >> $(PLIST_NAME)
	@echo '<plist version="1.0">' >> $(PLIST_NAME)
	@echo '<dict>' >> $(PLIST_NAME)
	@echo '    <key>Label</key>' >> $(PLIST_NAME)
	@echo '    <string>$(PLIST_NAME)</string>' >> $(PLIST_NAME)
	@echo '    <key>ProgramArguments</key>' >> $(PLIST_NAME)
	@echo '    <array>' >> $(PLIST_NAME)
	@echo '        <string>$(PYTHON_PATH)</string>' >> $(PLIST_NAME)
	@echo '        <string>$(SCRIPT_PATH)</string>' >> $(PLIST_NAME)
	@echo '    </array>' >> $(PLIST_NAME)
	@echo '    <key>RunAtLoad</key>' >> $(PLIST_NAME)
	@echo '    <key>RunAtLoad</key>' >> $(PLIST_NAME)
	@echo '    <true/>' >> $(PLIST_NAME)
	@echo '    <key>StartInterval</key>' >> $(PLIST_NAME)
	@echo '    <integer>600</integer>' >> $(PLIST_NAME)
	@echo '    <key>StandardOutPath</key>' >> $(PLIST_NAME)
	@echo '    <string>$(LOG_FILE)</string>' >> $(PLIST_NAME)
	@echo '    <key>StandardErrorPath</key>' >> $(PLIST_NAME)
	@echo '    <string>$(ERR_LOG_FILE)</string>' >> $(PLIST_NAME)
	@echo '</dict>' >> $(PLIST_NAME)
	@echo '</plist>' >> $(PLIST_NAME)
	@echo "   → $(PLIST_NAME)"
	@echo ""
	@echo "3️⃣  Installing and loading agent..."
	@mkdir -p $(HOME)/Library/LaunchAgents
	@mkdir -p $(HOME)/Library/Logs
	@cp $(PLIST_NAME) $(PLIST_DEST)
	@launchctl unload $(PLIST_DEST) 2>/dev/null || true
	@launchctl load $(PLIST_DEST)
	@rm $(PLIST_NAME)
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
	@echo "║            Service Status Check                        ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@if launchctl list | grep -q "$(basename $(PLIST_NAME) .plist)"; then \
		echo "✓ Service is RUNNING"; \
		echo ""; \
		launchctl list | grep "$(basename $(PLIST_NAME) .plist)"; \
	else \
		echo "✗ Service is NOT running"; \
		echo ""; \
		echo "To start: make install"; \
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