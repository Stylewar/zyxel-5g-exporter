# Setup Checklist

## Files to Copy from Artifacts

- [ ] cellwan_exporter.py
- [ ] Dockerfile
- [ ] docker-compose.yml
- [ ] prometheus.yml
- [ ] Makefile
- [ ] README.md
- [ ] grafana/provisioning/datasources/datasource.yml
- [ ] grafana/provisioning/dashboards/dashboard.yml
- [ ] grafana/provisioning/dashboards/cellwan.json

## Pre-Commit Verification

- [ ] All files copied
- [ ] `tree -a -I '.git'` shows correct structure
- [ ] `git status` shows all files
- [ ] `.env` is NOT in git status (should be ignored)
- [ ] `python3 -m py_compile cellwan_exporter.py` succeeds
- [ ] `docker build -t test .` succeeds

## Git Setup

- [ ] `git init` executed
- [ ] `git add .` executed
- [ ] `git commit` executed with message
- [ ] GitHub repository created
- [ ] `git remote add origin` executed
- [ ] `git push -u origin main` executed

## Post-Push Tasks

- [ ] Add repository description on GitHub
- [ ] Add topics: prometheus, monitoring, 5g, lte, docker, grafana
- [ ] Enable Issues
- [ ] Create first release (v1.0.0)
- [ ] Test clone and deploy on fresh system

## Optional Enhancements

- [ ] Add GitHub Actions for CI/CD
- [ ] Add badges to README
- [ ] Create Wiki page
- [ ] Add CONTRIBUTING.md
- [ ] Add SECURITY.md
