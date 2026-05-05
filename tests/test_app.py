import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def restore_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_success():
    email = "new_student@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_not_found():
    response = client.post("/activities/Unknown/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_already_signed_up():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_success():
    email = "john@mergington.edu"
    response = client.delete("/activities/Gym Class/participants", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Gym Class"}
    assert email not in activities["Gym Class"]["participants"]


def test_remove_participant_not_found_activity():
    response = client.delete("/activities/Unknown/participants", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_not_signed_up():
    response = client.delete("/activities/Chess Club/participants", params={"email": "not_registered@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"