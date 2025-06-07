# voltronic-mqtt
This container allows you to connect your Voltronic inverter (or any other inverter that works with `PI30` protocol) to [MQTT](https://mqtt.org) (and, becase of MQTT, [Home Assistant](https://www.home-assistant.io) :)).

## Usage
1. Clone this repository: `git clone https://github.com/rrroyal/voltronic-mqtt.git`
2. Navigate to the cloned repository: `cd voltronic-mqtt`

### Docker
To use this container, you must have [Docker](https://docker.com) and, optionally, [docker-compose](https://docs.docker.com/compose/) installed on your system.
1. Edit the `docker-compose.yml` file to specify the correct device path, MQTT host, and MQTT password for your system.
2. Run `docker-compose up` to start the container.

**Alternatively**, use these commands (with parameters configured to your use case) to run the container without `docker-compose`:
```sh
# Build the image
docker build -t voltronic-mqtt .

# Run the container
docker run -it -d --name voltronic-mqtt \
  -e VERBOSE=2 \
  -e DEVICE_PATH="/dev/ttyUSB0" \
  -e POLLING_INTERVAL=60 \
  -e MQTT_HOST="127.0.0.1:1883" \
  -e MQTT_PASS="user:pass" \
  -e MQTT_CLIENT_ID="voltronic-mqtt" \
  -e MQTT_TOPIC="iot/voltronic" \
  -e MQTT_TOPIC_SUB="send_cmd" \
  --device "/dev/ttyUSB0:/dev/ttyUSB0" \
  --restart unless-stopped \
  --network host \
  --privileged \
  voltronic-mqtt
```

### Standalone
You can also run the app by itself:
1. Configure `.env.example` for your use case and save it as `.env`.
2. Initialize a new `venv` environment: `python3 -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the program: `./standalone.sh` (if you're having errors with connecting to serial device, execute this command as root).

## Configuration

### `docker-compose.yml / .env`
This file contains the following configuration options:
- #### `VERBOSE`
	Level of logging (never: `-2`, always: `-1`, silent: `0`, error: `1`, notice: `2`, info: `3`, debug: `4`).
- #### `DEVICE_PATH`
	The path to the device that the inverter is connected to. This is typically `/dev/ttyUSB0` on UNIX systems.
- #### `POLLING_INTERVAL`
	The interval (in seconds) at which to poll the inverter for data.
- #### `MQTT_HOST`
	The hostname and port of the MQTT broker. Format: `host:port` (i.e. `127.0.0.1:1883`).
- #### `MQTT_PASS`
	The username and password to use when connecting to the MQTT broker. Format: `user:pass` (i.e. `AzureDiamond:hunter2`).
- #### `MQTT_CLIENT_ID`
  The ID of the MQTT client (i.e. `voltronic-mqtt`).
- #### `MQTT_TOPIC`
  The topic of MQTT messages (i.e. `iot/voltronic`) **Note: lowercased command will be added as a suffix (i.e. `/qpigs`).**
- #### `MQTT_TOPIC_SUB`
  The MQTT topic suffix to subscribe to (i.e. `send_cmd`)

## Devices
The container uses the following device:
- #### `/dev/ttyUSB0:/dev/ttyUSB0`
	This is the device that the inverter is connected to. This must be specified in the `docker-compose.yml`/`.env` file.

## Home Assistant
To use this program with [Home Assistant](https://www.home-assistant.io) you will need to connect your Home Assistant instance to the same MQTT broker as this program - you can read more about it [here](https://www.home-assistant.io/integrations/mqtt/). You can also deploy your own broker - i.e. [eclipse-mosquitto](https://hub.docker.com/_/eclipse-mosquitto).  
#### Please don't connect your Home Assistant instance to public brokers!
After that, you will need to configure MQTT entities. Example config is located inside the `homeassistant-mqtt.yml` file.

## Credits
- [ned-kelly/docker-voltronic-homeassistant](https://github.com/ned-kelly/docker-voltronic-homeassistant)
- [manio/skymax-demo](https://github.com/manio/skymax-demo)
