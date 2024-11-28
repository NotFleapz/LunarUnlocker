import time
import os
import subprocess
import sys
import psutil

# Function to install a package using pip if it's not installed
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required dependencies
def install_requirements():
    try:
        import psutil
    except ImportError:
        print("psutil not found. Installing...")
        install('psutil')

# Check if psutil is installed
install_requirements()

def get_latest_log_file(log_dir):
    """Returns the most recent log file in the specified directory."""
    try:
        # List all files in the log directory
        log_files = os.listdir(log_dir)
        
        if not log_files:
            print("No files found in the log directory.")
            return None
        
        # Filter out files that are not log files (case-insensitive)
        log_files = [f for f in log_files if f.lower().endswith('.log')]

        if not log_files:
            print("No .log files found in the log directory.")
            return None
        
        # Get the full path of the most recent file
        latest_log = max([os.path.join(log_dir, f) for f in log_files], key=os.path.getmtime)
        return latest_log
    except Exception as e:
        print(f"Error reading log directory: {e}")
        return None

def get_active_network_interfaces():
    """Returns a list of active network interfaces."""
    active_interfaces = []
    try:
        # Iterate over network interfaces and check for active IPv4 addresses
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                # If the address family is IPv4 (AF_INET)
                if addr.family == psutil.AF_LINK:  # Check for any active link address
                    active_interfaces.append(interface)
    except AttributeError:
        print("Error: 'psutil' version may not support AF_INET.")
    return active_interfaces

def disconnect_internet():
    """Disconnects the internet by disabling active network interfaces."""
    print("Disconnecting the internet...")
    active_interfaces = get_active_network_interfaces()
    
    if not active_interfaces:
        print("No active network interfaces found.")
        return []
    
    disabled_interfaces = []
    for interface in active_interfaces:
        print(f"Disabling interface: {interface}")
        subprocess.run(["netsh", "interface", "set", "interface", interface, "disable"])
        disabled_interfaces.append(interface)
    
    return disabled_interfaces

def reconnect_internet(disabled_interfaces):
    """Reconnects the internet by enabling previously disabled interfaces."""
    print("Reconnecting the internet...")
    
    if not disabled_interfaces:
        print("No interfaces to reconnect.")
        return
    
    for interface in disabled_interfaces:
        print(f"Enabling interface: {interface}")
        subprocess.run(["netsh", "interface", "set", "interface", interface, "enable"])

def reconnect_wifi():
    """Uses PowerShell to enable all network adapters."""
    print("Reconnecting Wi-Fi using PowerShell...")
    subprocess.run(["PowerShell", "-Command", "Start-Process powershell -Verb runAs -ArgumentList 'Enable-NetAdapter -Name *'"])

def get_user_from_file():
    """Reads the user from the user.txt file."""
    try:
        user_file_path = "user.txt"
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as file:
                user = file.read().strip()
                return user
        else:
            print(f"{user_file_path} not found. Using default user 'notfl'.")
            return "notfl"
    except Exception as e:
        print(f"Error reading user.txt: {e}")
        return "notfl"

def monitor_lunar():
    user = get_user_from_file()  # Get the user dynamically from user.txt
    log_dir = fr"C:\Users\{user}\.lunarclient\logs\game"  # Dynamic path based on the user
    script_start_time = time.time()  # Record the time when the script starts
    print(f"Script started at {script_start_time}")

    disconnected = False
    reconnected = False
    disabled_interfaces = []

    while True:
        log_file = get_latest_log_file(log_dir)
        
        if log_file is None:
            print("No log file found. Retrying in 5 seconds...")
            time.sleep(5)
            continue

        # Check the modification time of the log file
        log_file_mod_time = os.path.getmtime(log_file)

        # Only process logs that were created after the script started
        if log_file_mod_time < script_start_time:
            print(f"Log file {log_file} is older than script start time, skipping.")
            time.sleep(5)
            continue
        
        # Open the latest log and check for the start signal
        with open(log_file, 'r', encoding='utf-8') as file:
            logs = file.readlines()

        for line in logs:
            if "Found external file: Forge_v1_8.jar" in line and not disconnected:  # Trigger for JVM start
                print("JVM started, disconnecting the internet...")
                disabled_interfaces = disconnect_internet()
                disconnected = True  # Mark that the internet has been disconnected

            if "[LC] LUNARCLIENT_STATUS_STARTED" in line and disconnected and not reconnected:  # Game fully loaded
                print("Lunar Client fully loaded, reconnecting the internet...")
                reconnect_internet(disabled_interfaces)
                reconnect_wifi()  # Reconnect Wi-Fi if it's being used
                reconnected = True  # Mark that the internet has been reconnected

        # Wait for the next check
        time.sleep(5)

if __name__ == "__main__":
    monitor_lunar()
