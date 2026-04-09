# Zyxel 5G Router Prometheus Exporter

Prometheus exporter for Zyxel 5G routers that collects `cfg cellwan_status get`
over SSH and exposes LTE / NR5G / SCC / neighbor-cell metrics on `/metrics`.

The repository ships the exporter itself plus two Grafana dashboards. It does
not include a full Prometheus + Grafana stack anymore; `docker-compose.yml`
starts the exporter only.

## Features

- Collects primary LTE cell metrics such as RSSI, RSRP, RSRQ, SINR, CQI, MCS,
  PCI, and bandwidth
- Collects NR5G metrics such as RSRP, RSRQ, SINR, PCI, RFCN, and bandwidth
- Collects secondary-carrier and neighbor-cell metrics
- Exposes `cellwan_info`, `cellwan_status_up`, `cellwan_scrape_success`, and `cellwan_ca_band_active`
- Clears stale SCC and neighbor series when the router state changes
- Avoids exposing IMEI and module software version
- Includes CI for Python syntax, parser regression tests, linting, and
  tag-driven image releases

## Quick Start

### Docker Compose

Use the included compose file when you only want to run the exporter locally.

```bash
cp .env.example .env
# edit .env with your router credentials
docker compose up -d --build
curl http://localhost:9101/metrics
```

### Python

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
# edit .env with your router credentials
python3 cellwan_exporter.py
```

## Prometheus Scrape Config

Add the exporter to your existing Prometheus:

```yaml
scrape_configs:
  - job_name: "zyxel-cellwan-exporter"
    static_configs:
      - targets: ["192.168.1.50:9101"]
```

The example [prometheus.yml](/workspace/zyxel-5g-exporter/prometheus.yml) shows
the same setup for container-based deployment.

## Dashboards

The repository contains two dashboards:

- [cellwan_reduced.json](/workspace/zyxel-5g-exporter/grafana/provisioning/dashboards/cellwan_reduced.json)
  is the recommended day-to-day dashboard. It is compact and shows connection
  status, network information, primary LTE, NR5G, bandwidth, and SCC panels.
- [cellwan.json](/workspace/zyxel-5g-exporter/grafana/provisioning/dashboards/cellwan.json)
  is the expanded dashboard. It includes a metrics guide, additional PCI /
  handover history panels, and more explanatory context for analysis.

Current practical difference:

- the reduced dashboard has a `Network Information` stat panel based on
  `cellwan_info`
- the full dashboard focuses more on radio and handover analysis and does not
  have that panel

If `ca_combination` changes over time, Grafana can otherwise see multiple
historical `cellwan_info` series. The reduced dashboard now uses an instant
query for that panel so the current series renders reliably.

## Metrics

Important exported metrics:

- `cellwan_info`
  Labels: `network`, `access_technology`, `ca_combination`
- `cellwan_status_up`
  `1` when the router reports the cellular WAN as up
- `cellwan_scrape_success`
  `1` when the latest SSH scrape succeeded
- `cellwan_ca_band_active`
  `1` for each currently active LTE / NR carrier-aggregation band, labeled as `B1`, `B3`, `n28`, and so on
- `cellwan_primary_*`
  Primary LTE cell metrics
- `cellwan_nr5g_*`
  NR5G metrics
- `cellwan_scc_*`
  Secondary carrier metrics
- `cellwan_neighbor_*`
  Neighbor cell metrics

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ZYXEL_HOST` | Router IP address or hostname | Required |
| `ZYXEL_USER` | SSH username | Required |
| `ZYXEL_PASSWORD` | SSH password | Required |
| `EXPORTER_PORT` | Prometheus exporter port | `9101` |
| `EXPORTER_IP` | Exporter bind address | `0.0.0.0` |
| `SCRAPE_INTERVAL` | Seconds between scrapes | `30` |
| `DEBUG` | Enable debug logging | `false` |

## Development

Useful local commands:

```bash
make help
make build
make run
make test
make dev-test
make lint
```

CI / release model:

- pushes to `main` run checks and build the mutable image path
- semantic version tags such as `v1.1.2` publish release image tags
- current releases:
  - `v1.1.0`
  - `v1.1.1`
  - `v1.1.2`

## Security And Privacy

- The exporter uses SSH to log into the router and run `cfg cellwan_status get`
- IMEI and module software version are intentionally not exported
- Keep `.env` out of version control
- Restrict access to the exporter endpoint if it is exposed outside your LAN

## Troubleshooting

Basic checks:

```bash
curl http://localhost:9101/metrics
sshpass -p "password" ssh -tt user@192.168.1.1
python3 -m unittest discover -s tests -v
```

If the exporter is reachable but the router scrape is failing, check:

- `cellwan_scrape_success`
- exporter logs
- SSH connectivity and credentials

If Grafana panels look wrong after importing dashboards, verify that the panel
queries match the exported metric names on `/metrics`.
