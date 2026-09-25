"""
Post-release monitoring check, run by the Jenkins Monitoring stage.

1. Waits until Prometheus is successfully collecting metrics from production.
2. Lists every monitored target and its health.
3. Checks Grafana is up.
4. Confirms the alert rules are loaded.
5. Fails if any alert is firing for production.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

PROMETHEUS = os.environ.get("PROMETHEUS_URL", "http://prometheus:9090")
GRAFANA = os.environ.get("GRAFANA_URL", "http://grafana:3000")


def get(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode())


def query(expr):
    url = f"{PROMETHEUS}/api/v1/query?" + urllib.parse.urlencode({"query": expr})
    return get(url)["data"]["result"]


def wait_for(description, check, attempts=24, delay=5):
    for _ in range(attempts):
        try:
            if check():
                return True
        except Exception:
            pass
        time.sleep(delay)
    print(f"FAILED: {description}")
    sys.exit(1)


# 1. Prometheus can scrape production
wait_for(
    "Prometheus cannot collect metrics from the production API",
    lambda: any(r["value"][1] == "1" for r in query('up{job="echo-api",environment="production"}')),
)
print("Prometheus is collecting metrics from production: UP")

# 2. All monitored targets
print("Monitored targets:")
for target in get(f"{PROMETHEUS}/api/v1/targets")["data"]["activeTargets"]:
    name = target["labels"].get("environment", target["labels"]["job"])
    print(f"  {name:<12} {target['scrapeUrl']:<40} {target['health']}")

# 3. Grafana
wait_for("Grafana is not responding", lambda: get(f"{GRAFANA}/api/health").get("database") == "ok")
print("Grafana: UP (dashboard at http://localhost:3000)")

# 4. Alert rules loaded
groups = get(f"{PROMETHEUS}/api/v1/rules")["data"]["groups"]
rules = [rule["name"] for group in groups for rule in group["rules"]]
if not rules:
    print("FAILED: no alert rules are loaded")
    sys.exit(1)
print(f"Alert rules loaded ({len(rules)}): {', '.join(rules)}")

# 5. No production alerts firing
firing = [
    alert for alert in get(f"{PROMETHEUS}/api/v1/alerts")["data"]["alerts"]
    if alert["state"] == "firing" and alert["labels"].get("environment") == "production"
]
if firing:
    print("FAILED: alerts are firing for production:")
    for alert in firing:
        print(f"  {alert['labels']['alertname']}: {alert['annotations'].get('summary', '')}")
    sys.exit(1)

print("PASSED: production is monitored and no alerts are firing")