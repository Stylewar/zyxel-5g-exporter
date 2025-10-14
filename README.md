# Zyxel 5G Router Prometheus Exporter

A Prometheus exporter for Zyxel 5G routers that collects cellular WAN status metrics via SSH.

## Features

- Collects comprehensive 5G/LTE metrics including RSSI, RSRP, RSRQ, SINR
- Supports primary cell, NR5G, and secondary carrier (SCC) metrics
- Neighbor cell information
- Configurable scrape interval
- Docker support with health checks
- Credentials via environment variables or .env file

## Quick Start

### Using Python directly

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your router credentials
```

3. Run the exporter:
```bash
python cellwan_exporter.py
```

Or with command-line arguments:
```bash
python cellwan_exporter.py --host 192.168.1.1 --user admin --password secret --interval 30
```

### Using Docker

1. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your router credentials
```

2. Build and run:
```bash
docker-compose up -d
```

Or build manually:
```bash
docker build -t cellwan-exporter .
docker run -d \
  --name cellwan-exporter \
  -p 9101:9101 \
  -e ZYXEL_HOST=192.168.1.1 \
  -e ZYXEL_USER=admin \
  -e ZYXEL_PASSWORD=secret \
  cellwan-exporter
```

## Usage

### Command Line Arguments

```
usage: cellwan_exporter.py [-h] [--host HOST] [--user USER] [--password PASSWORD] 
                           [--port PORT] [--listen LISTEN] [--interval INTERVAL]

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          Router hostname or IP address
  --user USER          SSH username
  --password PASSWORD  SSH password
  --port PORT          Prometheus exporter port (default: 9101)
  --listen LISTEN      IP address to bind exporter (default: 0.0.0.0)
  --interval INTERVAL  Scrape interval in seconds (default: 30)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ZYXEL_HOST` | Router IP address or hostname | - |
| `ZYXEL_USER` | SSH username | - |
| `ZYXEL_PASSWORD` | SSH password | - |
| `EXPORTER_PORT` | Prometheus exporter port | 9101 |
| `EXPORTER_IP` | IP to bind exporter | 0.0.0.0 |
| `SCRAPE_INTERVAL` | Seconds between scrapes | 30 |

## Exposed Metrics

### Info Metrics
- `cellwan_info` - General router information (IMEI, module version, network, etc.)

### Status Metrics
- `cellwan_status_up` - Connection status (1=Up, 0=Down)

### Primary Cell Metrics
- `cellwan_primary_rssi_dbm` - RSSI in dBm
- `cellwan_primary_rsrp_dbm` - RSRP in dBm
- `cellwan_primary_rsrq_db` - RSRQ in dB
- `cellwan_primary_sinr_db` - SINR in dB
- `cellwan_primary_cqi` - Channel Quality Indicator
- `cellwan_primary_mcs` - Modulation and Coding Scheme
- `cellwan_primary_bandwidth_ul_mhz` - Uplink bandwidth
- `cellwan_primary_bandwidth_dl_mhz` - Downlink bandwidth
- And more...

### NR5G Metrics
- `cellwan_nr5g_rsrp_dbm` - NR5G RSRP
- `cellwan_nr5g_rsrq_db` - NR5G RSRQ
- `cellwan_nr5g_sinr_db` - NR5G SINR
- `cellwan_nr5g_bandwidth_dl_mhz` - NR5G downlink bandwidth

### Secondary Carrier (SCC) Metrics
- `cellwan_scc_rssi_dbm` - SCC RSSI
- `cellwan_scc_rsrp_dbm` - SCC RSRP
- `cellwan_scc_rsrq_db` - SCC RSRQ
- `cellwan_scc_sinr_db` - SCC SINR

### Neighbor Cell Metrics
- `cellwan_neighbor_rssi_dbm` - Neighbor cell RSSI
- `cellwan_neighbor_rsrp_dbm` - Neighbor cell RSRP
- `cellwan_neighbor_rsrq_db` - Neighbor cell RSRQ

All metrics include appropriate labels for filtering and aggregation.

## Prometheus Configuration

Add this to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'cellwan'
    static_configs:
      - targets: ['localhost:9101']
    scrape_interval: 30s
```

## Grafana Dashboard

Example PromQL queries:

```promql
# Primary cell RSRP
cellwan_primary_rsrp_dbm

# NR5G signal quality
cellwan_nr5g_sinr_db

# Connection status
cellwan_status_up

# Bandwidth usage
cellwan_primary_bandwidth_dl_mhz
```

## Security Notes

- **Never commit** `.env` file with real credentials
- Use Docker secrets or secure credential management in production
- Consider using SSH keys instead of passwords
- Restrict network access to the exporter port

## Troubleshooting

### SSH Connection Issues

1. Test SSH manually:
```bash
sshpass -p "password" ssh user@host "cfg cellwan_status get"
```

2. Check SSH host key issues:
```bash
ssh-keyscan -H 192.168.1.1 >> ~/.ssh/known_hosts
```

### Docker Issues

View logs:
```bash
docker-compose logs -f cellwan-exporter
```

Check container health:
```bash
docker ps
```

### Metric Issues

Test the exporter endpoint:
```bash
curl http://localhost:9101/metrics
```

## Requirements

- Python 3.11+
- sshpass
- openssh-client
- Router with SSH access enabled

## License

MIT

## Contributing

Pull requests welcome!
