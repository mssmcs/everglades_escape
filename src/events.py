# src/events.py

import random
from typing import Callable, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular import errors
if TYPE_CHECKING:
    from .game_state import GameState
    from .character import PartyMember

# Type alias for the effect function
EffectFunction = Callable[['GameState'], str] # Effect functions return message

class GameEvent:
    """Represents a game event (random or triggered)."""

    def __init__(self,
                 event_id: str,
                 name: str,
                 description: str,
                 event_type: str, # e.g., "Weather", "Wildlife", "Navigation", "Resource"
                 apply_effect: EffectFunction):
        # (Initialization remains the same)
        self.event_id: str = event_id
        self.name: str = name
        self.description: str = description
        self.event_type: str = event_type
        self.apply_effect: EffectFunction = apply_effect

    # Modified to accept game_state for logging
    def trigger(self, game_state: 'GameState') -> str:
        """Triggers the event's effect on the game state and logs results."""
        # --- REMOVED PRINT STATEMENTS ---
        # print(f"\n--- Event Triggered: {self.name} ---")
        # print(self.description)
        # -----------------------------

        # Log the trigger and description
        game_state.log_message(f"--- Event Triggered: {self.name} ---")
        game_state.log_message(self.description)

        # Execute effect - it should modify game_state directly AND return message
        outcome_message = self.apply_effect(game_state)

        # Log the outcome message returned by the effect function
        game_state.log_message(f"Outcome: {outcome_message}")
        # game_state.log_message("-----------------------------------\n") # Maybe too verbose

        # Add event to active list (if needed - current logic doesn't use active_events much)
        # game_state.active_events.append(self) # Re-evaluate if active events needed

        return outcome_message # Still return for potential immediate use by caller

    def __str__(self) -> str:
        """String representation of the event."""
        return f"{self.name} ({self.event_type} - {self.event_id})"


# --- Example Event Effect Functions ---
# These functions MUST accept GameState and return a message string.
# They should now use game_state.log_message for internal details if needed,
# but primary feedback should be via the return string.

# Modified to accept game_state for logging within member methods if needed
def sudden_storm_effect(game_state: 'GameState') -> str:
    """Effect logic for a sudden storm event."""
    canoe_damage = random.randint(5, 25)
    injury_chance = 0.3
    messages = [] # Collect parts of the outcome message

    # Damage canoe (if functional)
    current_canoe_health = game_state.resources.get('canoe_health', 0)
    new_canoe_health = current_canoe_health # Default if already broken
    if current_canoe_health > 0:
        new_canoe_health = max(0, current_canoe_health - canoe_damage)
        game_state.resources['canoe_health'] = new_canoe_health
        messages.append(f"The canoe is battered, taking {canoe_damage} damage (Health: {new_canoe_health}).")
        if new_canoe_health <= 0:
             messages.append("The canoe is destroyed!")
    else:
         messages.append("The storm rages, but the canoe is already broken.")


    # Injure party member?
    living_members = [m for m in game_state.party_members if m.is_alive()]
    if living_members and random.random() < injury_chance:
        member_to_injure: 'PartyMember' = random.choice(living_members)
        injury_damage = random.randint(1, 10)
        # Pass game_state for logging within take_damage and add_status_effect
        member_to_injure.take_damage(injury_damage, game_state)
        member_to_injure.add_status_effect("injured", game_state)
        # The take_damage method now logs the HP loss. We just add context here.
        messages.append(f"{member_to_injure.name} is injured amidst the chaos!")

    return "A sudden thunderstorm hits! " + " ".join(messages)

# Modified to accept game_state for potential logging in status effects
def found_berries_effect(game_state: 'GameState') -> str:
    """Effect logic for finding edible berries."""
    food_gain = random.randint(3, 8)
    game_state.resources['food'] = game_state.resources.get('food', 0) + food_gain
    message = f"You stumble upon a patch of ripe berries! Gained {food_gain} food."

    # Poison chance
    poison_chance = 0.05
    living_members = [m for m in game_state.party_members if m.is_alive()]
    if living_members and random.random() < poison_chance:
         member: 'PartyMember' = random.choice(living_members)
         # Pass game_state for logging within add_status_effect
         member.add_status_effect("sick", game_state)
         # add_status_effect logs the gain. We add context here.
         message += f" Unfortunately, {member.name} feels sick after eating them."

    return message

# Modified to accept game_state for logging
def snake_bite_effect(game_state: 'GameState') -> str:
    """Effect logic for a party member getting bitten by a snake."""
    living_members = [m for m in game_state.party_members if m.is_alive()]
    if not living_members:
        return "A venomous snake lunges, but there's no one left to bite."

    member_bitten: 'PartyMember' = random.choice(living_members)
    bite_damage = random.randint(10, 25) # Assuming snakebite status also does damage over time
    initial_message = f"Rustling in the undergrowth! A venomous snake bites {member_bitten.name}!"

    # Pass game_state for logging within take_damage and add_status_effect
    member_bitten.take_damage(bite_damage, game_state)
    member_bitten.add_status_effect("snakebitten", game_state)

    # take_damage logs the HP loss, add_status_effect logs the status gain.
    return initial_message # Return the event description, details are in log


# (Example usage block removed for brevity)