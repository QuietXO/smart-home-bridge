# tests/test_end_to_end.py
import json, sqlite3, time, paho.mqtt.publish as pub

def test_edge_to_db():
    """Publish 10 messages → expect 10 new rows in SQLite."""
    # Current row count
    conn = sqlite3.connect("cloud-agg/iot.db")
    start_rows = conn.execute("SELECT COUNT(*) FROM iot_events").fetchone()[0]

    # Publish 10 messages to the broker
    for i in range(10):
        payload = json.dumps({"sensor_id": "test", "metric": "temp", "value": i})
        pub.single(topic="lab", payload=payload, hostname="localhost", port=1883)

    # Wait a moment
    time.sleep(2)

    # Verify row increase
    end_rows = conn.execute("SELECT COUNT(*) FROM iot_events").fetchone()[0]
    assert end_rows - start_rows == 10
