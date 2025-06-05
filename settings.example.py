"""settings.example.py
Settings and constants for use with the energy monitor and ThingsBoard.

Make a copy of this file and name it "settings.py". Make your edits to this
new file to avoid committing sensitive information to the git history.

Written by Jotham Gates, May 2025.
"""

DISK_PATH = "/dev/disk/by-partuuid/<YOUR_UUID>"  # UUID of the "Origin EM" partition.
FOLDER = "/media/<USERNAME>/Origin EM/data/"  # Directory that the useful JavaScript files are located in once the partition is mounted.
MQTT_BROKER = "localhost"  # Address of the MQTT broker for the ThingsBoard server.
MQTT_PORT = 1883  # MQTT port (likely 1883 by default).
MQTT_USERNAME = "<ACCESS_TOKEN>"  # Access token for the device.
LIMIT_RECORDS = 5  # How many records to send at once. Set to 0 or None to disable limiting. Large messages with several hundred records may fail to send.

# Removing power from the USB ports when this script is not running.
# This is intended to stop the battery in the energy monitor being overcharged
# and puffing up. If REMOVE_POWER_BETWEEN_RUNS is True, this is enabled. If False,
# The "Origin EM" partition is remounted to refresh the data instead.
REMOVE_POWER_BETWEEN_RUNS = False
# Settings used by uhubctl.
# E.g. `uhubctl -l <USB_HUB_LOCATION> -p <USB_HUB_PORT> -a <0|1>`
USB_HUB_LOCATION = "1-1" # Default for a raspberry pi 3b
USB_HUB_PORT = "2" # Default for a raspberry pi 3b