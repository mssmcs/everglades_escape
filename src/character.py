# src/character.py

from typing import Set, Optional

# Use TYPE_CHECKING to avoid circular import with GameState
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_state import GameState

class PartyMember:
    """Represents a single member of the player's party."""

    def __init__(self,
                 name: str,
                 max_health: int = 100,
                 max_hunger: int = 100, # Represents fullness, 0 is starving
                 initial_health: Optional[int] = None,
                 initial_hunger: Optional[int] = None):
        # (Attributes remain the same)
        self.name: str = name
        self.max_health: int = max_health
        self.max_hunger: int = max_hunger
        self.health: int = initial_health if initial_health is not None else max_health
        self.hunger: int = initial_hunger if initial_hunger is not None else max_hunger
        self.status_effects: Set[str] = set()


    def is_alive(self) -> bool:
        """Checks if the party member is alive."""
        return self.health > 0

    # Modified to accept game_state for logging
    def take_damage(self, amount: int, game_state: Optional['GameState'] = None):
        """Reduces health by a specified amount, clamping at 0."""
        if amount <= 0 or not self.is_alive(): # Don't log if no actual damage taken
            return

        initial_health = self.health # Store initial health for logging comparison if needed
        self.health = max(0, self.health - amount)

        if game_state:
            game_state.log_message(f"{self.name} takes {amount} damage. Health: {self.health}/{self.max_health}")

        if not self.is_alive() and "perished" not in self.status_effects: # Check if newly perished
             if game_state:
                  game_state.log_message(f"{self.name} has perished.")
             self.add_status_effect("perished", game_state) # Add status *after* logging death


    # Modified to accept game_state for logging
    def heal(self, amount: int, game_state: Optional['GameState'] = None):
        """Increases health by a specified amount, clamping at max_health."""
        if amount <= 0 or not self.is_alive(): # Don't log if no actual healing
            return

        initial_health = self.health
        self.health = min(self.max_health, self.health + amount)

        # Log only if health actually changed
        if self.health > initial_health and game_state:
            game_state.log_message(f"{self.name} heals {amount} HP. Health: {self.health}/{self.max_health}")


    # Modified to accept game_state for logging
    def change_hunger(self, amount: int, game_state: Optional['GameState'] = None):
        """
        Changes hunger level (positive for eating, negative for getting hungrier).
        Clamps between 0 and max_hunger. Applies starving effect if hunger hits 0.
        Logs changes via the provided game_state.
        """
        if not self.is_alive():
            return

        initial_hunger = self.hunger
        initial_is_starving = "starving" in self.status_effects

        self.hunger = max(0, min(self.max_hunger, self.hunger + amount))

        # Log eating only if hunger increased (and potentially above a threshold?)
        if amount > 0 and self.hunger > initial_hunger and game_state:
            # game_state.log_message(f"{self.name} eats. Hunger: {self.hunger}/{self.max_hunger}") # Maybe too noisy
            pass # Logging handled by _consume_daily_food for clarity

        # Add/Remove starving effect based on hunger level
        new_is_starving = "starving" in self.status_effects # Check again in case add_status_effect was called

        if self.hunger <= 0 and not initial_is_starving:
             self.add_status_effect("starving", game_state) # Pass game_state for logging
             if game_state: # Log only if status was newly added
                 game_state.log_message(f"{self.name} is starving!")
        elif self.hunger > 10 and initial_is_starving: # Use initial starving state here
             self.remove_status_effect("starving", game_state) # Pass game_state for logging
             if game_state: # Log only if status was removed
                  game_state.log_message(f"{self.name} is no longer starving.")


    # Modified to accept game_state for logging
    def add_status_effect(self, effect: str, game_state: Optional['GameState'] = None):
        """Adds a status effect if the member is alive."""
        if not self.is_alive() and effect != "perished":
             return
        if effect not in self.status_effects:
            if game_state:
                game_state.log_message(f"{self.name} gains status: {effect}")
            self.status_effects.add(effect)


    # Modified to accept game_state for logging
    def remove_status_effect(self, effect: str, game_state: Optional['GameState'] = None):
        """Removes a status effect."""
        if effect in self.status_effects:
             if game_state:
                 game_state.log_message(f"{self.name} loses status: {effect}")
             self.status_effects.discard(effect)


    def has_status_effect(self, effect: str) -> bool:
        """Checks if the member has a specific status effect."""
        return effect in self.status_effects

    # Modified to accept game_state for logging
    def apply_daily_effects(self, game_state: 'GameState'):
        """Applies effects that occur daily, logging via game_state."""
        if not self.is_alive():
            return

        # Daily hunger decrease - pass game_state for logging within change_hunger
        self.change_hunger(-10, game_state)

        # Effects of statuses - pass game_state for logging within take_damage
        if self.has_status_effect("starving"):
            self.take_damage(12, game_state) # Using 12 damage now
        if self.has_status_effect("sick"):
            self.take_damage(3, game_state)
        if self.has_status_effect("snakebitten"):
            self.take_damage(8, game_state)
        if self.has_status_effect("injured"):
            # Placeholder: Maybe slight damage or impedes healing?
            # self.take_damage(1, game_state)
            pass


    def __str__(self) -> str:
        """String representation of the party member."""
        if not self.is_alive():
            return f"{self.name} (Perished)"

        status_str = f"Status: {', '.join(sorted(list(self.status_effects))) if self.status_effects else 'Healthy'}"
        return f"{self.name} (HP: {self.health}/{self.max_health}, Hunger: {self.hunger}/{self.max_hunger}, {status_str})"