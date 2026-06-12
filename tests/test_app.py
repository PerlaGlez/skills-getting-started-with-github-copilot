"""
Tests for the High School Management System API

Uses pytest with FastAPI TestClient and AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_email():
    """Provide a unique test email for each test."""
    return "testuser@mergington.edu"


class TestGetActivities:
    """Test the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Arrange: No setup needed for GET.
           Act: Make GET request to /activities.
           Assert: Status is 200 and response includes all activities.
        """
        # Arrange
        # (No setup needed for this GET request)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) > 0
        assert "Chess Club" in response.json()
        assert "Programming Class" in response.json()


class TestActivitySignup:
    """Test the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_returns_success(self, client, test_email):
        """Arrange: Prepare a new email that is not already signed up.
           Act: POST to signup endpoint.
           Assert: Status is 200 and success message is returned.
        """
        # Arrange
        activity_name = "Chess Club"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {test_email} for {activity_name}"}
        assert test_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        
        # Cleanup
        activities[activity_name]["participants"].remove(test_email)
    
    def test_signup_duplicate_email_returns_400(self, client):
        """Arrange: Use an email already signed up for the activity.
           Act: POST to signup endpoint with duplicate email.
           Assert: Status is 400 and error message is returned.
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = activities[activity_name]["participants"][0]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json() == {"detail": "Student already signed up for this activity"}
    
    def test_signup_nonexistent_activity_returns_404(self, client, test_email):
        """Arrange: Use a non-existent activity name.
           Act: POST to signup endpoint for non-existent activity.
           Assert: Status is 404 and activity not found error is returned.
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}


class TestActivityUnregister:
    """Test the DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_unregister_existing_participant_returns_success(self, client, test_email):
        """Arrange: Sign up a test user, then unregister them.
           Act: DELETE from the activity endpoint.
           Assert: Status is 200 and participant is removed.
        """
        # Arrange
        activity_name = "Basketball Team"
        # First, add the test participant
        activities[activity_name]["participants"].append(test_email)
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Unregistered {test_email} from {activity_name}"}
        assert test_email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_nonexistent_participant_returns_404(self, client, test_email):
        """Arrange: Prepare an email not in the activity.
           Act: DELETE with an email not in participants.
           Assert: Status is 404 and participant not found error is returned.
        """
        # Arrange
        activity_name = "Art Club"
        # Ensure test email is not in the activity
        if test_email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(test_email)
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Participant not found"}
    
    def test_unregister_from_nonexistent_activity_returns_404(self, client, test_email):
        """Arrange: Use a non-existent activity name.
           Act: DELETE from non-existent activity.
           Assert: Status is 404 and activity not found error is returned.
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}
