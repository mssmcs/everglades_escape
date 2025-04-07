# tests/test_events.py

import pytest
import random
from unittest.mock import Mock, MagicMock # Using unittest.mock for mocking GameState/PartyMember

# Import the classes and functions to be tested
from src.events import GameEvent, sudden_storm_effect, found_berries_effect, snake_bite_effect
# We need dummy/mock versions of GameState and PartyMember for isolated testing
# Or we can import the real ones if dependencies are simple enough
# from src.game_state import GameState
# from src.character import PartyMember

# --- Mock/Dummy Classes ---
# Create simple stand-ins for GameState and PartyMember for isolated testing of effects
class MockPartyMember:
    def __init__(self, name="Mock Member", health=100):
        self.name = name
        self.health = health
        self.status_effects = set()
        self._is_alive = health > 0

    def is_alive(self):
        return self._is_alive

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self._is_alive = False

    def add_status_effect(self, effect):
        self.status_effects.add(effect)

    def __str__(self):
        return self.name

class MockGameState:
    def __init__(self):
        self.resources = {'canoe_health': 100, 'food': 10}
        self.party_members = [MockPartyMember("Alice"), MockPartyMember("Bob")]
        self.active_events = []
        # Add log_message if needed by effects, or mock it
        self.message_log = []
    def log_message(self, msg):
        self.message_log.append(msg)


# --- Fixtures ---
@pytest.fixture
def mock_game_state() -> MockGameState:
    """Provides a mock GameState instance."""
    return MockGameState()

@pytest.fixture
def storm_event() -> GameEvent:
    """Provides a storm GameEvent instance."""
    return GameEvent("storm1", "Storm", "...", "Weather", sudden_storm_effect)

@pytest.fixture
def berry_event() -> GameEvent:
    """Provides a berry GameEvent instance."""
    return GameEvent("berry1", "Berries", "...", "Resource", found_berries_effect)

@pytest.fixture
def snake_event() -> GameEvent:
    """Provides a snake GameEvent instance."""
    return GameEvent("snake1", "Snake", "...", "Wildlife", snake_bite_effect)

# --- Test Functions ---

def test_game_event_init(storm_event):
    """Test GameEvent initialization."""
    assert storm_event.event_id == "storm1"
    assert storm_event.name == "Storm"
    assert storm_event.description == "..."
    assert storm_event.event_type == "Weather"
    assert storm_event.apply_effect == sudden_storm_effect

def test_game_event_trigger(storm_event, mock_game_state):
    """Test that triggering an event calls its effect function and adds to active_events."""
    # Mock the effect function to check if it's called
    mock_effect = MagicMock(return_value="Mock effect happened")
    event = GameEvent("test_event", "Test", "...", "Test", mock_effect)

    assert event not in mock_game_state.active_events
    result_message = event.trigger(mock_game_state)

    mock_effect.assert_called_once_with(mock_game_state) # Check if effect func was called
    assert result_message == "Mock effect happened"
    assert event in mock_game_state.active_events # Check if event was added to list

# --- Test Effect Functions ---

def test_sudden_storm_effect(mock_game_state):
    """Test the sudden_storm_effect function."""
    initial_canoe_health = mock_game_state.resources['canoe_health']
    initial_member_health = mock_game_state.party_members[0].health
    random.seed(123) # Control randomness for predictability

    message = sudden_storm_effect(mock_game_state)

    assert mock_game_state.resources['canoe_health'] < initial_canoe_health
    # Check if a member was potentially injured (depends on random seed)
    # In this case, with seed 123, random.random() < 0.3 is true, member takes damage
    assert mock_game_state.party_members[0].health < initial_member_health
    assert "injured" in mock_game_state.party_members[0].status_effects
    assert "canoe is battered" in message
    assert "injured" in message

def test_found_berries_effect(mock_game_state):
    """Test the found_berries_effect function (non-poisonous case)."""
    random.seed(123) # Ensure random() > 0.05 (poison chance)
    initial_food = mock_game_state.resources['food']

    message = found_berries_effect(mock_game_state)

    assert mock_game_state.resources['food'] > initial_food
    assert "Gained" in message
    assert "food" in message
    assert "sick" not in message # Check it wasn't the poison case

def test_found_berries_effect_poisonous(mock_game_state):
    """Test the found_berries_effect function (poisonous case)."""
    random.seed(0) # Ensure random() < 0.05 (poison chance)
    initial_food = mock_game_state.resources['food']
    member_affected = mock_game_state.party_members[0] # Will affect the first member

    message = found_berries_effect(mock_game_state)

    assert mock_game_state.resources['food'] > initial_food
    assert "Gained" in message
    assert "food" in message
    assert "sick" in message # Check it WAS the poison case
    assert "sick" in member_affected.status_effects

def test_snake_bite_effect(mock_game_state):
    """Test the snake_bite_effect function."""
    random.seed(123) # Control which member is chosen and damage
    member_to_be_bitten = mock_game_state.party_members[0] # random.choice picks first with seed 123
    initial_health = member_to_be_bitten.health

    message = snake_bite_effect(mock_game_state)

    assert member_to_be_bitten.health < initial_health
    assert "snakebitten" in member_to_be_bitten.status_effects
    assert member_to_be_bitten.name in message
    assert "bitten by a venomous snake" in message

def test_snake_bite_effect_no_living_members(mock_game_state):
    """Test snake bite effect when there are no living members."""
    mock_game_state.party_members = [] # Remove members
    message = snake_bite_effect(mock_game_state)
    assert "no one left to bite" in message

    mock_game_state.party_members = [MockPartyMember("Dead", health=0)]
    message = snake_bite_effect(mock_game_state)
    # The current implementation might still choose a dead member but not damage/affect them
    # A better implementation might filter for is_alive() before random.choice
    assert "bitten" not in message # Ensure no bite message if only dead members

