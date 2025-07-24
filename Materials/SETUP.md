### Phase 2
```
gcloud config set project  iot-bridge-lab-466916
gcloud config set run/region europe-west3
gcloud services enable compute.googleapis.com storage.googleapis.com
```
```
# edge-init.sh
set -e
apt-get update -qq
apt-get install -y docker.io docker-compose git
git clone https://github.com/QuietXO/smart-home-bridge.git /opt/bridge
cd /opt/bridge
/usr/bin/docker compose up -d mosquitto edge-sim


chmod +x edge-init.sh
gsutil cat gs://iot-edge-scripts-quietxo/edge-init.sh
```
```
gsutil mb -p $(gcloud config get-value project) \
          -l europe-west3 gs://iot-edge-scripts-$USER
gsutil cp edge-init.sh gs://iot-edge-scripts-$USER/

gcloud compute instances create edge-vm \
  --zone=europe-west3-b \
  --machine-type=e2-small \
  --metadata startup-script-url=gs://iot-edge-scripts-$USER/edge-init.sh \
  --tags=mqtt-broker
```
```
gcloud compute firewall-rules create mqtt-broker-1883 \
  --allow=tcp:1883 \
  --direction=INGRESS \
  --target-tags=mqtt-broker \
  --description="Allow MQTT plain-text"

gcloud compute instances describe edge-vm \
  --zone=europe-west3-b \
  --format='value(tags.items[])'

mosquitto_sub -h 35.234.76.35 -p 1883 -t lab -C 1 -v
nc -zv 35.234.76.35 1883
```
---

### 1. Set the project & default region
```
gcloud config set project iot-bridge-project
gcloud config set run/region europe-west4       # europe-west3 is the closest to Austria
```
---

### 2. Acknowledge the service’s pricing terms
```
gcloud services enable dataflow.googleapis.com      # Dataflow jobs \
gcloud services enable pubsub.googleapis.com        # code publish/subscribe \
gcloud services enable bigquery.googleapis.com      # project access to BigQuery datasets
```
---

### 3. Create could resources
```
gcloud pubsub topics create iot-ingest					# sensors send messages here
gcloud pubsub subscriptions create iot-bq-sub --topic iot-ingest	# attach sub to the topic and saves the messages (creates a temp buffer)
```
 			     publish()					pull(), ack()
 MQTT→Pub/Sub  ───────────►  (topic) iot-ingest  ─────────────►  Pub/Sub ───► BigQuery
	job								backlog

1st arrow: all sensor JSONs land in the topic
2nd arrow: the topic fan-outs each message into any attached subscription backlog(s)
3rd arrow: the consumer job drains iot-bq-sub, writes to BigQuery, then acknowledges
```
PROJECT_ID=$(gcloud config get-value project)
bq mk --dataset --location=EU $PROJECT_ID:iot_raw				# every sensor JSON will land in this dataset located in EU datacenter
bq mk --location=EU --table \
      --time_partitioning_type=DAY \
      --clustering_fields=sensor_id \
      --schema=ingest_ts:TIMESTAMP,sensor_id:STRING,metric:STRING,value:FLOAT64 \
      $PROJECT_ID:iot_raw.iot_events
```
MQTT broker
	│
	▼
Pub/Sub topic  ─────────────────────►  Pub/Sub subscription
									│
									▼
                                    					BigQuery table  iot_raw.iot_events

---

### 4. Dataflow service account
```
gcloud iam service-accounts create dataflow-mqtt \
      --display-name "Dataflow MQTT bridge"
```
^^^ VM worker account ^^^
```
gcloud projects add-iam-policy-binding $DEVSHELL_PROJECT_ID \
      --member "serviceAccount:dataflow-mqtt@$DEVSHELL_PROJECT_ID.iam.gserviceaccount.com" \
      --role roles/pubsub.publisher
```
^^^ grant the publisher role (IAM Policy) ^^^
```
gcloud projects add-iam-policy-binding $DEVSHELL_PROJECT_ID \
      --member "serviceAccount:dataflow-mqtt@$DEVSHELL_PROJECT_ID.iam.gserviceaccount.com" \
      --role roles/bigquery.dataEditor
```
^^^ grant editor role in BigQuery (IAM Policy) ^^^
```
SA="serviceAccount:dataflow-mqtt@$PROJECT_ID.iam.gserviceaccount.com"
```
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="$SA" --role=roles/dataflow.worker
```
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="$SA" --role=roles/storage.objectAdmin
```

---

### 5.
```
REGION=europe-west4
TEMPLATE=gs://dataflow-templates-$REGION/latest/flex/PubSub_to_BigQuery
```
```
gcloud dataflow flex-template run mqtt-pubsub-bridge \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --template-file-gcs-location="$TEMPLATE" \
  --service-account-email="dataflow-mqtt@$PROJECT_ID.iam.gserviceaccount.com" \
  --parameters="brokerServer=tcp://broker.emqx.io:1883,\
inputTopic=lab,\
outputTopic=projects/$PROJECT_ID/topics/iot-ingest,\
username=anon,\
password=anon"
```
```
gcloud dataflow flex-template run pubsub-bq-loader \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --template-file-gcs-location="$TEMPLATE" \
  --service-account-email="dataflow-mqtt@$PROJECT_ID.iam.gserviceaccount.com" \
  --parameters="inputSubscription=projects/$PROJECT_ID/subscriptions/iot-bq-sub,\
                outputTableSpec=$PROJECT_ID:iot_raw.iot_events,\
                writeDisposition=WRITE_APPEND,\
                ignoreUnknown=true"
```

---
### Local Debug Notes
```
docker compose up --build -d
docker compose down

docker run --rm --network smart-home-bridge_default \
  eclipse-mosquitto:2 \
  mosquitto_sub -h mosquitto -p 1883 -t lab -C 3

sqlite3 cloud-agg/iot.db 'SELECT COUNT(*) FROM iot_events;'

docker compose exec grafana sh -c 'ls -R /etc/grafana/provisioning'

make test
```