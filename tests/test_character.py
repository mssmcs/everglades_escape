# tests/test_character.py

import pytest
# Change to absolute import from src
from src.character import PartyMember

# --- Fixtures ---
@pytest.fixture
def basic_member() -> PartyMember:
    """Provides a basic PartyMember instance for testing."""
    return PartyMember(name="Test Member", max_health=100, max_hunger=100)

# --- Test Functions ---

def test_partymember_init_defaults():
    """Test PartyMember initialization with default values."""
    member = PartyMember(name="Default Member")
    assert member.name == "Default Member"
    assert member.max_health == 100
    assert member.health == 100
    assert member.max_hunger == 100
    assert member.hunger == 100
    assert member.status_effects == set()
    assert member.is_alive()

def test_partymember_init_custom():
    """Test PartyMember initialization with custom values."""
    member = PartyMember(name="Custom", max_health=120, max_hunger=80, initial_health=90, initial_hunger=70)
    assert member.name == "Custom"
    assert member.max_health == 120
    assert member.health == 90
    assert member.max_hunger == 80
    assert member.hunger == 70
    assert member.is_alive()

def test_take_damage_normal(basic_member):
    """Test taking a normal amount of damage."""
    basic_member.take_damage(30)
    assert basic_member.health == 70
    assert basic_member.is_alive()

def test_take_damage_to_zero(basic_member):
    """Test taking damage exactly to zero health."""
    basic_member.take_damage(100)
    assert basic_member.health == 0
    assert not basic_member.is_alive()
    assert "perished" in basic_member.status_effects

def test_take_damage_below_zero(basic_member):
    """Test taking damage that would go below zero health."""
    basic_member.take_damage(150)
    assert basic_member.health == 0
    assert not basic_member.is_alive()
    assert "perished" in basic_member.status_effects

def test_take_damage_zero_or_negative(basic_member):
    """Test taking zero or negative damage (should have no effect)."""
    initial_health = basic_member.health
    basic_member.take_damage(0)
    assert basic_member.health == initial_health
    basic_member.take_damage(-10)
    assert basic_member.health == initial_health

def test_heal_normal(basic_member):
    """Test normal healing."""
    basic_member.health = 50
    basic_member.heal(20)
    assert basic_member.health == 70

def test_heal_to_max(basic_member):
    """Test healing exactly to maximum health."""
    basic_member.health = 90
    basic_member.heal(10)
    assert basic_member.health == 100

def test_heal_above_max(basic_member):
    """Test healing that would go above maximum health."""
    basic_member.health = 95
    basic_member.heal(20)
    assert basic_member.health == 100

def test_heal_zero_or_negative(basic_member):
    """Test healing zero or negative amount."""
    basic_member.health = 50
    basic_member.heal(0)
    assert basic_member.health == 50
    basic_member.heal(-10)
    assert basic_member.health == 50

def test_heal_when_dead(basic_member):
    """Test that healing has no effect when health is 0."""
    basic_member.health = 0
    basic_member.heal(50)
    assert basic_member.health == 0

def test_change_hunger_increase(basic_member):
    """Test increasing hunger (eating)."""
    basic_member.hunger = 50
    basic_member.change_hunger(30)
    assert basic_member.hunger == 80

def test_change_hunger_decrease(basic_member):
    """Test decreasing hunger."""
    basic_member.hunger = 50
    basic_member.change_hunger(-20)
    assert basic_member.hunger == 30

def test_change_hunger_to_max(basic_member):
    """Test increasing hunger to maximum."""
    basic_member.hunger = 90
    basic_member.change_hunger(20)
    assert basic_member.hunger == 100

def test_change_hunger_above_max(basic_member):
    """Test increasing hunger above maximum."""
    basic_member.hunger = 95
    basic_member.change_hunger(20)
    assert basic_member.hunger == 100

def test_change_hunger_to_zero(basic_member):
    """Test decreasing hunger to zero and applying 'starving' status."""
    basic_member.hunger = 10
    assert "starving" not in basic_member.status_effects
    basic_member.change_hunger(-10)
    assert basic_member.hunger == 0
    assert "starving" in basic_member.status_effects

def test_change_hunger_below_zero(basic_member):
    """Test decreasing hunger below zero and applying 'starving' status."""
    basic_member.hunger = 5
    assert "starving" not in basic_member.status_effects
    basic_member.change_hunger(-15)
    assert basic_member.hunger == 0
    assert "starving" in basic_member.status_effects

def test_change_hunger_removes_starving(basic_member):
    """Test that increasing hunger removes 'starving' status."""
    basic_member.hunger = 0
    basic_member.add_status_effect("starving")
    assert "starving" in basic_member.status_effects
    basic_member.change_hunger(15) # Eat something
    assert basic_member.hunger == 15
    assert "starving" not in basic_member.status_effects

def test_status_effects(basic_member):
    """Test adding, checking, and removing status effects."""
    assert not basic_member.has_status_effect("sick")
    basic_member.add_status_effect("sick")
    assert basic_member.has_status_effect("sick")
    assert "sick" in basic_member.status_effects
    basic_member.add_status_effect("injured")
    assert basic_member.has_status_effect("injured")
    assert basic_member.status_effects == {"sick", "injured"}
    basic_member.remove_status_effect("sick")
    assert not basic_member.has_status_effect("sick")
    assert basic_member.has_status_effect("injured")
    assert basic_member.status_effects == {"injured"}
    basic_member.remove_status_effect("nonexistent") # Should not raise error
    assert basic_member.status_effects == {"injured"}

def test_apply_daily_effects_hunger(basic_member):
    """Test that daily effects decrease hunger."""
    initial_hunger = basic_member.hunger
    basic_member.apply_daily_effects()
    # Assumes default daily hunger decrease is -10 (as in PartyMember code)
    assert basic_member.hunger == initial_hunger - 10

def test_apply_daily_effects_starving_damage(basic_member):
    """Test that daily effects apply damage when starving."""
    basic_member.hunger = 0
    basic_member.add_status_effect("starving")
    initial_health = basic_member.health
    basic_member.apply_daily_effects()
    # Assumes starving damage is 5 (as in PartyMember code)
    assert basic_member.health == initial_health - 5
    assert basic_member.hunger == 0 # Hunger stays at 0

def test_apply_daily_effects_status_damage(basic_member):
    """Test that daily effects apply damage for statuses like 'sick' or 'snakebitten'."""
    basic_member.add_status_effect("sick")
    basic_member.add_status_effect("snakebitten")
    initial_health = basic_member.health
    basic_member.apply_daily_effects()
    # Assumes sick damage=3, snakebitten damage=8 (as in PartyMember code)
    expected_damage = 3 + 8
    assert basic_member.health == initial_health - expected_damage

def test_is_alive(basic_member):
    """Test the is_alive method."""
    assert basic_member.is_alive()
    basic_member.health = 1
    assert basic_member.is_alive()
    basic_member.health = 0
    assert not basic_member.is_alive()
    basic_member.health = -10
    assert not basic_member.is_alive()

def test_str_representation(basic_member):
    """Test the string representation."""
    basic_member.health = 85
    basic_member.hunger = 75
    basic_member.add_status_effect("tired")
    expected_str = "Test Member (HP: 85/100, Hunger: 75/100, Status: tired)"
    assert str(basic_member) == expected_str

    basic_member.health = 0
    basic_member.add_status_effect("perished")
    assert str(basic_member) == "Test Member (Perished)"

