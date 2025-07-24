import sqlite3, json, os, paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

BROKER = os.getenv("BROKER", "mosquitto")
TOPIC  = os.getenv("TOPIC",  "lab")

conn = sqlite3.connect("/app/iot.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS iot_events "
             "(ingest_ts TEXT,sensor_id TEXT,metric TEXT,value REAL)")

def on_msg(_, __, msg):
    j = json.loads(msg.payload)
    conn.execute("INSERT INTO iot_events VALUES (datetime('now'),?,?,?)",
                 (j["sensor_id"], j["metric"], j["value"]))
    conn.commit()

mqttc = mqtt.Client(
    client_id="",
    protocol=mqtt.MQTTv311,
    callback_api_version=CallbackAPIVersion.VERSION2
)
mqttc.on_message = on_msg
mqttc.connect(BROKER, 1883, 60)
mqttc.subscribe(TOPIC)
mqttc.loop_forever()
