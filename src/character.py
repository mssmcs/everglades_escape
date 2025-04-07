# src/character.py

from typing import Set, Optional

class PartyMember:
    """Represents a single member of the player's party."""

    def __init__(self,
                 name: str,
                 max_health: int = 100,
                 max_hunger: int = 100, # Represents fullness, 0 is starving
                 initial_health: Optional[int] = None,
                 initial_hunger: Optional[int] = None):
        """
        Initializes a party member.

        Args:
            name: The name of the party member.
            max_health: The maximum health points.
            max_hunger: The maximum hunger level (fullness).
            initial_health: Starting health (defaults to max_health).
            initial_hunger: Starting hunger (defaults to max_hunger).
        """
        self.name: str = name
        self.max_health: int = max_health
        self.max_hunger: int = max_hunger

        self.health: int = initial_health if initial_health is not None else max_health
        self.hunger: int = initial_hunger if initial_hunger is not None else max_hunger

        # Status effects (e.g., "injured", "sick", "snakebitten", "exhausted", "starving")
        self.status_effects: Set[str] = set()

    def is_alive(self) -> bool:
        """Checks if the party member is alive."""
        return self.health > 0

    def take_damage(self, amount: int):
        """Reduces health by a specified amount, clamping at 0."""
        if amount <= 0:
            return
        self.health = max(0, self.health - amount)
        print(f"{self.name} takes {amount} damage. Health: {self.health}/{self.max_health}") # Temporary feedback
        if not self.is_alive():
            print(f"{self.name} has perished.")
            self.add_status_effect("perished") # Mark as perished

    def heal(self, amount: int):
        """Increases health by a specified amount, clamping at max_health."""
        if amount <= 0 or not self.is_alive():
            return
        self.health = min(self.max_health, self.health + amount)
        print(f"{self.name} heals {amount} HP. Health: {self.health}/{self.max_health}") # Temporary feedback


    def change_hunger(self, amount: int):
        """
        Changes hunger level (positive for eating, negative for getting hungrier).
        Clamps between 0 and max_hunger. Applies starving effect if hunger hits 0.
        """
        if not self.is_alive():
            return

        self.hunger = max(0, min(self.max_hunger, self.hunger + amount))

        if amount > 0:
            print(f"{self.name} eats. Hunger: {self.hunger}/{self.max_hunger}") # Temporary feedback
        elif amount < 0:
             # Optional: feedback for getting hungrier
             # print(f"{self.name} gets hungrier. Hunger: {self.hunger}/{self.max_hunger}")
             pass


        # Add/Remove starving effect based on hunger level
        is_starving = "starving" in self.status_effects
        if self.hunger <= 0 and not is_starving:
             self.add_status_effect("starving")
             print(f"{self.name} is starving!")
        elif self.hunger > 10 and is_starving: # Example threshold to remove starving
             self.remove_status_effect("starving")
             print(f"{self.name} is no longer starving.")

    def add_status_effect(self, effect: str):
        """Adds a status effect if the member is alive."""
        if not self.is_alive() and effect != "perished": # Allow adding 'perished' even if health is 0
             return
        if effect not in self.status_effects:
            print(f"{self.name} gains status: {effect}") # Temporary feedback
            self.status_effects.add(effect)
            # Potentially add immediate effects of the status here (e.g., damage for 'snakebitten')

    def remove_status_effect(self, effect: str):
        """Removes a status effect."""
        if effect in self.status_effects:
             print(f"{self.name} loses status: {effect}") # Temporary feedback
             self.status_effects.discard(effect)


    def has_status_effect(self, effect: str) -> bool:
        """Checks if the member has a specific status effect."""
        return effect in self.status_effects

    def apply_daily_effects(self):
        """Applies effects that occur daily (e.g., hunger decrease, starving damage)."""
        if not self.is_alive():
            return

        # Daily hunger decrease
        self.change_hunger(-10) # Example value

        # Effects of statuses
        if self.has_status_effect("starving"):
            self.take_damage(5) # Example damage from starving
        if self.has_status_effect("sick"):
            self.take_damage(3) # Example damage from sickness
        if self.has_status_effect("snakebitten"):
            self.take_damage(8) # Example damage from snakebite
            # Maybe add a chance to recover or worsen

    def __str__(self) -> str:
        """String representation of the party member."""
        if not self.is_alive():
            return f"{self.name} (Perished)"

        status_str = f"Status: {', '.join(sorted(list(self.status_effects))) if self.status_effects else 'Healthy'}"
        return f"{self.name} (HP: {self.health}/{self.max_health}, Hunger: {self.hunger}/{self.max_hunger}, {status_str})"

# Example Usage (optional, for testing this file directly)
if __name__ == '__main__':
    leader = PartyMember(name="Chayton", max_health=110)
    member1 = PartyMember(name="Api", initial_hunger=30)

    print("--- Initial Party ---")
    print(leader)
    print(member1)
    print("-" * 20)

    member1.take_damage(25)
    leader.change_hunger(-20)
    member1.change_hunger(-30) # Should trigger starving
    member1.apply_daily_effects() # Should take starving damage
    leader.apply_daily_effects()
    member1.change_hunger(50) # Eat something
    member1.heal(10)
    member1.add_status_effect("sick")
    member1.apply_daily_effects() # Take sick damage


    print("\n--- After some actions ---")
    print(leader)
    print(member1)
    print("-" * 20)
