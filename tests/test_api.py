import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Deep copy original activities and restore before each test
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check: known activity present
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure email is not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in resp.json()["message"] or "Signed up" in resp.json()["message"]

    # Verify participant added
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200

    # Verify participant removed
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]
