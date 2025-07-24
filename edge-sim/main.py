import os, json, random, time, paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

BROKER = os.getenv("BROKER", "mosquitto")
TOPIC  = os.getenv("TOPIC",  "lab")

client = mqtt.Client(
    client_id="",
    protocol=mqtt.MQTTv311,
    callback_api_version=CallbackAPIVersion.VERSION2
)
client.connect(BROKER, 1883, 60)

while True:
    payload = {
        "sensor_id": "demo",
        "metric": "temp",
        "value": round(random.uniform(20, 25), 1)
    }
    client.publish(TOPIC, json.dumps(payload))
    time.sleep(1)
