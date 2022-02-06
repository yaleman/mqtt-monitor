""" mqtt_monitor """

import asyncio.exceptions
import json
import sys
import time

import click
import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, result_code): # pylint: disable=unused-argument
    """ on_connect  method """
    print(f"Connected with result code {result_code}")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic=userdata["topic"])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg): # pylint: disable=unused-argument
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
    print(json.dumps(data))

@click.command()
@click.argument("hostname")
@click.option("--port", "-p", type=int, default=1883, help="Port to connect to.")
@click.option("-t", "--topic", default='#', help="Default is '#' which shows everything but system messages")
def cli(hostname: str=None, topic: str="#", port: int=1883):
    """ MQTT Monitor """
    if not hostname:
        sys.exit(1)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.user_data_set({
        "topic" : topic,
    })

    while True:

        try:

            client.connect(hostname, port, 60)

            # Blocking call that processes network traffic, dispatches callbacks and
            # handles reconnecting.
            # Other loop*() functions are available that give a threaded interface and a
            # manual interface.
            client.loop_forever()
        except asyncio.exceptions.TimeoutError as error_message:
            print(f"Timeout Error connecting, sleeping for 60 seconds: {error_message}", file=sys.stderr)
            time.sleep(60)
