# Complete Setup Guide for GitHub Export

This guide helps you export all project files to a GitHub repository.

## Method 1: Manual Setup (Recommended)

### Step 1: Create Local Project Directory

```bash
mkdir zyxel-5g-prometheus-exporter
cd zyxel-5g-prometheus-exporter
```

### Step 2: Create Directory Structure

```bash
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
```

### Step 3: Create All Files

You need to create the following files. All content is available in the artifacts above.

#### Root Directory Files:
1. **cellwan_exporter.py** - Main Python script (artifact: "5G Router Prometheus Exporter")
2. **Dockerfile** - Docker image definition (artifact: "Dockerfile")
3. **docker-compose.yml** - Full stack orchestration (artifact: "docker-compose.yml (Full Stack)")
4. **requirements.txt** - Python dependencies (artifact: "requirements.txt")
5. **prometheus.yml** - Prometheus config (artifact: "prometheus.yml")
6. **.env.example** - Environment template (artifact: ".env.example")
7. **.dockerignore** - Docker ignore (artifact: ".dockerignore")
8. **.gitignore** - Git ignore (artifact: ".gitignore")
9. **Makefile** - Convenience commands (artifact: "Makefile")
10. **README.md** - Documentation (artifact: "README.md (Complete)")
11. **LICENSE** - MIT License

#### Grafana Provisioning Files:
12. **grafana/provisioning/datasources/datasource.yml** (artifact: "grafana/provisioning/datasources/datasource.yml")
13. **grafana/provisioning/dashboards/dashboard.yml** (artifact: "grafana/provisioning/dashboards/dashboard.yml")
14. **grafana/provisioning/dashboards/cellwan.json** (artifact: "grafana/provisioning/dashboards/cellwan.json")

### Step 4: Create LICENSE File

```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 Zyxel 5G Prometheus Exporter Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

### Step 5: Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit: Zyxel 5G Router Prometheus Exporter

- Complete Prometheus exporter for Zyxel 5G routers
- Docker support with full monitoring stack
- Pre-configured Grafana dashboard
- Comprehensive metrics collection (RSSI, RSRP, RSRQ, SINR)
- Support for primary cell, NR5G, and secondary carriers
- Neighbor cell tracking
- Health checks and alerting
"
```

### Step 6: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `zyxel-5g-prometheus-exporter`
3. Description: `Prometheus exporter for Zyxel 5G routers with full monitoring stack`
4. Choose Public or Private
5. **Do NOT** initialize with README, .gitignore, or license (we already have them)
6. Click "Create repository"

### Step 7: Push to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/zyxel-5g-prometheus-exporter.git
git branch -M main
git push -u origin main
```

### Step 8: Add Repository Topics (Optional)

On GitHub repository page, click "⚙️" next to "About" and add topics:
- `prometheus`
- `exporter`
- `5g`
- `lte`
- `monitoring`
- `grafana`
- `docker`
- `zyxel`
- `metrics`
- `iot`

## Method 2: Using the Setup Script

### Step 1: Save the Setup Script

Save the `setup-github-repo.sh` artifact to a file and make it executable:

```bash
chmod +x setup-github-repo.sh
```

### Step 2: Run the Script

```bash
./setup-github-repo.sh
```

This creates the directory structure and basic files.

### Step 3: Copy Remaining Files

You still need to manually copy the Python script and other artifacts into the created directory structure.

### Step 4: Follow Steps 5-7 from Method 1

Initialize git, create GitHub repo, and push.

## Verification Checklist

Before pushing to GitHub, verify:

- [ ] All 14 files are created
- [ ] Directory structure is correct
- [ ] .gitignore is working (`.env` should NOT be tracked)
- [ ] Python script has correct permissions (`chmod +x cellwan_exporter.py`)
- [ ] README.md renders correctly
- [ ] All artifacts copied correctly

Test locally:
```bash
# Check file structure
tree -a

# Verify git status
git status

# Test Python script syntax
python3 -m py_compile cellwan_exporter.py

# Test Docker build
docker build -t test-build .
```

## Project Structure Verification

Your final structure should look like:

```
zyxel-5g-prometheus-exporter/
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── cellwan_exporter.py
├── docker-compose.yml
├── prometheus.yml
├── requirements.txt
└── grafana/
    └── provisioning/
        ├── dashboards/
        │   ├── cellwan.json
        │   └── dashboard.yml
        └── datasources/
            └── datasource.yml
```

Verify with:
```bash
tree -a -I '.git'
```

## Common Issues

### Issue: Permission Denied on Push

```bash
# Use SSH instead of HTTPS
git remote set-url origin git@github.com:YOUR_USERNAME/zyxel-5g-prometheus-exporter.git
```

### Issue: Large File Error

```bash
# Check for accidentally committed data volumes
git rm -r --cached prometheus-data grafana-data
git commit -m "Remove data volumes"
```

### Issue: .env Accidentally Committed

```bash
# Remove from git
git rm --cached .env
git commit -m "Remove .env from tracking"

# On GitHub, go to Settings → Secrets to rotate credentials
```

## Post-Setup Tasks

After pushing to GitHub:

1. **Add Repository Description**: Click "⚙️" next to About
2. **Add Topics**: prometheus, monitoring, 5g, lte, docker, grafana
3. **Enable Issues**: Settings → Features → Issues
4. **Add Wiki Page** (optional): Getting Started guide
5. **Create Release**: Releases → Draft a new release → v1.0.0
6. **Add GitHub Actions** (optional): For automated builds

## GitHub Actions Example (Optional)

Create `.github/workflows/docker-build.yml`:

```yaml
name: Docker Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: docker build -t cellwan-exporter .
```

## Sharing Your Repository

Add these badges to your README.md:

```markdown
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Prometheus](https://img.shields.io/badge/prometheus-compatible-orange)
```

## Need Help?

- Check all artifacts are correctly copied
- Verify file permissions
- Test Docker build locally before pushing
- Review .gitignore to ensure secrets aren't committed

---

**You're now ready to share your Zyxel 5G Router Prometheus Exporter with the world! 🚀**
