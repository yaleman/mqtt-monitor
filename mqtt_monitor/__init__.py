""" mqtt_monitor """

import asyncio.exceptions
import json
from os import PathLike
from pathlib import Path
import sys
import time
from typing import Dict, List, Optional, TypedDict, Union

import click
import paho.mqtt.client as mqtt # type: ignore
from pydantic import BaseModel

class UserData(TypedDict):
    """ userdata typing """
    hostname: str
    port: str
    topics: List[str]
    keepalives: int


class ConfigFile(BaseModel):
    """ mqtt-monitor configuration model """
    hostname: str
    port: int = 1883
    topics: List[str] = []
    keepalives: int = 60

CONNECT_RC = {
    0: "Connection successful",
    1: "Connection refused - incorrect protocol version",
    2: "Connection refused - invalid client identifier",
    3: "Connection refused - server unavailable",
    4: "Connection refused - bad username or password",
    5: "Connection refused - not authorised",
    # 6-255: Currently unused.
}



# The callback for when the client receives a CONNACK response from the server.
def on_connect(
    client: mqtt.Client,
    userdata: UserData,
    _: Dict[str, Union[int, str]],
    result_code: int,
    ) -> None:
    """ on_connect  method """
    msg = json.dumps({
        "action" : "connected",
        "message" : CONNECT_RC.get(result_code,f"Unknown result code: {result_code}"),
    })
    print(msg, file=sys.stderr)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in userdata["topics"]:
        client.subscribe(topic=topic)

# The callback for when a PUBLISH message is received from the server.
# pylint: disable=unused-argument
def on_message(
    client: mqtt.Client,
    userdata: UserData,
    msg: mqtt.MQTTMessage,
    ) -> None: # pylint: disable=unused-argument
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
    print(json.dumps(data, default=str, ensure_ascii=False), file=sys.stderr)

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
    default=None,
    multiple=True,
    help="Default is '#' which shows everything but system messages, can specify multiple times.",
    )
def cli(
    config_file: Path=Path("~/.config/mqtt-monitor.json"),
    hostname: Optional[str]=None,
    topic: Optional[List[str]]=None,
    port: int=1883,
    ) -> None:
    """ MQTT Monitor """

    config_filepath = Path(config_file).expanduser().resolve()

    if config_filepath.exists():
        config = ConfigFile.parse_file(config_filepath)
    elif Path("mqtt-monitor.json").exists():
        config = ConfigFile.parse_file("mqtt-monitor.json")
    else:
        config = ConfigFile(hostname=hostname, topics=topic, port=port)

    print(json.dumps({
        "action" : "startup",
        "hostname" : config.hostname,
        "port" : config.port,
        "topics" : config.topics,
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
