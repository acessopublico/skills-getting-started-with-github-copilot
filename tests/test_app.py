from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

DEFAULT_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_app_state():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(DEFAULT_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(DEFAULT_ACTIVITIES))


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_student_email():
    activity_name = "Chess Club"
    email = "student@example.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_email():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    response = client.post("/activities/Does Not Exist/signup?email=student@example.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "student@example.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    activity_name = "Chess Club"
    email = "missing@example.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
