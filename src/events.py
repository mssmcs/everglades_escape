# src/events.py

import random
from typing import Callable, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular import errors if GameState imports this module
if TYPE_CHECKING:
    from game_state import GameState # Assuming game_state.py contains GameState
    from character import PartyMember # Assuming character.py contains PartyMember

# Type alias for the effect function
# It takes the GameState and returns a message string describing the outcome.
EffectFunction = Callable[['GameState'], str]

class GameEvent:
    """Represents a game event (random or triggered)."""

    def __init__(self,
                 event_id: str, # Unique identifier
                 name: str,
                 description: str,
                 event_type: str, # e.g., "Weather", "Wildlife", "Navigation", "Resource"
                 apply_effect: EffectFunction):
        """
        Initializes a game event.

        Args:
            event_id: A unique string identifier for this event.
            name: The display name of the event.
            description: Text describing the event occurrence to the player.
            event_type: Category of the event.
            apply_effect: A function that takes the current GameState object
                          as input, modifies it according to the event's logic,
                          and returns a string message describing what happened.
        """
        self.event_id: str = event_id
        self.name: str = name
        self.description: str = description
        self.event_type: str = event_type
        self.apply_effect: EffectFunction = apply_effect

    def trigger(self, game_state: 'GameState') -> str:
        """Triggers the event's effect on the game state."""
        print(f"\n--- Event Triggered: {self.name} ---") # Temporary feedback
        print(self.description)
        outcome_message = self.apply_effect(game_state)
        print(f"Outcome: {outcome_message}")
        print("-----------------------------------\n")
        # Add the event itself to the active_events list in game_state
        # Note: You might want more complex logic for how long events stay active
        game_state.active_events.append(self)
        return outcome_message # Return the message for potential display

    def __str__(self) -> str:
        """String representation of the event."""
        return f"{self.name} ({self.event_type} - {self.event_id})"


# --- Example Event Effect Functions ---
# These functions define the logic that happens when an event is triggered.
# They directly modify the passed GameState object.

def sudden_storm_effect(game_state: 'GameState') -> str:
    """Effect logic for a sudden storm event."""
    canoe_damage = random.randint(5, 25)
    injury_chance = 0.3 # 30% chance someone gets slightly injured
    message = []

    # Damage canoe
    current_canoe_health = game_state.resources.get('canoe_health', 0)
    new_canoe_health = max(0, current_canoe_health - canoe_damage)
    game_state.resources['canoe_health'] = new_canoe_health
    message.append(f"The canoe is battered by wind and waves, taking {canoe_damage} damage (Health: {new_canoe_health}).")
    if new_canoe_health <= 0:
         message.append("The canoe is destroyed!")
         # Potentially trigger game over or a very difficult state

    # Injure party member?
    living_members = [m for m in game_state.party_members if m.is_alive()]
    if living_members and random.random() < injury_chance:
        member_to_injure: 'PartyMember' = random.choice(living_members)
        injury_damage = random.randint(1, 10)
        member_to_injure.take_damage(injury_damage)
        member_to_injure.add_status_effect("injured")
        message.append(f"{member_to_injure.name} is injured ({injury_damage} HP) amidst the chaos!")

    return "A sudden thunderstorm hits! " + " ".join(message)

def found_berries_effect(game_state: 'GameState') -> str:
    """Effect logic for finding edible berries."""
    food_gain = random.randint(3, 8)
    game_state.resources['food'] = game_state.resources.get('food', 0) + food_gain
    # Maybe a small chance they are poisonous?
    poison_chance = 0.05
    if random.random() < poison_chance and game_state.party_members:
         member: 'PartyMember' = random.choice([m for m in game_state.party_members if m.is_alive()])
         if member:
             member.add_status_effect("sick")
             return f"You stumble upon a patch of berries! Gained {food_gain} food, but {member.name} feels sick after eating them."
         else:
             return f"You stumble upon a patch of ripe berries! Gained {food_gain} food."
    else:
        return f"You stumble upon a patch of ripe berries! Gained {food_gain} food."


def snake_bite_effect(game_state: 'GameState') -> str:
    """Effect logic for a party member getting bitten by a snake."""
    living_members = [m for m in game_state.party_members if m.is_alive()]
    if not living_members:
        return "A venomous snake lunges, but there's no one left to bite."

    member_bitten: 'PartyMember' = random.choice(living_members)
    bite_damage = random.randint(10, 25)
    member_bitten.take_damage(bite_damage)
    member_bitten.add_status_effect("snakebitten")
    return f"Rustling in the undergrowth! {member_bitten.name} is bitten by a venomous snake ({bite_damage} HP)!"


# Example Usage (optional, for testing this file directly)
# Note: This requires dummy GameState and PartyMember classes or importing them.
if __name__ == '__main__':

    # --- Create Dummy classes for testing if not importing ---
    class DummyPartyMember:
        def __init__(self, name):
            self.name = name
            self.health = 100
            self.status_effects = set()
        def is_alive(self): return self.health > 0
        def take_damage(self, amount): self.health -= amount; print(f"{self.name} took {amount} damage -> {self.health} HP")
        def add_status_effect(self, effect): self.status_effects.add(effect); print(f"{self.name} got {effect}")
        def __str__(self): return f"{self.name} (HP: {self.health}, Status: {self.status_effects})"

    class DummyGameState:
        def __init__(self):
            self.resources = {'canoe_health': 100, 'food': 10}
            self.party_members = [DummyPartyMember("TestMember1"), DummyPartyMember("TestMember2")]
            self.active_events = []
        def __str__(self):
            party_str = "\n  ".join(map(str, self.party_members))
            return f"Resources: {self.resources}\nParty:\n  {party_str}\nActive Events: {self.active_events}"

    # --- Instantiate Events ---
    storm_event = GameEvent(
        event_id="storm_01", name="Sudden Thunderstorm",
        description="Dark clouds gather rapidly...", event_type="Weather",
        apply_effect=sudden_storm_effect
    )
    berry_event = GameEvent(
        event_id="find_berries_01", name="Berry Patch",
        description="You spot some edible-looking berries...", event_type="Resource",
        apply_effect=found_berries_effect
    )
    snake_event = GameEvent(
        event_id="snake_bite_01", name="Snake Attack!",
        description="Rustling in the undergrowth!", event_type="Wildlife",
        apply_effect=snake_bite_effect
    )

    print("--- Game Events ---")
    print(storm_event)
    print(berry_event)
    print(snake_event)
    print("-" * 20)

    # --- Trigger Events ---
    print("\n--- Triggering Events ---")
    test_state = DummyGameState()
    print("Initial State:")
    print(test_state)

    storm_event.trigger(test_state)
    print("\nState after storm:")
    print(test_state)

    berry_event.trigger(test_state)
    print("\nState after finding berries:")
    print(test_state)

    snake_event.trigger(test_state)
    print("\nState after snake bite:")
    print(test_state)

    print(f"\nFinal Active Events List: {test_state.active_events}")

