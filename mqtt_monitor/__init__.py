""" mqtt_monitor """

import asyncio.exceptions
import json
import sys
import time
from pathlib import Path

import click
import paho.mqtt.client as mqtt
from pydantic import BaseModel

class ConfigFile(BaseModel):
    """ mqtt-monitor configuration model """
    hostname: str
    port: int = 1883
    topic: str = "#"
    keepalives: int = 60



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, result_code): # pylint: disable=unused-argument
    """ on_connect  method """
    print(json.dumps({
        "action" : "connected",
        "message" : f"result code {result_code}",
    }), file=sys.stderr)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic=userdata["topic"])

# The callback for when a PUBLISH message is received from the server.
def on_message(client: mqtt.Client, userdata, msg): # pylint: disable=unused-argument
    """ message handler """
    try:
        message = json.loads(msg.payload)
    except json.JSONDecodeError:
        if isinstance(msg.payload, str):
            message = msg.payload.encode("utf-8")
        else:
            message = msg.payload.decode("utf-8")
    data = {
        "_time" : time.time(),
        "topic" : msg.topic,
        "msg" : message,
    }
    print(json.dumps(data, ensure_ascii=False), file=sys.stderr)

@click.command()
@click.option("--config-file", type=Path, default="~/.config/mqtt-monitor.json")
@click.option("--hostname")
@click.option(
    "--port", "-p",
    type=int,
    default=1883,
    help="Port to connect to.")
@click.option(
    "--topic", "-t",
    default='#',
    help="Default is '#' which shows everything but system messages",
    )
def cli(
    config_file=Path("~/.config/mqtt-monitor.json"),
    hostname: str=None,
    topic: str="#",
    port: int=1883,
    ):
    """ MQTT Monitor """

    config_filepath = Path(config_file).expanduser().resolve()

    if config_filepath.exists():
        config = ConfigFile.parse_file(config_filepath)
    elif Path("mqtt-monitor.json").exists():
        config = ConfigFile.parse_file("mqtt-monitor.json")
    else:
        config = ConfigFile(hostname=hostname, topic=topic, port=port)

    print(json.dumps({
        "action" : "startup",
        "hostname" : config.hostname,
        "port" : config.port,
        "topic" : config.topic,
    }), file=sys.stderr)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.user_data_set(config.dict())

    while True:
        try:
            client.connect(
                config.hostname,
                config.port,
                config.keepalives,
                )

            # Blocking call that processes network traffic, dispatches callbacks and
            # handles reconnecting.
            # Other loop*() functions are available that give a threaded interface and a
            # manual interface.
            client.loop_forever()
        except asyncio.exceptions.TimeoutError as error_message:
            print(json.dumps({
                "error" : "timeout",
                "message" : f"sleeping for 60 seconds: {error_message}",
            }), file=sys.stderr)
            time.sleep(60)
        except Exception as error: #pylint: disable=broad-except
            print(f"Error, sleeping for 5 seconds: {error}", file=sys.stderr)
            time.sleep(5)
