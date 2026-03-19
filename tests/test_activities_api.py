import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities state between tests."""
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activities():
    # Arrange
    # (None beyond the default state)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    encoded_activity = urllib.parse.quote(activity_name, safe="")
    response = client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    # Act
    encoded_activity = urllib.parse.quote(activity_name, safe="")
    client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")
    response = client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json().get("detail", "")


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "toremove@mergington.edu"

    encoded_activity = urllib.parse.quote(activity_name, safe="")
    client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_signed_up_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    encoded_activity = urllib.parse.quote(activity_name, safe="")
    response = client.delete(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json().get("detail", "")
