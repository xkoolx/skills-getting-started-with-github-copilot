"""
Tests for the Mergington High School Activities API.

Uses the AAA (Arrange-Act-Assert) testing pattern for clarity and structure.
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns HTTP 200 OK."""
        # Arrange
        # (No setup needed - using existing fixtures)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_json(self, client):
        """Test that GET /activities returns JSON with activities data."""
        # Arrange
        # (No setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has all required fields."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert required_fields.issubset(set(activity_data.keys()))
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)

    def test_get_activities_participants_are_strings(self, client):
        """Test that participants in each activity are email addresses (strings)."""
        # Arrange
        # (No setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)


class TestSignUpForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_with_valid_activity_and_email(self, client):
        """Test successful signup with valid activity and email."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity."""
        # Arrange
        activity_name = "Programming Class"
        email = "newemail@mergington.edu"

        # Act - Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - Check final state
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])

        # Assert
        assert signup_response.status_code == 200
        assert final_count == initial_count + 1
        assert email in final_response.json()[activity_name]["participants"]

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signup to nonexistent activity returns 404 Not Found."""
        # Arrange
        activity_name = "NonexistentActivity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_registration_returns_400(self, client):
        """Test that duplicate signup returns 400 Bad Request."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_email_validation(self, client):
        """Test signup with various email formats."""
        # Arrange
        activity_name = "Gym Class"
        valid_emails = [
            "john.doe@mergington.edu",
            "jane123@mergington.edu",
            "student@mergington.edu"
        ]

        # Act & Assert
        for email in valid_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant."""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"

        # Act - Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Act - Check final state
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]

        # Assert
        assert unregister_response.status_code == 200
        assert email not in final_participants
        assert len(final_participants) == len(initial_participants) - 1

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregister from nonexistent activity returns 404."""
        # Arrange
        activity_name = "NonexistentActivity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_unregistered_participant_returns_400(self, client):
        """Test that unregistering unregistered participant returns 400."""
        # Arrange
        activity_name = "Swimming Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]


class TestActivityCapacity:
    """Tests for activity capacity constraints."""

    def test_activity_respects_max_participants(self, client):
        """Test that activities enforce max_participants limit in the data."""
        # Arrange
        # (No setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            participant_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            assert participant_count <= max_participants, \
                f"{activity_name} has more participants than max_participants"

    def test_activity_available_spots_calculation(self, client):
        """Test that available spots are calculated correctly."""
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.get("/activities")
        activity = response.json()[activity_name]
        participant_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        available_spots = max_participants - participant_count

        # Assert
        assert available_spots >= 0
        assert available_spots == (activity["max_participants"] - len(activity["participants"]))


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that / redirects to /static/index.html."""
        # Arrange
        # (No setup needed)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers.get("location", "")
