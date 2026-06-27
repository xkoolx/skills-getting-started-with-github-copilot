"""
Pytest configuration and fixtures for the Mergington High School Activities API tests.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Provide a TestClient for making HTTP requests to the app."""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provide sample activity data for testing."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        }
    }
