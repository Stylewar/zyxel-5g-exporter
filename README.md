# Zyxel 5G Router Prometheus Exporter

A complete monitoring solution for Zyxel 5G routers that collects cellular WAN status metrics via SSH and provides a full Prometheus + Grafana stack.

## Recent Updates

**v1.1.0 (2024-10-18)** - Privacy & Dashboard Improvements
- 🔒 Removed IMEI and module version for privacy compliance (GDPR)
- 📊 Added datasource selector to dashboard for multi-Prometheus support
- 🎨 Reorganized dashboard with grouped Primary LTE and NR5G sections
- 📈 Added color-coded stat panels with quality thresholds
- See [PRIVACY_CHANGES.md](PRIVACY_CHANGES.md) for details

## Features

- 🚀 Collects comprehensive 5G/LTE metrics (RSSI, RSRP, RSRQ, SINR)
- 📊 Supports primary cell, NR5G, and secondary carrier (SCC) metrics
- 📡 Neighbor cell information tracking
- ⚙️ Configurable scrape interval
- 🐳 Complete Docker stack with Prometheus and Grafana
- 📈 Pre-configured Grafana dashboard with grouped metrics
- 🔒 Privacy-focused: No personal identifiable information collected
- 💚 Health checks included

## Quick Start (Full Stack)

This will start the exporter, Prometheus, and Grafana:

1. **Clone and setup**:
```bash
git clone <your-repo>
cd zyxel-exporter
cp .env.example .env
```

2. **Edit `.env`** with your router credentials:
```bash
ZYXEL_HOST=192.168.1.1
ZYXEL_USER=admin
ZYXEL_PASSWORD=your_password
```

3. **Create required directories**:
```bash
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
```

4. **Start the stack**:
```bash
docker-compose up -d
```

5. **Access the services**:
   - **Grafana**: http://localhost:3000 (admin/admin)
   - **Prometheus**: http://localhost:9090
   - **Exporter Metrics**: http://localhost:9101/metrics

## Quick Start (Exporter Only)

If you already have Prometheus/Grafana or want just the exporter:

### Using Python

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run exporter
python cellwan_exporter.py
```

### Using Docker

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

## Project Structure

```
.
├── cellwan_exporter.py           # Main exporter script
├── Dockerfile                     # Container image definition
├── docker-compose.yml             # Full stack orchestration
├── requirements.txt               # Python dependencies
├── prometheus.yml                 # Prometheus configuration
├── .env.example                   # Environment variables template
├── .dockerignore                  # Docker build exclusions
├── Makefile                       # Convenience commands
├── README.md                      # This file
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── datasource.yml     # Prometheus datasource
        └── dashboards/
            ├── dashboard.yml      # Dashboard provider
            └── cellwan.json       # Pre-built dashboard
```

## Command Line Usage

```
usage: cellwan_exporter.py [-h] [--host HOST] [--user USER] [--password PASSWORD] 
                           [--port PORT] [--listen LISTEN] [--interval INTERVAL]

Zyxel 5G Router Prometheus Exporter

optional arguments:
  -h, --help           Show help message
  --host HOST          Router hostname or IP address
  --user USER          SSH username
  --password PASSWORD  SSH password
  --port PORT          Prometheus exporter port (default: 9101)
  --listen LISTEN      IP address to bind (default: 0.0.0.0)
  --interval INTERVAL  Scrape interval in seconds (default: 30)
```

### Examples

```bash
# Using command line arguments
python cellwan_exporter.py --host 192.168.1.1 --user admin --password secret

# Custom port and interval
python cellwan_exporter.py --host 192.168.1.1 --user admin --password secret \
  --port 9100 --interval 60

# Using environment variables
export ZYXEL_HOST=192.168.1.1
export ZYXEL_USER=admin
export ZYXEL_PASSWORD=secret
python cellwan_exporter.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ZYXEL_HOST` | Router IP address or hostname | Required |
| `ZYXEL_USER` | SSH username | Required |
| `ZYXEL_PASSWORD` | SSH password | Required |
| `EXPORTER_PORT` | Prometheus exporter port | 9101 |
| `EXPORTER_IP` | IP to bind exporter | 0.0.0.0 |
| `SCRAPE_INTERVAL` | Seconds between scrapes | 30 |
| `GRAFANA_USER` | Grafana admin username | admin |
| `GRAFANA_PASSWORD` | Grafana admin password | admin |

## Exposed Metrics

### Info Metrics
- `cellwan_info` - Router information (network, access technology, CA combination)
  - **Note**: IMEI and module version are NOT collected for privacy protection

### Status Metrics
- `cellwan_status_up` - Connection status (1=Up, 0=Down)

### Primary LTE Cell Metrics
- `cellwan_primary_rssi_dbm` - RSSI in dBm
- `cellwan_primary_rsrp_dbm` - RSRP in dBm
- `cellwan_primary_rsrq_db` - RSRQ in dB
- `cellwan_primary_sinr_db` - SINR in dB
- `cellwan_primary_cqi` - Channel Quality Indicator
- `cellwan_primary_mcs` - Modulation and Coding Scheme
- `cellwan_primary_ri` - Rank Indicator
- `cellwan_primary_pmi` - Precoding Matrix Indicator
- `cellwan_primary_bandwidth_ul_mhz` - Uplink bandwidth
- `cellwan_primary_bandwidth_dl_mhz` - Downlink bandwidth
- `cellwan_primary_physical_cell_id` - Physical cell ID
- `cellwan_primary_rfcn` - Radio Frequency Channel Number

### NR5G Metrics
- `cellwan_nr5g_rsrp_dbm` - NR5G RSRP
- `cellwan_nr5g_rsrq_db` - NR5G RSRQ
- `cellwan_nr5g_sinr_db` - NR5G SINR
- `cellwan_nr5g_bandwidth_dl_mhz` - NR5G downlink bandwidth
- `cellwan_nr5g_physical_cell_id` - NR5G physical cell ID
- `cellwan_nr5g_rfcn` - NR5G RFCN

### Secondary Carrier (SCC) Metrics
- `cellwan_scc_rssi_dbm` - SCC RSSI (labels: scc_index, band, physical_cell_id)
- `cellwan_scc_rsrp_dbm` - SCC RSRP
- `cellwan_scc_rsrq_db` - SCC RSRQ
- `cellwan_scc_sinr_db` - SCC SINR
- `cellwan_scc_bandwidth_dl_mhz` - SCC downlink bandwidth
- `cellwan_scc_rfcn` - SCC RFCN

### Neighbor Cell Metrics
- `cellwan_neighbor_rssi_dbm` - Neighbor RSSI
- `cellwan_neighbor_rsrp_dbm` - Neighbor RSRP
- `cellwan_neighbor_rsrq_db` - Neighbor RSRQ

All metrics include appropriate labels for filtering (band, cell_id, enodeb_id, etc.)

## Makefile Commands

Convenient shortcuts for common tasks:

```bash
make help       # Show available commands
make build      # Build Docker image
make run        # Start containers
make stop       # Stop containers
make restart    # Restart containers
make logs       # View container logs
make clean      # Remove containers and images
make test       # Test exporter endpoint
make install    # Install Python dependencies
```

## Grafana Dashboard

The included dashboard provides:

- **Connection Status** - Visual indicator of Up/Down state
- **Network Information** - Operator, technology, bands (no IMEI/device info)
- **Primary LTE Cell Section** - Grouped LTE metrics (RSRP, RSSI, SINR, RSRQ)
- **NR5G Cell Section** - Grouped 5G metrics (RSRP, SINR, RSRQ, Bandwidth)
- **Signal Quality Comparison** - LTE vs 5G comparison charts
- **Bandwidth Usage** - Primary, NR5G, and SCC bandwidth
- **Secondary Carriers** - Individual SCC signal strength and quality
- **Datasource Selector** - Switch between multiple Prometheus instances

### Dashboard Features

- Color-coded metrics with quality thresholds:
  - 🔴 Red: Poor signal
  - 🟠 Orange: Fair signal  
  - 🟡 Yellow: Good signal
  - 🟢 Green: Excellent signal
- Grouped panels by cell type (Primary LTE / NR5G)
- Statistics in legends (last, mean, min, max)
- Auto-refresh every 30 seconds

1. Access Grafana at http://localhost:3000
2. Navigate to Dashboards → "5G Router Cellular Metrics"
3. Click the gear icon to edit
4. Modify panels or add new ones
5. Save changes

## PromQL Examples

Useful Prometheus queries:

```promql
# Primary cell signal strength
cellwan_primary_rsrp_dbm

# NR5G signal quality
cellwan_nr5g_sinr_db

# Connection uptime percentage (last 24h)
avg_over_time(cellwan_status_up[24h]) * 100

# Total bandwidth
cellwan_primary_bandwidth_dl_mhz + 
cellwan_nr5g_bandwidth_dl_mhz + 
sum(cellwan_scc_bandwidth_dl_mhz)

# Signal quality alerts
cellwan_primary_sinr_db < 10 or cellwan_nr5g_sinr_db < 10

# Average RSRP per band
avg(cellwan_primary_rsrp_dbm) by (band)
```

## Alerting Examples

Add to `prometheus.yml` under `rule_files`:

```yaml
groups:
  - name: cellwan_alerts
    interval: 30s
    rules:
      - alert: CellwanDown
        expr: cellwan_status_up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "5G Router connection is down"
          
      - alert: PoorSignalQuality
        expr: cellwan_primary_sinr_db < 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Poor signal quality detected (SINR < 5dB)"
```

## Security Best Practices

⚠️ **Important Security Notes**:

1. **Never commit** `.env` file with real credentials to version control
2. Add `.env` to `.gitignore` (already included)
3. Use strong passwords for router and Grafana
4. Consider SSH key authentication instead of passwords
5. Restrict network access to exporter/Grafana ports
6. **Privacy**: No IMEI or device identifiers are collected or exposed
7. Use Docker secrets in production:

```yaml
# docker-compose.yml production example
services:
  cellwan-exporter:
    secrets:
      - zyxel_password
    environment:
      ZYXEL_PASSWORD_FILE: /run/secrets/zyxel_password

secrets:
  zyxel_password:
    file: ./secrets/zyxel_password.txt
```

## Troubleshooting

### SSH Connection Issues

**Test SSH manually:**
```bash
sshpass -p "password" ssh user@192.168.1.1 "cfg cellwan_status get"
```

**Fix host key verification:**
```bash
ssh-keyscan -H 192.168.1.1 >> ~/.ssh/known_hosts
```

### Docker Issues

**View logs:**
```bash
docker-compose logs -f cellwan-exporter
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

**Check container health:**
```bash
docker ps
docker inspect cellwan-exporter
```

**Restart specific service:**
```bash
docker-compose restart cellwan-exporter
```

**Rebuild after code changes:**
```bash
docker-compose up -d --build
```

### Metrics Not Appearing

**Test exporter endpoint:**
```bash
curl http://localhost:9101/metrics
```

**Check Prometheus targets:**
- Open http://localhost:9090/targets
- Verify cellwan-exporter shows as "UP"

**Verify Prometheus can reach exporter:**
```bash
docker-compose exec prometheus wget -qO- http://cellwan-exporter:9101/metrics
```

### Grafana Issues

**Reset admin password:**
```bash
docker-compose exec grafana grafana-cli admin reset-admin-password newpassword
```

**Check datasource connection:**
- Grafana → Configuration → Data Sources → Prometheus
- Click "Test" button

**Dashboard not loading:**
- Check `grafana/provisioning/dashboards/` files exist
- Verify correct permissions on mounted volumes
- Restart Grafana: `docker-compose restart grafana`

### Parser Errors

If the router output format changes:

1. Capture raw output:
```bash
python cellwan_exporter.py --host 192.168.1.1 --user admin --password secret 2>&1 | tee output.log
```

2. Check the parser logic in `parse_cellwan_status()` function
3. Submit an issue with the output format

## Performance Considerations

- **Scrape Interval**: Default 30s is recommended. Lower values increase SSH overhead
- **SSH Timeout**: 30 seconds timeout protects against hanging connections
- **Resource Usage**: Minimal - exporter uses ~50MB RAM
- **Network Impact**: ~1KB per scrape

## Requirements

### System Requirements
- Python 3.11+ (for standalone)
- Docker & Docker Compose (for containerized deployment)
- Network access to router SSH port (typically 22)

### Python Dependencies
```
prometheus-client==0.19.0
python-dotenv==1.0.0
```

### System Packages (for standalone)
- sshpass
- openssh-client

**Install on Ubuntu/Debian:**
```bash
apt-get install sshpass openssh-client
```

**Install on macOS:**
```bash
brew install sshpass
```

## Router Configuration

Ensure SSH access is enabled on your Zyxel router:

1. Login to router web interface
2. Navigate to System → Remote Management
3. Enable SSH access
4. Set SSH port (default: 22)
5. Create/use admin credentials

## Development

### Project Setup

```bash
# Clone repository
git clone <your-repo>
cd zyxel-exporter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python cellwan_exporter.py --host 192.168.1.1 --user admin --password secret
```

### Adding New Metrics

1. Add metric definition in `cellwan_exporter.py`:
```python
new_metric = Gauge('cellwan_new_metric', 'Description', ['label1', 'label2'])
```

2. Parse the value in `parse_cellwan_status()`:
```python
data['new_field'] = value_part
```

3. Update metric in `update_metrics()`:
```python
value = safe_float(data.get('new_field'))
if value is not None:
    new_metric.labels(label1=x, label2=y).set(value)
```

4. Document in README and update Grafana dashboard

### Testing

**Manual test:**
```bash
# Run exporter
python cellwan_exporter.py --host 192.168.1.1 --user admin --password secret

# In another terminal, check metrics
curl http://localhost:9101/metrics | grep cellwan
```

**Docker test:**
```bash
make build
make run
make test
make logs
```

## Deployment Scenarios

### Scenario 1: Standalone Exporter

Use when you already have Prometheus/Grafana:

```bash
# Run only the exporter
docker run -d \
  --name cellwan-exporter \
  --restart unless-stopped \
  -p 9101:9101 \
  -e ZYXEL_HOST=192.168.1.1 \
  -e ZYXEL_USER=admin \
  -e ZYXEL_PASSWORD=secret \
  cellwan-exporter
```

Add to existing `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'cellwan'
    static_configs:
      - targets: ['<exporter-host>:9101']
```

### Scenario 2: Full Stack

Complete monitoring solution with Prometheus + Grafana:

```bash
docker-compose up -d
```

Access at:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Metrics: http://localhost:9101/metrics

### Scenario 3: Multiple Routers

Monitor multiple routers by running multiple exporter instances:

```yaml
# docker-compose.yml
version: '3.8'

services:
  cellwan-exporter-router1:
    build: .
    container_name: cellwan-exporter-router1
    restart: unless-stopped
    ports:
      - "9101:9101"
    environment:
      - ZYXEL_HOST=192.168.1.1
      - ZYXEL_USER=admin
      - ZYXEL_PASSWORD=${ROUTER1_PASSWORD}

  cellwan-exporter-router2:
    build: .
    container_name: cellwan-exporter-router2
    restart: unless-stopped
    ports:
      - "9102:9101"
    environment:
      - ZYXEL_HOST=192.168.2.1
      - ZYXEL_USER=admin
      - ZYXEL_PASSWORD=${ROUTER2_PASSWORD}
```

Update `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'cellwan'
    static_configs:
      - targets: ['cellwan-exporter-router1:9101']
        labels:
          router: 'router1'
          location: 'office'
      - targets: ['cellwan-exporter-router2:9101']
        labels:
          router: 'router2'
          location: 'datacenter'
```

## Production Deployment Checklist

- [ ] Change default Grafana password
- [ ] Use strong router credentials
- [ ] Enable HTTPS for Grafana (reverse proxy)
- [ ] Set up firewall rules (restrict access to 9090, 9101, 3000)
- [ ] Configure Prometheus retention policy
- [ ] Set up alerting rules
- [ ] Configure alert notifications (Slack, email, etc.)
- [ ] Enable persistent volumes for data
- [ ] Set up backup for Prometheus/Grafana data
- [ ] Monitor exporter health in Prometheus
- [ ] Document router-specific settings
- [ ] Test failure scenarios (network loss, router reboot)
- [ ] Set up log rotation for container logs

## Backup and Recovery

### Backup Prometheus Data
```bash
# Stop Prometheus
docker-compose stop prometheus

# Backup data
tar -czf prometheus-backup-$(date +%Y%m%d).tar.gz -C /var/lib/docker/volumes prometheus-data

# Restart Prometheus
docker-compose start prometheus
```

### Backup Grafana Dashboards
```bash
# Export all dashboards
docker-compose exec grafana grafana-cli admin export-dashboard > dashboards-backup.json

# Or backup entire Grafana volume
tar -czf grafana-backup-$(date +%Y%m%d).tar.gz -C /var/lib/docker/volumes grafana-data
```

### Restore
```bash
# Stop services
docker-compose down

# Restore volumes
tar -xzf prometheus-backup-YYYYMMDD.tar.gz -C /var/lib/docker/volumes
tar -xzf grafana-backup-YYYYMMDD.tar.gz -C /var/lib/docker/volumes

# Start services
docker-compose up -d
```

## Integration Examples

### Alertmanager Integration

Add to `docker-compose.yml`:
```yaml
  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    restart: unless-stopped
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager-data:/alertmanager
    networks:
      - monitoring
```

### Home Assistant Integration

Use Prometheus integration in Home Assistant:
```yaml
# configuration.yaml
prometheus:
  namespace: homeassistant

sensor:
  - platform: rest
    name: "5G Signal Strength"
    resource: http://localhost:9101/metrics
    value_template: "{{ value | regex_findall_index('cellwan_primary_rsrp_dbm ([-0-9.]+)') }}"
    unit_of_measurement: "dBm"
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Reporting Issues

Please include:
- Router model and firmware version
- Output of `cfg cellwan_status get`
- Error messages from exporter logs
- Docker/Python version

## Changelog

### v1.1.0 (2024-10-18)
- 🔒 **Privacy**: Removed IMEI and module version from metrics (GDPR compliance)
- 📊 **Dashboard**: Added datasource selector variable for multi-Prometheus support
- 🎨 **Dashboard**: Reorganized into Primary LTE and NR5G sections with clear headers
- 📈 **Dashboard**: Added color-coded stat panels with signal quality thresholds
- 📁 **Dashboard**: Improved layout with comparison and SCC sections
- 📝 **Docs**: Added PRIVACY_CHANGES.md with detailed changelog
- 📝 **Docs**: Updated README with privacy information

### v1.0.0 (2024-10-14)
- Initial release
- Full 5G/LTE metrics support
- Docker deployment
- Grafana dashboard included
- Multi-router support

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Prometheus project for the excellent metrics system
- Grafana for visualization platform
- Zyxel for router hardware

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: This README

## Related Projects

- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [prometheus-client](https://github.com/prometheus/client_python)

---

**Happy Monitoring!** 📊📡
