# mqtt-monitor

MQTT Monitoring thing

# Configuration 

The following things are configurable, either with a local `mqtt-monitor.json` or `~/.config/mqtt-monitor.json`

```json
hostname: str
port: int = 1883
topics: List[str] = ["#"]
keepalives: int = 60
```

## Usage

```shell
python -m pip install git+https://github.com/yaleman/mqtt-monitor
mqtt-monitor <hostname>
```

Or use docker one-off:

```shell
docker run --rm --name mqtt_monitor \
    -v "$(pwd)/mqtt-monitor.json:/app/mqtt-monitor.json" \
    ghcr.io/yaleman/mqtt-monitor:latest
```

Keep it running in the background:

```shell
docker run -d \
    --name mqtt_monitor \
    --restart always \
    -v "$(pwd)/mqtt-monitor.json:/app/mqtt-monitor.json" \
    ghcr.io/yaleman/mqtt-monitor:latest
```

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd mqtt-monitor
    poetry install
    poetry run python -m mqtt_monitor <hostname>

Building the docker container:

```shell
docker build -t ghcr.io/yaleman/mqtt-monitor
```