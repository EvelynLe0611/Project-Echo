# Jenkins DevSecOps Pipeline (SIT223 Task 7.3HD)

This is a fork of the DataBytes **Project Echo** repository. I built a seven-stage
Jenkins pipeline for its FastAPI backend (`src/production/backend`).

## Pipeline stages

| Stage | Tools | Gate |
|---|---|---|
| 1. Build | Docker | Image fails to build |
| 2. Test | pytest, mongomock, pytest-cov, real MongoDB + Redis | Any test fails |
| 3. Code Quality | SonarCloud | Quality gate fails |
| 4. Security | Bandit, pip-audit, Trivy | Medium/High code issue or fixable Critical CVE |
| 5. Deploy | Docker Compose (staging, port 9100) | Unhealthy, wrong version or smoke tests fail |
| 6. Release | Manual approval, Docker Compose (production, port 9200) | Failed health check triggers automatic rollback |
| 7. Monitoring | Prometheus, Grafana | Production not monitored or an alert is firing |

## Files I added or changed

| File | Purpose |
|---|---|
| `Jenkinsfile` | The full pipeline |
| `ci/test.env` | Dummy settings used only by CI tests |
| `.trivyignore` | Accepted vulnerability, with justification and expiry date |
| `deploy/docker-compose.yml` | Staging and production environments |
| `deploy/monitoring/` | Prometheus config, alert rules, Grafana dashboard, post-release check |
| `src/production/backend/integration_tests/` | Integration and smoke tests |
| `src/production/backend/requirements.txt` | Removed dev tools and unused Flask, upgraded libraries |
| `src/production/backend/API.Dockerfile` | Added OS and packaging-tool security updates |
| `src/production/backend/app/services/projects.py` | Fixed a Pydantic v1/v2 bug that broke project creation |
| `src/production/backend/app/routers/hmi.py`, `weather_data.py`, `app/services/payments.py` | Fixed or justified Bandit findings |

## Secrets

No real secrets are stored in this repository. The pipeline reads them from Jenkins
credentials at runtime: `SONAR_TOKEN`, `STAGING_JWT_SECRET`, `STAGING_MONGO_PASSWORD`,
`PROD_JWT_SECRET`, `PROD_MONGO_PASSWORD` and `GRAFANA_ADMIN_PASSWORD`.