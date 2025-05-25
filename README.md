# Smart energy monitor data logging
This script reads the data from a connected Origin Energy branded smart meter
monitor and publishes the data to [ThingsBoard](https://thingsboard.io/).

Written by Jotham Gates, May 2025.

## Notes on the energy monitor
The energy monitor's model name is "SM-EM-FMAG-P" and it connects to a smart
meter using Zigbee. These monitors were distributed as freebies in Victoria,
Australia many years ago. As fair as I know, these particular devices are no
longer produced or distributed.

When connected to a computer using USB (vendor id `2047`, product id `08a4`),
the monitor appears as two drives, each with one partition:
  - `Upgrade EM` is for use when updating the firmware.
  - `Origin EM` contains a HTML page showing data in half hour chunks. The
    data we are interested in is obtained from JavaScript files in this page.

Further information may be gained from these sources:
- [Whirlpool thread on the devices](https://forums.whirlpool.net.au/archive/2165708)
- [FCCID page showing photos and other documents for the device](https://fccid.io/2AALMPVU-G2NA)
    - At one point, the monitor's model was "PVU-G2NA PowerVu".
- [User manual](https://www.manualslib.com/manual/713959/Origin-Energy-Monitor.html)


## Installation and setup
1. Clone this repository to the computer that the monitor will be connected to.
2. Create a python virtual environment and activate it.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3. Install the required libraries
    ```bash
    pip3 install -r requirements.txt
    ```
4. Log into your ThingsBoard server and create a new device. Note down the MQTT
    access token for it.
5. Make a copy of [`settings.example.py`](./settings.example.py) and name it 
    `settings.py`. Fill in the required constants for file paths, UUIDs, address
    of your ThingsBoard server and access token.
6. Check that everything is working correctly by manually running
    [`read_data.py`](./read_data.py).
    ```bash
    ./read_data.py
    ```
7. Set up a cron job to regularly run the script to fetch new data from the
    energy monitor and publish it. This can be accomplished using `crontab -e`.  
    The following example acquires and uploaded fresh data at 3 minutes past the
    half hour to allow for some discrepancy between the energy monitor's clock
    and the computer's.
    ```cron
    3/30 * * * * cd <FOLDER_OF_THIS_SCRIPT> && ./.venv/bin/python3 read_data.py
    ```