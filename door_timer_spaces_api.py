import paho.mqtt.client as mqtt  # pip install paho-mqtt
import time
import json
import os

MQTT_SERVER_IP = "util"
# SPACEAPI_TEMPLATE = r"C:\Code\python\artifactory_spaces_api_interface\spaceapi.template.json"
# SPACEAPI_TEMP = r"C:\Code\python\artifactory_spaces_api_interface\spaceapi.json.tmp"
# SPACEAPI_OUT = r"C:\Code\python\artifactory_spaces_api_interface\spaceapi.json"

SPACEAPI_TEMPLATE = r"/home/spaceapi/spaceapi.template.json"
SPACEAPI_TEMP = r"/home/spaceapi/spaceapi.json.tmp"
SPACEAPI_OUT = r"/var/www/space/spaceapi.json"

ENCODING = "utf-8"

MQTT_TOPIC_STATUS = "status/arduino_artimer"
MQTT_TOPIC_TIME_REMAIN = "sensors/arduino_artimer/time_remaining"

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
        print("{} {}".format(topic, payload))
        if topic == MQTT_TOPIC_TIME_REMAIN:
            time_remaining = float(payload)
            update_spaceapi(time_remaining=time_remaining)
    except Exception as e:
        print("Exception: {}".format(e))


def update_spaceapi(time_remaining):
    open_state = (time_remaining > 0)
    if open_state:
        message = "Open for {} hours (by Door Timer)".format(time_remaining)
    else:
        message = 'Closed (by Door Timer)'

    with open(SPACEAPI_TEMPLATE) as f:
        j = json.load(f)

    # Update the json contents
    state = j['state']
    state['open'] = open_state
    state['time_remaining'] = time_remaining
    state['lastchange'] = time.time()
    state['message'] = message

    with open(SPACEAPI_TEMP, 'w') as f:
        json.dump(j, f, sort_keys=True, indent=4, separators=(',', ': '))

    os.replace(SPACEAPI_TEMP, SPACEAPI_OUT)

    print("Updated: {}".format(SPACEAPI_OUT))


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_SERVER_IP, 1883, 60)

    client.loop_start()

    while True:
        # temperature = sensor.blocking_read()
        # client.publish("paho/temperature", temperature)
        pass


if __name__ == "__main__":
    main()
