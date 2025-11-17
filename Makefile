.PHONY: install uninstall clean

# Configuration
PLIST_NAME = com.user.monitordockdoor.plist
PLIST_PATH = ~/Library/LaunchAgents/$(PLIST_NAME)
SCRIPT_NAME = monitor_dockdoor.py
CONFIG_NAME = config.ini

install:
	@echo "--- Installing WindowServer Memory Monitor Agent ---"
	@echo "1. Ensuring ~/Library/LaunchAgents directory exists..."
	@mkdir -p ~/Library/LaunchAgents

	@echo "2. Copying $(PLIST_NAME) to $(PLIST_PATH)..."
	@cp $(PLIST_NAME) $(PLIST_PATH)

	@echo "3. Unloading any existing agent (if present)..."
	@launchctl unload $(PLIST_PATH) 2>/dev/null || true

	@echo "4. Loading the new agent..."
	@launchctl load $(PLIST_PATH)

	@echo "5. Creating default $(CONFIG_NAME) if it doesn't exist..."
	@if [ ! -f $(CONFIG_NAME) ]; then \
		echo "[settings]" > $(CONFIG_NAME); \
		echo "memory_threshold_gb = 4.0" >> $(CONFIG_NAME); \
		echo "apps_to_restart = DockDoor, alt-tab" >> $(CONFIG_NAME); \
		echo "Default $(CONFIG_NAME) created. Review and adjust as needed." \
	fi

	@echo "--- Installation Complete ---"
	@echo "The agent will now run every 10 minutes."
	@echo "Check logs: tail -f ~/Library/Logs/com.user.monitordockdoor.out.log"
	@echo "To uninstall: make uninstall"

uninstall:
	@echo "--- Uninstalling WindowServer Memory Monitor Agent ---"
	@echo "1. Unloading agent (if present)..."
	@launchctl unload $(PLIST_PATH) 2>/dev/null || true

	@echo "2. Removing $(PLIST_NAME) from $(PLIST_PATH)..."
	@rm -f $(PLIST_PATH)

	@echo "--- Uninstallation Complete ---"
	@echo "The agent has been removed."

clean:
	@echo "--- Cleaning up local files ---"
	@rm -f $(CONFIG_NAME)
	@rm -f test_script.py
	@echo "--- Cleanup Complete ---"
