"""
Integration tests for the Project Echo API.

These tests run against a real, running API container connected to a real
MongoDB container (started by the Jenkins pipeline). They check that the
components work together end to end - unlike the unit tests, which use mocks.
"""
import os
import uuid

import httpx
import pytest

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:9000")


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


def make_project(name):
    return {
        "name": name,
        "description": "Created by Jenkins integration test",
        "location": "Otways",
        "status": "active",
        "sensorIds": [],
        "ecologists": [],
    }


def test_api_is_up(client):
    response = client.get("/")
    assert response.status_code == 200


def test_metrics_endpoint_exposes_prometheus_metrics(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "echo_http_requests_total" in response.text


def test_project_crud_lifecycle(client):
    name = f"ci-{uuid.uuid4().hex[:8]}"

    # Create
    response = client.post("/projects", json=make_project(name))
    assert response.status_code == 200, response.text
    created = response.json()
    project_id = created["id"]
    assert created["name"] == name

    # Read
    response = client.get("/projects")
    assert response.status_code == 200
    assert any(p["id"] == project_id for p in response.json()["items"])

    # Update
    response = client.put(f"/projects/{project_id}", json=make_project(name + "-updated"))
    assert response.status_code == 200, response.text
    assert response.json()["name"] == name + "-updated"

    # Delete
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    # Confirm it is gone
    response = client.get("/projects")
    assert all(p["id"] != project_id for p in response.json()["items"])


def test_create_project_rejects_invalid_body(client):
    response = client.post("/projects", json=["not", "a", "project"])
    assert response.status_code == 422