import paho.mqtt.client as mqtt  # pip install paho-mqtt
import time
import json
import os
import argparse

# MQTT_SERVER_IP = "util"
# # SPACEAPI_TEMPLATE = r"C:\Code\python\artifactory_spaces_api_interface\spaceapi.template.json"
# # SPACEAPI_TEMP = r"C:\Code\python\artifactory_spaces_api_interface\spaceapi.json.tmp"
# # SPACEAPI_OUT = r"C:\Code\python\artifactory_spaces_api_interface\spaceapi.json"
#
# SPACEAPI_TEMPLATE = r"/home/spaceapi/spaceapi.template.json"
# SPACEAPI_TEMP = r"/home/spaceapi/spaceapi.json.tmp"
# SPACEAPI_OUT = r"/var/www/space/spaceapi.json"

ENCODING = "utf-8"

MQTT_TOPIC_STATUS = "status/arduino_artimer"
MQTT_TOPIC_TIME_REMAIN = "sensors/arduino_artimer/time_remaining"

config = {}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe(MQTT_TOPIC_STATUS)
    client.subscribe(MQTT_TOPIC_TIME_REMAIN)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode(ENCODING)
        topic = msg.topic
        print("Received '{}' '{}'".format(topic, payload))
        if topic == MQTT_TOPIC_TIME_REMAIN:
            time_remaining = float(payload)
            update_spaceapi(time_remaining=time_remaining)
    except Exception as e:
        print("Exception: {}".format(e))


def update_spaceapi(time_remaining):
    global config

    open_state = (time_remaining > 0)
    if open_state:
        message = "Open for {} hours (by Door Timer)".format(time_remaining)
    else:
        message = 'Closed (by Door Timer)'

    with open(config['spaceapi_template']) as f:
        j = json.load(f)

    # Update the json contents
    state = j['state']
    state['open'] = open_state
    state['time_remaining'] = time_remaining
    state['lastchange'] = time.time()
    state['message'] = message

    with open(config['spaceapi_temp'], 'w') as f:
        json.dump(j, f, sort_keys=True, indent=4, separators=(',', ': '))

    os.replace(config['spaceapi_temp'], config['spaceapi_out'])

    print("Updated: {}".format(config['spaceapi_out']))


def read_config(path):
    with open(path) as f:
        j = json.load(f)
    return j


def main():
    arg_parser = argparse.ArgumentParser(description="SpacesAPI interface")
    arg_parser.add_argument('config', help='path to config json file')
    args = arg_parser.parse_args()

    global config
    config = read_config(args.config)
    print("Config: {}".format(config))

    client = mqtt.Client("spaceapi_interface")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config["mqtt_server"], 1883, 60)

    client.loop_start()

    while True:
        pass


if __name__ == "__main__":
    main()
