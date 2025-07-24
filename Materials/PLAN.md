# MQTT-to-BigQuery Bridge
### for smart-home sensors

> **Scope freeze (v1.0):** *Build, measure & demo a serverless pipeline that moves smart‑home sensor readings from an MQTT broker into a time‑partitioned BigQuery table, with an (optional) Grafana dashboard.*

---
## 0‑to‑100 Timeline
| Phase                     | Purpose                             | Status |
|---------------------------|-------------------------------------|:------:|
| 0 Kick‑off                | Git, Documents, DAG                 |   ✅    |
| 1 Local containers        | Sim & broker in Docker              |   ✅    |
| 2 Edge VM + broker        | Raspberry‑Pi‑like VM                |   ✅    |
| 3 Storage node            | Pub/Sub + BQ dataset                |   🟡    |
| 4 Cloud VM & UI           | Aggregator, web, Grafana            |   ⬜    |
| 5 IaC scripts             | deploy.sh / Terraform               |   ⬜    |
| 6 Load tests              | Locust, Monitoring                  |   ⬜    |
| 7 Evaluation              | Graphs of Performance               |   ⬜    |
| 7.1 Data ingest           | Pull CSV + Monitoring metrics       |   ⬜    |
| 7.2 Plots & Tables        | Latency / Throughput / Autoscaling  |   ⬜    |
| 7.3 Discussion write-up   | Bottlenecks, Scaling, Cost analysis |   ⬜    |
| 7.4 Export & Integration  | Embed figures in report & slides    |   ⬜    |
| 7.5 Reproducibility check | Notebook rerun on clean repo        |   ⬜    |
| 8 (Opt) GKE               | Autopilot manifests                 |   ⬜    |
| 9 Packaging               | ZIP, Presentation, Report           |   ⬜    |

> **Legend:** done: ✅ **||** in‑progress: 🟡 **||** not started: ⬜

---
## Phase‑by‑Phase Checklist

### Phase 0 — Kick‑off (✅)
- [x] Create **private repo** `smart-home-bridge` on GitHub.
- [x] Add collaborators.
- [x] Add **README.md**, **diagrams/architecture.png**, this **PLAN.md**.
- [x] Add high‑level cards (Phase 1 … Phase 9).

### Phase 1 — Local dev & containers (✅)
- [x] `edge-sim/` Python publisher → Dockerfile.
- [x] Mosquitto broker container in `docker-compose.yml`.
- [x] SQLite placeholder store.
- [x] Grafana+BigQuery plugin via Docker.
- [x] Unit tests + `make test`.

### Phase 2 — Edge VM (✅)
- [x] Startup script `edge-init.sh` (installs Docker, pulls images, opens ports 1883/8883).
- [x] Firewall rule tag `mqtt-broker-1883` tag `mqtt-broker`.
- [x] Systemd health‑check (restarts Mosquitto).

### Phase 3 — Storage node (GCP)
- [ ] Pub/Sub topic `iot-ingest` + subscription `iot-bq-sub`.
- [ ] BigQuery dataset `iot_raw` & table `iot_events` (DAY partition, cluster `sensor_id`).
- [ ] Secrets in Secret Manager.
- [ ] **Create bucket** `iot-raw-events-$PROJECT_ID` (regional, Standard)
- [ ] Add lifecycle delete > 90 days; uniform ACLs
- [ ] Edge cron: gzip daily JSONL → `gsutil cp raw/YYYY-MM-DD.jsonl.gz`
- [ ] Cloud Function (or cloud-agg) triggers on `finalize` → bq load

### Phase 4 — Cloud VM & UI
- [ ] `cloud-agg` container subscribes & writes via `google-cloud-bigquery`.
- [ ] `web-ui` (Flask + DataTables) container.
- [ ] Grafana container, BigQuery data‑source JSON provisioned.
- [ ] Cloud‑init script `cloud-init.sh`.

### Phase 5 — IaC & Automation
- [ ] `deploy.sh` bash script (or Terraform) provisioning all resources end‑to‑end.
- [ ] `destroy.sh` cleanup script.
- [ ] GitHub Action to lint Terraform / shell.

### Phase 6 — Load & Scale Testing
- [ ] **locust/** directory with `locustfile.py` that spawns virtual “sensors”
- [ ] **locust-runner.sh** script (runs Locust locally *or* in Cloud Run)
- [ ] Save CSV logs to **results/** for plotting
- [ ] Locust scenarios: 100, 500, 2 000 vUsers
- [ ] Monitoring dashboard JSON export
- [ ] Autoscaling demo: Cloud Run revision with aggregator

### Phase 7 — Evaluation & Report
#### 7.1 Data ingest
- [ ] Pull **Locust CSV logs** (`results/*.csv`) into a Jupyter notebook.
- [ ] Query **Cloud Monitoring API** for:
  - Pub/Sub backlog age & message count
  - Dataflow worker-count (autoscaling events)
  - VM / Cloud-Run CPU % & memory MB
  - Edge-to-cloud **network latency** (ping RTT *or* Pub/Sub publish-age)
  - BigQuery streaming-insert latencies
- [ ] Merge Locust and Monitoring dataframes on timestamp.

#### 7.2 Plots & Tables
- [ ] **Latency CDF / histogram** per test scenario.
- [ ] **Throughput vs virtual-users** line chart.
- [ ] **Autoscaling timeline** → number of workers / VM instances over time.
- [ ] **Resource-utilisation heat-map** (CPU, memory per component).
- [ ] **Edge-to-cloud latency plot** (RTT or publish-age vs time).
- [ ] **Cost table** — BQ, Pub/Sub, Dataflow, VMs, Cloud Run; €/1 000 msgs.

#### 7.3 Discussion write-up
- [ ] Identify primary bottlenecks (CPU, backlog, network).
- [ ] Analyse autoscaling behaviour (scale-out trigger, cool-down).
- [ ] Compare cost vs load; €/1 000 msgs at 100, 500, 2 000 vUsers.
- [ ] Suggest future optimisations (e.g., Storage Write API, HPA tuning).

#### 7.4 Export & Integration
- [ ] Save all plots to `report/assets/`.
- [ ] Embed figures with captions in `report.md` / LaTeX.
- [ ] Add **3 evaluation slides** (results, cost, take-aways) to `slides.pptx`.

#### 7.5 Reproducibility check
- [ ] Re-run notebook on a **fresh clone**; verify plots identical.
- [ ] Commit notebook as `notebooks/evaluation.ipynb` and lock package versions.

### Phase 8 — Optional GKE Autopilot
- [ ] Convert Compose to Kubernetes manifests (Deployment, HPA, Service).
- [ ] Deploy to Autopilot; capture screenshot for bonus credit.

### Phase 9 — Packaging & Submission
- [ ] Generate `report.pdf` (≤ 15 pages) from markdown → LaTeX.
- [ ] 10‑slide presentation deck.
- [ ] `zip.sh` script packs: `/src`, `/docker`, `/infra`, README, report, slides.
- [ ] Smoke‑test zip on fresh GCP project.

---

*"Plan is nothing; planning is everything." — Dwight D. Eisenhower*

