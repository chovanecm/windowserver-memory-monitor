# WindowServer Memory Leak Workaround for DockDoor

This project contains a script and a macOS `launchd` agent to automatically monitor the `WindowServer` process for excessive memory usage—a symptom often associated with apps like DockDoor—and restart the application to reclaim the memory.

This solution works **without requiring `sudo` or root access** by intelligently parsing the output of the `top` command.

## The Problem

Certain applications can cause the macOS `WindowServer` process to leak memory over time. The "Memory" column in Activity Monitor shows this value growing, leading to system slowdowns. A common workaround is to periodically quit and restart the application suspected of causing the leak. This agent automates that workaround.

## The Solution

This solution uses a combination of a Python script and a standard, user-level `launchd` agent:

1.  **`monitor_dockdoor.py`**: A Python script that runs the `top` command to get the memory usage of `WindowServer` that matches the value shown in Activity Monitor. If it exceeds a predefined threshold (e.g., 4 GB), it gracefully quits and restarts the `DockDoor` application.
2.  **`com.user.monitordockdoor.plist`**: A `launchd` property list file that configures macOS to run the Python script automatically in the background as the logged-in user. It is set to run upon login and repeat every 10 minutes.

## Files

- `monitor_dockdoor.py`: The core monitoring and restarting logic (uses `top`).
- `com.user.monitordockdoor.plist`: The user-level `launchd` agent configuration.
- `README.md`: This documentation file.

## Setup

The agent has been configured and installed. The steps taken were:

1.  **Agent Configuration**: The `.plist` file was moved to the user's `LaunchAgents` directory.
    ```bash
    mkdir -p ~/Library/LaunchAgents
    mv com.user.monitordockdoor.plist ~/Library/LaunchAgents/
    ```
2.  **Agent Loading**: The `launchd` agent was loaded into the system, starting the monitoring process.
    ```bash
    launchctl load ~/Library/LaunchAgents/com.user.monitordockdoor.plist
    ```

## Usage and Verification

The agent runs automatically in the background. You do not need to do anything to start it.

To check if the agent is running and see its output, you can monitor its log file. Open a terminal and run:

```bash
tail -f ~/Library/Logs/com.user.monitordockdoor.out.log
```

You will see a new entry every 10 minutes with the current memory usage of `WindowServer`.

## Managing the Agent

You can manually stop and start the agent at any time.

**To stop the agent:**

```bash
launchctl unload ~/Library/LaunchAgents/com.user.monitordockdoor.plist
```

**To start the agent again:**

```bash
launchctl load ~/Library/LaunchAgents/com.user.monitordockdoor.plist
```

The agent will also start automatically on your next login or system reboot.

## Configuration

If you need to adjust the settings, you can edit the following files:

- **To change the memory threshold**:
  - Edit the `monitor_dockdoor.py` script.
  - Change the `MEMORY_THRESHOLD_GB` variable to your desired value in gigabytes.

- **To change the check interval**:
  - Edit the `~/Library/LaunchAgents/com.user.monitordockdoor.plist` file.
  - Find the `StartInterval` key and change the following integer to the desired number of seconds.
    ```xml
    <key>StartInterval</key>
    <integer>600</integer> <!-- 600 seconds = 10 minutes -->
    ```
  - After editing the `.plist` file, you must unload and reload the agent for the changes to take effect.