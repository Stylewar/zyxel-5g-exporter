# Docker Compose Files Summary

## Two Configurations Available

### 1. 📦 Full Stack - `docker-compose.yml`

**What it includes:**
- ✅ Cellwan Exporter
- ✅ Prometheus
- ✅ Grafana
- ✅ Pre-configured dashboards
- ✅ Persistent data volumes

**Quick start:**
```bash
docker-compose up -d
```

**Access:**
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Exporter: http://localhost:9101/metrics

**Best for:**
- Getting started quickly
- Testing and demos
- Self-contained monitoring solution
- When you don't have existing monitoring infrastructure

---

### 2. 🎯 Exporter Only - `docker-compose.exporter.yml`

**What it includes:**
- ✅ Cellwan Exporter only

**Quick start:**
```bash
docker-compose -f docker-compose.exporter.yml up -d
```

**Access:**
- Exporter: http://localhost:9101/metrics

**Best for:**
- Integration with existing Prometheus/Grafana
- Production deployments
- Minimal resource usage (~50 MB RAM)
- When you want fine-grained control
- Multi-tenant environments

---

## Quick Comparison

| Feature | Full Stack | Exporter Only |
|---------|-----------|---------------|
| **Command** | `docker-compose up -d` | `docker-compose -f docker-compose.exporter.yml up -d` |
| **Services** | 3 (Exporter, Prometheus, Grafana) | 1 (Exporter) |
| **Ports** | 9101, 9090, 3000 | 9101 |
| **RAM** | ~800 MB | ~50 MB |
| **Setup Time** | 2-3 minutes | 30 seconds |
| **Dashboard** | ✅ Included | ⚠️ Manual import needed |
| **Data Persistence** | ✅ Yes (volumes) | ❌ No (stateless) |
| **Best For** | Quick start, testing | Production, integration |

---

## Common Commands

### Full Stack
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Check status
docker-compose ps
```

### Exporter Only
```bash
# Start
docker-compose -f docker-compose.exporter.yml up -d

# Stop
docker-compose -f docker-compose.exporter.yml down

# View logs
docker-compose -f docker-compose.exporter.yml logs -f

# Restart
docker-compose -f docker-compose.exporter.yml restart

# Check status
docker-compose -f docker-compose.exporter.yml ps
```

### Using Makefile (Easier!)
```bash
# Full Stack
make run              # Start
make stop             # Stop
make logs             # View logs
make restart          # Restart

# Exporter Only
make run-exporter     # Start
make stop-exporter    # Stop
make logs-exporter    # View logs
make restart-exporter # Restart
```

---

## When to Use Which?

### Choose Full Stack if:
- 🎯 You're just getting started
- 🎯 You want to test the exporter quickly
- 🎯 You need a demo or proof of concept
- 🎯 You don't have Prometheus/Grafana yet
- 🎯 You want everything pre-configured
- 🎯 You're okay with ~800 MB RAM usage

### Choose Exporter Only if:
- 🎯 You already have Prometheus running
- 🎯 You already have Grafana running
- 🎯 You're deploying to production
- 🎯 You want minimal resource usage
- 🎯 You need to monitor multiple routers
- 🎯 You have existing monitoring infrastructure
- 🎯 You want maximum flexibility

---

## Integration Examples

### Integrating Exporter Only with Existing Prometheus

#### Option 1: Same Docker Network
```yaml
# Your existing docker-compose.yml
services:
  prometheus:
    # ... your config
    networks:
      - monitoring

# Use the monitoring network
networks:
  monitoring:
    external: true
```

Add to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'cellwan'
    static_configs:
      - targets: ['cellwan-exporter:9101']
```

#### Option 2: Host Network
```bash
# Run exporter with host network
docker run -d --network host \
  -e ZYXEL_HOST=192.168.1.1 \
  -e ZYXEL_USER=admin \
  -e ZYXEL_PASSWORD=secret \
  cellwan-exporter
```

Add to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'cellwan'
    static_configs:
      - targets: ['localhost:9101']
```

#### Option 3: External Access
Add to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'cellwan'
    static_configs:
      - targets: ['<exporter-host-ip>:9101']
```

---

## Switching Between Configurations

### From Full Stack to Exporter Only
```bash
# 1. Stop full stack
docker-compose down

# 2. Optional: Backup data
docker run --rm \
  -v zyxel-5g-exporter_prometheus-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz -C /data .

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

## Environment Variables

Both configurations use the same `.env` file:

```bash
# Required
ZYXEL_HOST=192.168.1.1
ZYXEL_USER=admin
ZYXEL_PASSWORD=your_password_here

# Optional
EXPORTER_PORT=9101
EXPORTER_IP=0.0.0.0
SCRAPE_INTERVAL=30

# Full stack only
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

---

## Resource Usage

### Full Stack
- **CPU**: 1-2 cores
- **RAM**: 500-800 MB
- **Disk**: 5-20 GB (for metrics storage)

### Exporter Only
- **CPU**: 0.1-0.5 core
- **RAM**: 50-100 MB
- **Disk**: 100-500 MB

---

## Troubleshooting

### Full Stack Issues

**Problem: Grafana dashboard not loading**
```bash
# Check if files exist
ls -la grafana/provisioning/dashboards/
ls -la grafana/provisioning/datasources/

# Restart Grafana
docker-compose restart grafana
```

**Problem: Prometheus can't scrape exporter**
```bash
# Check if on same network
docker network inspect zyxel-5g-exporter_monitoring

# Check Prometheus targets
# Open http://localhost:9090/targets
```

### Exporter Only Issues

**Problem: Can't connect to router**
```bash
# Check from inside container
docker exec -it cellwan-exporter ping $ZYXEL_HOST

# Check logs
docker-compose -f docker-compose.exporter.yml logs -f
```

**Problem: Port already in use**
```bash
# Check what's using the port
lsof -i :9101

# Change port in docker-compose.exporter.yml
ports:
  - "9102:9101"
```

---

## Multiple Routers

### With Full Stack
Edit `docker-compose.yml`:
```yaml
services:
  cellwan-exporter-1:
    build: .
    container_name: cellwan-exporter-1
    ports:
      - "9101:9101"
    environment:
      - ZYXEL_HOST=192.168.1.1
      - ZYXEL_USER=admin
      - ZYXEL_PASSWORD=secret1
      
  cellwan-exporter-2:
    build: .
    container_name: cellwan-exporter-2
    ports:
      - "9102:9101"
    environment:
      - ZYXEL_HOST=192.168.2.1
      - ZYXEL_USER=admin
      - ZYXEL_PASSWORD=secret2
```

### With Exporter Only
Run multiple instances with different projects:
```bash
# Router 1
docker-compose -f docker-compose.exporter.yml -p router1 up -d

# Router 2 (create .env.router2)
docker-compose -f docker-compose.exporter.yml -p router2 --env-file .env.router2 up -d
```

---

## Testing

### Verify Exporter Works
```bash
# Check metrics endpoint
curl http://localhost:9101/metrics

# Check specific metric
curl http://localhost:9101/metrics | grep cellwan_status_up

# Verify no IMEI exposed (privacy check)
curl http://localhost:9101/metrics | grep -i imei
# Should return nothing
```

### Verify Full Stack
```bash
# Check all services
docker-compose ps

# Should show all as "Up" and "healthy"
# Test Grafana
curl http://localhost:3000/api/health

# Test Prometheus
curl http://localhost:9090/-/healthy
```

---

## Migration Paths

### Scenario 1: Testing → Production

**Start:** Full Stack for testing
```bash
docker-compose up -d
```

**Migrate to:** Exporter Only + Existing Monitoring
```bash
# 1. Export Grafana dashboard
# Save dashboard JSON from Grafana UI

# 2. Stop full stack
docker-compose down

# 3. Deploy exporter only
docker-compose -f docker-compose.exporter.yml up -d

# 4. Add to existing Prometheus
# 5. Import dashboard to existing Grafana
```

### Scenario 2: Standalone → Centralized

**Start:** Multiple standalone full stacks
```bash
# Router 1
cd router1 && docker-compose up -d

# Router 2  
cd router2 && docker-compose up -d
```

**Migrate to:** Multiple exporters + Central monitoring
```bash
# Stop standalone stacks
cd router1 && docker-compose down
cd router2 && docker-compose down

# Start exporters only
cd router1 && docker-compose -f docker-compose.exporter.yml up -d
cd router2 && docker-compose -f docker-compose.exporter.yml up -d

# Configure central Prometheus to scrape both
```

---

## Best Practices

### For Full Stack
✅ Change default Grafana password immediately
✅ Set Prometheus retention policy based on disk space
✅ Regular backups of volumes
✅ Monitor disk usage
✅ Use reverse proxy with HTTPS for external access

### For Exporter Only
✅ Use Docker secrets for credentials in production
✅ Place behind firewall/VPN
✅ Monitor exporter uptime in your Prometheus
✅ Set up alerting for exporter down
✅ Document Prometheus scrape configuration

---

## Quick Decision Tree

```
Do you already have Prometheus/Grafana?
├── NO  → Use Full Stack (docker-compose.yml)
│        Quick start, everything included
│
└── YES → Use Exporter Only (docker-compose.exporter.yml)
         Minimal footprint, easy integration

Are you just testing?
├── YES → Use Full Stack (docker-compose.yml)
│        Easy setup and teardown
│
└── NO  → Use Exporter Only (docker-compose.exporter.yml)
         Production-ready, minimal resources

Do you need to monitor multiple routers?
├── 1-2 Routers  → Either works fine
├── 3-5 Routers  → Prefer Exporter Only per router + Central monitoring
└── 5+ Routers   → Definitely Exporter Only + Central monitoring
```

---

## Support & Documentation

- 📖 Full deployment guide: [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md)
- 📝 Main documentation: [README.md](README.md)
- 🔒 Privacy information: [PRIVACY_CHANGES.md](PRIVACY_CHANGES.md)
- ❓ Issues: Open an issue on GitHub

---

## Summary

**TL;DR:**

- 🚀 **Getting started?** → Use `docker-compose up -d`
- 🏢 **Production/Integration?** → Use `docker-compose -f docker-compose.exporter.yml up -d`
- 📚 **Need details?** → Read [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md)
- 🛠️ **Prefer shortcuts?** → Use `make run` or `make run-exporter`

Both configurations are fully tested and production-ready. Choose based on your needs! 🎯
