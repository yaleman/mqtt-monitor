# mqtt-monitor

MQTT Monitoring thing

# Configuration 

The following things are configurable, either with a local `mqtt-monitor.json` or `~/.config/mqtt-monitor.json`

```json
hostname: str
port: int = 1883
topic: str = "#"
keepalives: int = 60
```

## Usage

```
python -m pip install git+https://github.com/yaleman/mqtt-monitor
mqtt-monitor <hostname>
```

Or use docker one-off:

```
docker run --rm --name mqtt_monitor \
    -v "$(pwd)/mqtt-monitor.json:/app/mqtt-monitor.json" \
    ghcr.io/yaleman/mqtt_monitor:latest
```

Keep it running in the background:

```
docker run -d --name mqtt_monitor \
    -v "$(pwd)/mqtt-monitor.json:/app/mqtt-monitor.json" \
    ghcr.io/yaleman/mqtt_monitor:latest
```

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd mqtt-monitor
    poetry install
    poetry run python -m mqtt_monitor <hostname>

