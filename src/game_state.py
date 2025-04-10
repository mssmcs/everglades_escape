# src/game_state.py

from typing import List, Dict, Any, Optional, Tuple

# Relative imports assuming character.py, world.py, events.py are in the same directory (src)
# Need to handle potential circular import if Character needs GameState for logging
# One way is using TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .character import PartyMember
    from .world import Location
    from .events import GameEvent

# Use forward references (strings) in type hints if needed to avoid runtime circular imports
# from .character import PartyMember # Keep this if TYPE_CHECKING isn't sufficient alone
from .world import Location
from .events import GameEvent, EffectFunction

# --- Constants related to consumption ---
FOOD_CONSUMED_PER_DAY = 1
HUNGER_RESTORED_PER_FOOD = 10

class GameState:
    """
    Represents the central state container for the Everglades Escape game.
    Handles game progression, state changes, and logging via message_log.
    """
    def __init__(self,
                 initial_time_limit: int = 30,
                 initial_food: int = 20,
                 initial_canoe_health: int = 100):
        # (Initialization attributes remain the same)
        self.current_day: int = 1
        self.time_remaining: int = initial_time_limit
        self.party_members: List['PartyMember'] = [] # Use forward reference or TYPE_CHECKING
        self.resources: Dict[str, Any] = {
            'food': initial_food,
            'canoe_health': initial_canoe_health,
            'wood': 0,
            'herbs': 0,
            'repair_materials': 0,
        }
        self.current_location: Optional[Location] = None
        self.locations: Dict[str, Location] = {}
        self.events: Dict[str, GameEvent] = {}
        self.active_events: List[GameEvent] = []
        self.game_over: bool = False
        self.win_condition_met: bool = False
        self.loss_reason: Optional[str] = None
        self.message_log: List[str] = []

    def setup_game(self, party: List['PartyMember'], locations: Dict[str, Location], events: Dict[str, GameEvent], start_location_id: str):
        """Sets up the initial state with party, locations, events, and start location."""
        self.party_members = party
        self.locations = locations
        self.events = events
        start_loc = self.locations.get(start_location_id)
        if start_loc:
            self.current_location = start_loc
            self.log_message(f"Game started. Party arrives at {start_loc.name}.")
        else:
            msg = f"Error: Start location ID '{start_location_id}' not found in loaded locations."
            self.log_message(msg) # Log the error
            print(f"FATAL SETUP ERROR: {msg}") # Still print fatal errors? Or handle differently?
            self.game_over = True
            self.loss_reason = "Game setup error: Invalid start location."

    def log_message(self, message: str):
        """Adds a message to the game log queue for later display."""
        # --- REMOVED PRINT STATEMENT ---
        # print(f"LOG: {message}")
        # -----------------------------
        self.message_log.append(message)

    def get_and_clear_messages(self) -> List[str]:
        """Returns the current message log and clears it."""
        messages = self.message_log[:]
        self.message_log = []
        return messages

    def _consume_daily_food(self):
        """Handles automatic daily food consumption (prioritizes hungriest)."""
        living_members = [m for m in self.party_members if m.is_alive()]
        if not living_members:
            return

        living_members.sort(key=lambda member: member.hunger)
        members_fed_count = 0
        members_went_hungry_count = 0
        food_available = self.resources.get('food', 0)

        # Log attempt only once before loop
        # self.log_message(f"Attempting daily food consumption. Available: {food_available} food.")

        for member in living_members:
            if food_available >= FOOD_CONSUMED_PER_DAY:
                food_available -= FOOD_CONSUMED_PER_DAY
                self.resources['food'] -= FOOD_CONSUMED_PER_DAY
                members_fed_count += 1
                # Pass self (game_state) to change_hunger for logging
                member.change_hunger(HUNGER_RESTORED_PER_FOOD, self)
            else:
                members_went_hungry_count += 1

        if members_fed_count > 0:
             self.log_message(f"Consumed {members_fed_count * FOOD_CONSUMED_PER_DAY} food for {members_fed_count} members.")
        if members_went_hungry_count > 0:
             self.log_message(f"{members_went_hungry_count} members could not eat due to lack of food.")
        elif members_fed_count == len(living_members):
             # Maybe only log shortages? Logging "all fed" might be noisy.
             # self.log_message("All members were fed.")
             pass
        # No need to log if no living members, handled by early return


    def apply_daily_party_effects(self):
        """Applies daily effects (like hunger decrease, status damage) to all living party members."""
        # self.log_message(f"--- Applying Daily Effects (Day {self.current_day}) ---") # Maybe too verbose?
        if not self.party_members:
            return

        for member in self.party_members:
            if member.is_alive():
                # Pass self (game_state) to apply_daily_effects for logging purposes
                member.apply_daily_effects(self)

        # self.log_message("-------------------------------------") # Verbose


    def check_game_over_conditions(self):
        """Checks for win or loss conditions and updates game state if met."""
        if self.game_over:
            return

        if self.current_location and self.current_location.is_destination:
            self.set_game_over(win=True, reason=f"Congratulations! The party reached {self.current_location.name} safely.")
            return

        if self.time_remaining <= 0:
            # Add log message here before setting game over? set_game_over already logs.
            self.set_game_over(win=False, reason="The impending disaster arrived... you ran out of time.")
            return

        if not any(member.is_alive() for member in self.party_members):
            self.set_game_over(win=False, reason="The entire party has perished in the Everglades.")
            return

        # Canoe check - still just logs a warning
        if self.resources.get('canoe_health', 0) <= 0:
             # Check if already warned to avoid spamming log
             # This simple check isn't robust enough for stateful warnings
             # if "canoe destroyed" not in " ".join(self.message_log[-5:]): # Hacky check
             #     self.log_message("Warning: The canoe is destroyed!")
             pass # Keep the warning logic minimal for now

    def advance_day(self):
        """Advances the game by one day, handles food consumption, applies effects, and checks game over."""
        if self.game_over:
            # self.log_message("Cannot advance day: Game is already over.") # Maybe too noisy
            return

        self.current_day += 1
        self.time_remaining -= 1
        # self.log_message(f"\n=== Advancing to Day {self.current_day} | Time Remaining: {self.time_remaining} days ===") # View concern?

        self._consume_daily_food()
        self.apply_daily_party_effects()
        # TODO: Daily event checks
        self.check_game_over_conditions() # Check after effects


    def set_game_over(self, win: bool, reason: str):
        """Sets the game over status and logs the reason."""
        if not self.game_over:
            self.game_over = True
            self.win_condition_met = win
            self.loss_reason = reason
            self.log_message(f"--- GAME OVER ---")
            self.log_message(reason) # Log the reason to the message queue

    # (get_party_status_summary, get_resource_summary, __str__ remain the same)
    def get_party_status_summary(self) -> str:
        """Returns a multi-line string summarizing the status of each party member."""
        if not self.party_members:
            return "Party: None"
        summary = ["Party Status:"]
        sorted_party = self.party_members
        for member in sorted_party:
            summary.append(f"  - {member}") # Uses PartyMember.__str__
        return "\n".join(summary)

    def get_resource_summary(self) -> str:
        """Returns a string summarizing key resources."""
        relevant_resources = ['food', 'canoe_health', 'wood', 'herbs', 'repair_materials']
        summary = [f"{name.replace('_', ' ').capitalize()}: {self.resources.get(name, 0)}"
                   for name in relevant_resources if name in self.resources]
        return "Resources: " + ", ".join(summary)

    def __str__(self) -> str:
        """Provides a comprehensive string representation of the current game state."""
        location_name = self.current_location.name if self.current_location else "Unknown"
        status = (
            f"--- Game State ---\n"
            f"Day: {self.current_day}, Time Left: {self.time_remaining} days\n"
            f"Location: {location_name}\n"
            f"{self.get_resource_summary()}\n"
            f"{self.get_party_status_summary()}\n"
            f"Game Over: {self.game_over} " + (f"(Win: {self.win_condition_met})" if self.game_over else "")
        )
        if self.game_over and self.loss_reason:
             status += f"\nReason: {self.loss_reason}"
        return status + "\n------------------"