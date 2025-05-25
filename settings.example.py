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
