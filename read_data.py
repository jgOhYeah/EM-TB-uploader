#!/usr/bin/env python3
"""read_data.py
A simple script to obtain data from an Origin Energy branded SM-EM-FMAG-P smart
meter monitor and upload it to ThingsBoard over MQTT.

Written by Jotham Gates, May 2025.
"""
import re
import os
import json
import threading
from typing import Dict, List, Tuple
import subprocess
import paho.mqtt.client as mqtt

try:
    import settings
except ModuleNotFoundError:
    print(
        "Please make a copy of 'settings.example.py' named 'settings.py' and edit it to match your installation."
    )
    exit(1)


class Data:
    def __init__(self, filename: str, needs_quotes: bool = False) -> None:
        """Loads a JSON object from a js file.

        This uses regular expressions - specific to the energy monitor's files.

        Args:
            filename (str): Filename to load in FOLDER.

        Returns:
            dict: Data from the file.
        """
        with open(os.path.join(settings.FOLDER, filename)) as file:
            text = file.read()

        search = re.search("\\{.*\\}", text, re.DOTALL)
        if search is not None:
            json_str = search.group()
        else:
            raise ValueError(f"Could not find the data in '{filename}'.")

        if needs_quotes:
            # Add quotes to the keys if needed.
            json_str = re.sub("(\\w+):", '"\\1":', json_str)
        self.data = json.loads(json_str)

    def _day_timestamps(self, timestamp: str) -> Tuple[List[int], List[float]]:
        """Obtains a list of timestamps and data values for a given timestamp at the start of the day.

        Args:
            timestamp (str): Timestamp string they day is stored under.

        Returns:
            Tuple[List[int], List[float]]: List of timestamps and values.
        """
        values: List[float | None] = self.data["data"][timestamp]
        start_time = int(timestamp)
        INCREMENT = 1800000  # ms per half hour.
        assert len(values) == 48, "Expecting each value list to have 48 elements."
        time_range = range(start_time, start_time + len(values) * INCREMENT, INCREMENT)
        filtered_times = []
        filtered_values = []
        for i in range(len(values)):
            if values[i] is not None:
                filtered_times.append(time_range[i])
                filtered_values.append(values[i])

        return filtered_times, filtered_values

    def all_timestamps(self) -> Tuple[List[int], List[float]]:
        """Converts the data into a tuple containing a list of timestamps and a list of values."""
        times: List[int] = []
        values: List[float] = []
        for day_ts in self.data["data"].keys():
            filtered_times, filtered_values = self._day_timestamps(day_ts)
            times.extend(filtered_times)
            values.extend(filtered_values)

        return times, values


class NotConnectedException(Exception):
    """Exception for if the monitor is not mounted correctly."""

    pass


def remount(unmount:bool) -> None:
    """Remounts the energy monitor's filesystem to get the latest data."""
    if unmount:
        subprocess.run(("udisksctl", "unmount", "-b", settings.DISK_PATH))
    try:
        subprocess.run(("udisksctl", "mount", "-b", settings.DISK_PATH), check=True)
    except subprocess.CalledProcessError as e:
        raise NotConnectedException(e)

def set_usb_power(state:bool) -> None:
    """Turns on or off power for the USB port."""
    subprocess.run(("uhubctl", "-l", settings.USB_HUB_LOCATION, "-p", settings.USB_HUB_PORT, "-a", "1" if state else "0"))

Telemetry = List[Dict[str, int | Dict[str, float]]]


def as_telemetry(sources: Dict[str, Data]) -> Telemetry:
    """Generates thingsboard telemetry.

    Args:
        sources (Dict[str, Data]): The Data objects with the key to use in the output.

    Returns:
        Telemetry: Thingsboard timeseries list of times and values.
    """
    # Merge everything into a single disctionary.
    merged: Dict[int, Dict[str, float]] = {}
    for key, source in sources.items():
        # Load all timestamps from the js file.
        times, values = source.all_timestamps()

        # Limit the number of items to upload if requested.
        if settings.LIMIT_RECORDS:
            times = times[-settings.LIMIT_RECORDS :]
            values = values[-settings.LIMIT_RECORDS :]

        # Add to the merged dictionary.
        for i in range(len(times)):
            if times[i] not in merged:
                # This time is not in the results dictionary yet. Add it.
                merged[times[i]] = {}

            # Add the value to the dictionary.
            merged[times[i]][key] = values[i]

    # Convert the dictionary into a list of dictionaries.
    result: List[Dict[str, int | Dict[str, float]]] = []
    for time, values in merged.items():
        result.append({"ts": time, "values": values})
    return result


def send_telemetry(telemetry: Telemetry) -> None:
    """Sends the telemetry using MQTT."""
    # Connect
    print("Connecting to MQTT")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore
    client.username_pw_set(settings.MQTT_USERNAME)

    done_event = threading.Event() # Allows processing to proceed once published.

    def on_publish(client, userdata, mid, reason_code, properties):
        """Sets the done event flag so that the connection can be shut (single shot script)."""
        done_event.set()

    client.on_publish = on_publish
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
    client.loop_start()

    # Send the telemetry
    print("Publishing")
    TOPIC = "v1/devices/me/telemetry"
    msg_info = client.publish(
        TOPIC, json.dumps(telemetry), qos=1
    )  # Set qos=1 so we know when the message was sent.
    msg_info.wait_for_publish()

    # Disconnect.
    done_event.wait()
    print("Disconnecting")
    client.disconnect()
    client.loop_stop()


if __name__ == "__main__":
    # Apply power and mount the partition or remount.
    if settings.REMOVE_POWER_BETWEEN_RUNS:
        set_usb_power(True)
        remount(False)
    else:
        remount(True)
    
    # Aquire and process the data.
    telemetry = as_telemetry(
        {
            "gen": Data("gen.js"),
            "gen_cred": Data("gen_cred.js"),
            "con_cost": Data("con_cost.js"),
            "cons": Data("cons.js"),
        }
    )
    print(json.dumps(telemetry))
    send_telemetry(telemetry)

    # Turn off power if needed.
    if settings.REMOVE_POWER_BETWEEN_RUNS:
        set_usb_power(False)
        
    print("Finished")