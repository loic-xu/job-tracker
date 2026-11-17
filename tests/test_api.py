from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server.main import app, candidature


@pytest.fixture
def client(tmp_path, monkeypatch):
    csv_file = tmp_path / "test_api.csv"
    csv_file.write_text("id,company,title,type,application_date,status,notes,link\n")
    monkeypatch.setenv("CSV_PATH", str(csv_file))

    candidature.csv_path = Path(csv_file)

    return TestClient(app)


def test_get_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_application(client):
    response = client.get("/api/applications")
    assert response.status_code == 200
    assert response.json() == []


def test_post_application_success(client):
    input_data = {
        "company": "Google",
        "title": "Software Engineer",
        "type": "CDI",
        "application_date": "2026-08-12",
        "status": "Applied",
        "notes": "Entretien prévu",
        "link": "https://careers.google.com/jobs/123",
    }
    response = client.post("/api/applications", json=input_data)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["company"] == "Google"
    assert data["status"] == "Applied"


def test_get_stats(client):
    client.post(
        "/api/applications",
        json={
            "company": "Meta",
            "title": "Backend Dev",
            "link": "https://meta.com/careers",
        },
    )

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["by_status"]["To Apply"] == 1


def test_update_application_success(client):
    post_res = client.post(
        "/api/applications",
        json={"company": "Amazon", "title": "Dev Ops", "link": "https://aws.com"},
    )
    app_id = post_res.json()["id"]
    update_res = client.put(f"/api/applications/{app_id}", json={"status": "Interview"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "Interview"
    assert update_res.json()["company"] == "Amazon"


def test_update_application_not_found(client):
    response = client.put("/api/applications/999", json={"status": "Rejected"})
    assert response.status_code == 404


def test_delete_application_success(client):
    post_res = client.post(
        "/api/applications",
        json={"company": "Apple", "title": "iOS Dev", "link": "https://apple.com"},
    )
    app_id = post_res.json()["id"]
    delete_res = client.delete(f"/api/applications/{app_id}")
    assert delete_res.status_code == 200
    assert delete_res.json() == {"ok": True}


def test_delete_application_not_found(client):
    response = client.delete("/api/applications/999")
    assert response.status_code == 404
