#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2020 Ondrej Kyjanek <ondrej.kyjanek@gmail.com>
#
# Contributors:
#    Ondrej Kyjanek - initial implementation

# This shows a simple example of a chat application with mqtt.

import paho.mqtt.client as mqttc
import paho.mqtt.properties as properties
import logging

logging.basicConfig(level=logging.INFO)

HOST = "broker.hivemq.com"
PORT = 1883
BASE_TOPIC = "ITECH_COM_WS"
PUB_TOPIC = "{}/chatroom/pub".format(BASE_TOPIC)
SUB_TOPIC = "{}/chatroom/pub".format(BASE_TOPIC)
STATUS_TOPIC = "{}/chatroom/status".format(BASE_TOPIC)
USERNAME = "OKY"

def on_message(client, userdata, msg):
    #payload is utf-8 encoded string so we need to decode it first
    try:
        if hasattr(msg.properties, "UserProperty"):
            print("{0[0][1]}: {1}".format(
                msg.properties.UserProperty,
                msg.payload.decode('utf-8'))
                )
        else:
            print("UnknownUser: {0}".format(
                msg.payload.decode('utf-8'))
                )
    except Exception as e:
        logging.error(e)

def on_user_status(client, userdata, msg):
    print("STATUS: {}".format(msg.payload.decode("utf-8")))

def on_subscribe(client, userdata, mid, granted_qos, properties):
    logging.info("Subscribed")

def on_disconnect(client, userdata, rc, properties):
    logging.info("Disconnected {}".format(rc))

def on_connect(client:mqttc.Client, userdata, flags, rc, properties):
    client.publish(
        STATUS_TOPIC, 
        payload="{} connected".format(USERNAME)
    )
    logging.info("Connected {}".format(rc))

def main():
    client = mqttc.Client(protocol=mqttc.MQTTv5)
    client.enable_logger(logging.getLogger())

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    props = properties.Properties(properties.PacketTypes.PUBLISH)
    props.UserProperty = ("name",USERNAME)

    client.message_callback_add(STATUS_TOPIC,on_user_status)
    client.message_callback_add(PUB_TOPIC,on_message)
    
    client.will_set(STATUS_TOPIC, payload="{} disconnected".format(USERNAME),properties=props)

    client.connect(HOST,PORT)
    client.loop_start()
    logging.info("Loop started")
    client.subscribe([
        (SUB_TOPIC,1),
        (STATUS_TOPIC,2)
    ])

    while True:
        message = input()
        client.publish(
            PUB_TOPIC,
            payload=message,
            qos=2,
            retain=False,
            properties=props)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Closing")
