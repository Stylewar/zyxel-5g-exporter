# Docker Compose Files Guide

This project includes two docker-compose files for different deployment scenarios.

## Available Files

### 1. `docker-compose.yml` - Full Stack
**Complete monitoring solution with Exporter + Prometheus + Grafana**

Use this when:
- ✅ You want everything in one command
- ✅ You don't have existing Prometheus/Grafana
- ✅ You want a quick start for testing
- ✅ You're setting up a new monitoring stack

**Includes:**
- Cellwan Exporter (port 9101)
- Prometheus (port 9090)
- Grafana (port 3000)
- Pre-configured datasources
- Pre-loaded dashboard
- Persistent volumes for data

### 2. `docker-compose.exporter.yml` - Exporter Only
**Just the exporter service**

Use this when:
- ✅ You already have Prometheus running
- ✅ You already have Grafana running
- ✅ You want to integrate with existing monitoring
- ✅ You're running multiple exporters
- ✅ You want minimal resource usage

**Includes:**
- Cellwan Exporter only (port 9101)

---

## Usage Examples

### Full Stack Deployment

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 2. Start full stack
docker-compose up -d

# 3. Access services
# Exporter: http://localhost:9101/metrics
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Exporter Only Deployment

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 2. Start exporter only
docker-compose -f docker-compose.exporter.yml up -d

# 3. Access exporter
# Exporter: http://localhost:9101/metrics

# View logs
docker-compose -f docker-compose.exporter.yml logs -f

# Stop service
docker-compose -f docker-compose.exporter.yml down
```

---

## Configuration Comparison

| Feature | Full Stack | Exporter Only |
|---------|-----------|---------------|
| **Services** | Exporter + Prometheus + Grafana | Exporter only |
| **Ports** | 9101, 9090, 3000 | 9101 |
| **Volumes** | prometheus-data, grafana-data | None |
| **Networks** | monitoring | monitoring |
| **Memory Usage** | ~500-800 MB | ~50 MB |
| **Setup Time** | 2-3 minutes | 30 seconds |
| **Best For** | Quick start, testing, demos | Production, existing stack |

---

## Integration with Existing Prometheus

If using `docker-compose.exporter.yml`, add this to your existing Prometheus configuration:

### Option 1: Same Docker Network

```yaml
# In your existing docker-compose.yml
services:
  prometheus:
    # ... your existing prometheus config
    networks:
      - monitoring  # Join the monitoring network

networks:
  monitoring:
    external: true  # Use the external monitoring network
```

Then update your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'cellwan'
    static_configs:
      - targets: ['cellwan-exporter:9101']
```

### Option 2: Host Network

```yaml
# In docker-compose.exporter.yml, change to:
services:
  cellwan-exporter:
    network_mode: "host"
```

Then in your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'cellwan'
    static_configs:
      - targets: ['localhost:9101']
```

### Option 3: External Access

```yaml
scrape_configs:
  - job_name: 'cellwan'
    static_configs:
      - targets: ['<exporter-host-ip>:9101']
```

---

## Environment Variables

Both files use the same environment variables:

```bash
# Required
ZYXEL_HOST=192.168.1.1
ZYXEL_USER=admin
ZYXEL_PASSWORD=your_password

# Optional
EXPORTER_PORT=9101
EXPORTER_IP=0.0.0.0
SCRAPE_INTERVAL=30

# Full stack only
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

---

## Port Mapping

### Full Stack
- `9101` - Cellwan Exporter metrics endpoint
- `9090` - Prometheus web interface
- `3000` - Grafana web interface

### Exporter Only
- `9101` - Cellwan Exporter metrics endpoint

To change ports, edit the `ports:` section:

```yaml
ports:
  - "8080:9101"  # Map host port 8080 to container port 9101
```

---

## Data Persistence

### Full Stack
Creates persistent volumes:
- `prometheus-data` - Stores Prometheus metrics
- `grafana-data` - Stores Grafana dashboards and settings

**Backup:**
```bash
docker run --rm -v zyxel-5g-exporter_prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .
docker run --rm -v zyxel-5g-exporter_grafana-data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .
```

**Restore:**
```bash
docker run --rm -v zyxel-5g-exporter_prometheus-data:/data -v $(pwd):/backup alpine tar xzf /backup/prometheus-backup.tar.gz -C /data
docker run --rm -v zyxel-5g-exporter_grafana-data:/data -v $(pwd):/backup alpine tar xzf /backup/grafana-backup.tar.gz -C /data
```

### Exporter Only
No persistent volumes - stateless service

---

## Resource Requirements

### Full Stack
**Minimum:**
- CPU: 1 core
- RAM: 1 GB
- Disk: 5 GB (for metrics storage)

**Recommended:**
- CPU: 2 cores
- RAM: 2 GB
- Disk: 20 GB

### Exporter Only
**Minimum:**
- CPU: 0.1 core
- RAM: 64 MB
- Disk: 100 MB

**Recommended:**
- CPU: 0.5 core
- RAM: 128 MB
- Disk: 500 MB

---

## Switching Between Configurations

### From Full Stack to Exporter Only

```bash
# 1. Stop full stack
docker-compose down

# 2. Backup data (optional)
docker run --rm -v zyxel-5g-exporter_prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .

# 3. Start exporter only
docker-compose -f docker-compose.exporter.yml up -d
```

### From Exporter Only to Full Stack

```bash
# 1. Stop exporter
docker-compose -f docker-compose.exporter.yml down

# 2. Start full stack
docker-compose up -d
```

---

## Health Checks

Both configurations include health checks:

```bash
# Check container health
docker ps

# Should show "healthy" status:
# CONTAINER ID   STATUS
# abc123...      Up 2 minutes (healthy)

# Manual health check
curl http://localhost:9101/metrics
```

---

## Troubleshooting

### Full Stack Issues

**Prometheus can't reach exporter:**
```bash
# Check network
docker network inspect zyxel-5g-exporter_monitoring

# Check if services are on same network
docker inspect cellwan-exporter | grep Networks -A 5
docker inspect prometheus | grep Networks -A 5
```

**Grafana dashboard not loading:**
```bash
# Check provisioning directory
ls -la grafana/provisioning/dashboards/
ls -la grafana/provisioning/datasources/

# Restart Grafana
docker-compose restart grafana
```

### Exporter Only Issues

**Can't connect to router:**
```bash
# Check from inside container
docker exec -it cellwan-exporter bash
ping $ZYXEL_HOST

# Check logs
docker-compose -f docker-compose.exporter.yml logs -f
```

**Port already in use:**
```bash
# Check what's using port 9101
lsof -i :9101

# Change port in docker-compose.exporter.yml
ports:
  - "9102:9101"
```

---

## Production Recommendations

### For Full Stack
1. Change default Grafana password
2. Enable HTTPS with reverse proxy (nginx/traefik)
3. Set up proper authentication
4. Configure backup schedules
5. Monitor disk usage
6. Set Prometheus retention policy

### For Exporter Only
1. Use Docker secrets for credentials
2. Place behind firewall/VPN
3. Use read-only network for security
4. Monitor exporter uptime
5. Set up alerting in your Prometheus

---

## Examples

### Multiple Routers (Full Stack)

```yaml
# docker-compose.yml
services:
  cellwan-exporter-1:
    build: .
    container_name: cellwan-exporter-1
    ports:
      - "9101:9101"
    environment:
      - ZYXEL_HOST=192.168.1.1
      # ... other settings
      
  cellwan-exporter-2:
    build: .
    container_name: cellwan-exporter-2
    ports:
      - "9102:9101"
    environment:
      - ZYXEL_HOST=192.168.2.1
      # ... other settings
```

### Multiple Routers (Exporter Only)

```bash
# Router 1
docker-compose -f docker-compose.exporter.yml -p router1 up -d

# Router 2 (different port and env)
ZYXEL_HOST=192.168.2.1 \
  docker-compose -f docker-compose.exporter.yml -p router2 \
  -e EXPORTER_PORT=9102 up -d
```

---

## Quick Reference

```bash
# Full Stack
docker-compose up -d              # Start
docker-compose down               # Stop
docker-compose logs -f            # Logs
docker-compose ps                 # Status
docker-compose restart            # Restart all

# Exporter Only
docker-compose -f docker-compose.exporter.yml up -d
docker-compose -f docker-compose.exporter.yml down
docker-compose -f docker-compose.exporter.yml logs -f
docker-compose -f docker-compose.exporter.yml ps
docker-compose -f docker-compose.exporter.yml restart
```

---

## Choosing the Right Configuration

**Use Full Stack (`docker-compose.yml`) if:**
- 🎯 You're getting started
- 🎯 You want everything pre-configured
- 🎯 You're running a demo or POC
- 🎯 You don't have existing monitoring infrastructure

**Use Exporter Only (`docker-compose.exporter.yml`) if:**
- 🎯 You have existing Prometheus/Grafana
- 🎯 You want fine-grained control
- 🎯 You're running in production
- 🎯 You need minimal resource usage
- 🎯 You're integrating with existing monitoring stack

---

**Need help?** Open an issue on GitHub or check the main README.md for more information.
