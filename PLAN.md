# MQTT-to-BigQuery Bridge
### for smart-home sensors

> **Scope freeze (v1.0):** *Build, measure & demo a serverless pipeline that moves smart‑home sensor readings from an MQTT broker into a time‑partitioned BigQuery table, with an (optional) Grafana dashboard.*

---
## 0‑to‑100 Timeline
| Phase              | Purpose                  | Status |
|--------------------|--------------------------|--------|
| 0 Kick‑off         | Repo, board, docs        | ✅ |
| 1 Local containers | Sim & broker in Docker   | ⬜ |
| 2 Edge VM + broker | Raspberry‑Pi‑like VM     | ⬜ |
| 3 Storage node     | Pub/Sub + BQ dataset     | ⬜ |
| 4 Cloud VM & UI    | Aggregator, web, Grafana | ⬜ |
| 5 IaC scripts      | deploy.sh / Terraform    | ⬜ |
| 6 Load tests       | Locust, Monitoring       | ⬜ |
| 7 Evaluation       | Graphs, cost calc        | ⬜ |
| 8 (Opt) GKE        | Autopilot manifests      | ⬜ |
| 9 Packaging        | Zip, slides, report      | ⬜ |

> **Legend:** done: ✅ | in‑progress: 🟡 | not started: ⬜

---
## Phase‑by‑Phase Checklist

### Phase 0 — Kick‑off (✅)
- [x] Create **private repo** `smart-home-bridge` on GitHub.
- [x] Add collaborators.
- [x] Add **README.md**, **diagrams/architecture.png**, this **PLAN.md**.
- [x] Add high‑level cards (Phase 1 … Phase 9).

### Phase 1 — Local dev & containers
- [ ] `edge-sim/` Python publisher → Dockerfile.
- [ ] Mosquitto broker container in `docker-compose.yml`.
- [ ] SQLite placeholder store.
- [ ] Grafana+BigQuery plugin via Docker.
- [ ] Unit tests + `make test`.

### Phase 2 — Edge VM
- [ ] Startup script `edge-init.sh` (installs Docker, pulls images, opens ports 1883/8883).
- [ ] Firewall rule tag `mqtt-edge`.
- [ ] Systemd health‑check (restarts Mosquitto).

### Phase 3 — Storage node (GCP)
- [ ] Pub/Sub topic `iot-ingest` + subscription `iot-bq-sub`.
- [ ] BigQuery dataset `iot_raw` & table `iot_events` (DAY partition, cluster `sensor_id`).
- [ ] Secrets in Secret Manager.

### Phase 4 — Cloud VM & UI
- [ ] `cloud-agg` container subscribes & writes via `google-cloud-bigquery`.
- [ ] `web-ui` (Flask + DataTables) container.
- [ ] Grafana container, BigQuery data‑source JSON provisioned.
- [ ] Cloud‑init script `cloud-init.sh`.

### Phase 5 — IaC & Automation
- [ ] `deploy.sh` bash script (or Terraform) provisioning all resources end‑to‑end.
- [ ] `destroy.sh` cleanup script.
- [ ] GitHub Action to lint Terraform / shell.

### Phase 6 — Load‑ & Scale‑Testing
- [ ] Locust scenarios: 100, 500, 2 000 vUsers.
- [ ] Monitoring dashboard JSON export.
- [ ] Autoscaling demo: Cloud Run revision with aggregator.

### Phase 7 — Evaluation & Report
- [ ] Jupyter notebook → latency histogram, throughput vs users chart.
- [ ] Cloud cost spreadsheet (BQ, Dataflow, VMs).
- [ ] Draft discussion of bottlenecks, future work.

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

