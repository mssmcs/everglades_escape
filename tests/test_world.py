# tests/test_world.py

import pytest
from src.world import Location

@pytest.fixture
def sample_location() -> Location:
    """Provides a sample Location instance for testing."""
    return Location(
        location_id="loc1",
        name="Sample Spot",
        description="A place for testing.",
        connections={"go north": "loc2", "go south": "loc3"},
        hazards=["mud", "bugs"],
        resource_availability={"water": 1.0, "berries": 0.5},
        is_destination=False
    )

@pytest.fixture
def destination_location() -> Location:
    """Provides a sample destination Location instance."""
    return Location(
        location_id="dest",
        name="Safe Haven",
        description="The end goal.",
        is_destination=True
    )

def test_location_init(sample_location):
    """Test Location initialization."""
    assert sample_location.location_id == "loc1"
    assert sample_location.name == "Sample Spot"
    assert sample_location.description == "A place for testing."
    assert sample_location.connections == {"go north": "loc2", "go south": "loc3"}
    assert sample_location.hazards == ["mud", "bugs"]
    assert sample_location.resource_availability == {"water": 1.0, "berries": 0.5}
    assert not sample_location.is_destination

def test_location_init_defaults():
    """Test Location initialization with minimal arguments."""
    loc = Location(location_id="min", name="Minimal", description="...")
    assert loc.location_id == "min"
    assert loc.name == "Minimal"
    assert loc.description == "..."
    assert loc.connections == {}
    assert loc.hazards == []
    assert loc.resource_availability == {}
    assert not loc.is_destination

def test_location_is_destination(sample_location, destination_location):
    """Test the is_destination flag."""
    assert not sample_location.is_destination
    assert destination_location.is_destination

def test_get_possible_travel_actions(sample_location):
    """Test retrieving possible travel actions."""
    actions = sample_location.get_possible_travel_actions()
    assert isinstance(actions, list)
    # Order isn't guaranteed in dict keys before Python 3.7, so use set
    assert set(actions) == {"go north", "go south"}

def test_get_possible_travel_actions_empty():
    """Test retrieving travel actions when there are none."""
    loc = Location(location_id="end", name="End", description="No way out")
    assert loc.get_possible_travel_actions() == []

def test_get_destination_id(sample_location):
    """Test retrieving the destination ID for a valid action."""
    assert sample_location.get_destination_id("go north") == "loc2"
    assert sample_location.get_destination_id("go south") == "loc3"

def test_get_destination_id_invalid(sample_location):
    """Test retrieving the destination ID for an invalid action."""
    assert sample_location.get_destination_id("go west") is None
    assert sample_location.get_destination_id("") is None

def test_location_str(sample_location):
    """Test the string representation of Location."""
    loc_str = str(sample_location)
    assert "Sample Spot (loc1)" in loc_str
    assert "go north, go south" in loc_str # Order might vary pre 3.7
    assert "mud, bugs" in loc_str
    assert "'water': 1.0" in loc_str
    assert "'berries': 0.5" in loc_str
    assert "Is Destination: False" in loc_str

