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
