.PHONY: install uninstall

# --- Configuration ---
# The directory where the script and config will be installed.
INSTALL_DIR = $(HOME)/.config/windowserver_monitor

# The name of the launchd agent plist file.
PLIST_NAME = com.user.windowserver_monitor.plist

# The final destination for the plist file.
PLIST_DEST = $(HOME)/Library/LaunchAgents/$(PLIST_NAME)

# The path to the python executable. We use 'which' to find it automatically.
# We use the shell function to run this once and store it.
PYTHON_PATH := $(shell which python3)

# The final path of the installed script.
SCRIPT_PATH = $(INSTALL_DIR)/monitor_dockdoor.py


# --- Targets ---

install:
	@echo "--- Installing WindowServer Memory Monitor ---"

	@echo "1. Creating install directory at $(INSTALL_DIR)..."
	@mkdir -p $(INSTALL_DIR)

	@echo "2. Copying script and creating default config..."
	@cp monitor_dockdoor.py $(INSTALL_DIR)/
	@if [ ! -f "$(INSTALL_DIR)/config.ini" ]; then \
		cp config.ini $(INSTALL_DIR)/; \
		echo "Default config.ini copied. You can edit it at $(INSTALL_DIR)/config.ini"; \
	else \
		echo "Existing config.ini found at $(INSTALL_DIR). Leaving it untouched."; \
	fi

	@echo "3. Generating new $(PLIST_NAME) with correct paths..."
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
	@echo '    <true/>' >> $(PLIST_NAME)
	@echo '    <key>StartInterval</key>' >> $(PLIST_NAME)
	@echo '    <integer>600</integer>' >> $(PLIST_NAME)
	@echo '    <key>StandardOutPath</key>' >> $(PLIST_NAME)
	@echo '    <string>$(HOME)/Library/Logs/windowserver_monitor.out.log</string>' >> $(PLIST_NAME)
	@echo '    <key>StandardErrorPath</key>' >> $(PLIST_NAME)
	@echo '    <string>$(HOME)/Library/Logs/windowserver_monitor.err.log</string>' >> $(PLIST_NAME)
	@echo '</dict>' >> $(PLIST_NAME)
	@echo '</plist>' >> $(PLIST_NAME)

	@echo "4. Installing and loading the agent..."
	@cp $(PLIST_NAME) $(PLIST_DEST)
	@launchctl unload $(PLIST_DEST) 2>/dev/null || true
	@launchctl load $(PLIST_DEST)
	@rm $(PLIST_NAME)

	@echo ""
	@echo "--- Installation Complete ---"
	@echo "The agent is now active and will run every 10 minutes."
	@echo "Logs are at: ~/Library/Logs/windowserver_monitor.out.log"
	@echo "To uninstall, run: make uninstall"

uninstall:
	@echo "--- Uninstalling WindowServer Memory Monitor ---"
	@echo "1. Unloading and removing agent..."
	@launchctl unload $(PLIST_DEST) 2>/dev/null || true
	@rm -f $(PLIST_DEST)

	@echo "2. Removing installed files from $(INSTALL_DIR)..."
	@rm -rf $(INSTALL_DIR)

	@echo "Note: Log files in ~/Library/Logs/ have not been removed."
	@echo "--- Uninstallation Complete ---"