# Repository Guidelines

## Project Structure & Module Organization
Core exporter logic resides in `cellwan_exporter.py`, handling SSH polling and the Prometheus HTTP endpoint. Support files sit at repo root: `prometheus.yml` for local scrape config, `docker-compose.yml` and `Dockerfile` for container workflows, and the `Makefile` wrappers. Onboarding references (`SETUP_CHECKLIST.md`, `COMPLETE_SETUP_GUIDE.md`) live adjacent. Grafana dashboards and datasource manifests are grouped under `grafana/`; keep future assets in that tree.

## Build, Test, and Development Commands
- `make install` – install dependencies from `requirements.txt`.
- `make dev-run` – run the exporter with Python for iterative debugging.
- `python cellwan_exporter.py --host ...` – override connection options when testing routers.
- `docker-compose up -d` – build and launch the exporter plus Prometheus locally.
- `make test` – curl the metrics endpoint at `http://localhost:9101/metrics`.
- `make dev-test` – run `pytest` for the `tests/` suite (create the folder as needed).

## Coding Style & Naming Conventions
Target Python 3.10+, follow PEP 8, and keep indentation at four spaces. Use `snake_case` for functions and variables, `PascalCase` for classes, and uppercase module constants such as `EXPORTER_PORT`. Logger strings must omit credentials and IMEI data. YAML stays two-space indented; retain tabs in the `Makefile`.

## Testing Guidelines
Pytest is the default runner. Mirror source filenames (`test_cellwan_exporter.py`) and name test functions descriptively. Prefer fixtures and fakes for SSH responses so tests pass without router access. Cover metric parsing, error handling, and any new command-line flags before requesting review.

## Commit & Pull Request Guidelines
Commits should use short, imperative subjects (`Add NR5G SINR metric`) and scope to one logical change. Document config updates, new environment keys, or Grafana assets in the body. Pull requests must include a concise summary, verification steps (e.g., `make dev-test`, `docker-compose up`), linked issues, and screenshots when dashboards change.

## Configuration & Security Notes
Keep sensitive values in `.env`, never in Git. Update `.env.example` whenever a new variable is required. Sanitize exported metrics or logs before sharing externally, and double-check scrape intervals to avoid overwhelming constrained WAN links.
