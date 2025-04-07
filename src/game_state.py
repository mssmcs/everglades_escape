# src/game_state.py

from typing import List, Dict, Any, Optional, Tuple

# Relative imports assuming character.py, world.py, events.py are in the same directory (src)
from .character import PartyMember
from .world import Location
from .events import GameEvent, EffectFunction # Import GameEvent and potentially EffectFunction if needed

class GameState:
    """
    Represents the central state container for the Everglades Escape game.

    Holds all current, dynamic game information, manages game progression (days),
    and checks for win/loss conditions. It interacts with PartyMember, Location,
    and GameEvent objects.
    """
    def __init__(self,
                 initial_time_limit: int = 30, # Example: 30 days
                 initial_food: int = 20,
                 initial_canoe_health: int = 100):
        """
        Initializes the game state with default or starting values.
        Actual party and starting location should be set by a setup function.

        Args:
            initial_time_limit: The total time available in days.
            initial_food: Starting amount of food resources.
            initial_canoe_health: Starting health/condition of the canoe.
        """
        self.current_day: int = 1
        self.time_remaining: int = initial_time_limit

        # Party members - initialized as empty, to be populated during setup
        self.party_members: List[PartyMember] = []

        # Resources (can be expanded)
        self.resources: Dict[str, Any] = {
            'food': initial_food,
            'canoe_health': initial_canoe_health,
            'wood': 0,
            'herbs': 0,
            'repair_materials': 0,
            # Add other resources like tools, water, etc.
        }

        # Location and Events - initialized as None/empty
        self.current_location: Optional[Location] = None # Set during game setup
        self.locations: Dict[str, Location] = {} # Dictionary to hold all loaded locations {location_id: Location}
        self.events: Dict[str, GameEvent] = {} # Dictionary to hold all defined events {event_id: GameEvent}
        self.active_events: List[GameEvent] = [] # List of event objects currently affecting the state

        # Win/Loss Status
        self.game_over: bool = False
        self.win_condition_met: bool = False
        self.loss_reason: Optional[str] = None # e.g., "Ran out of time", "Party perished"

        # Message log for feedback to the UI layer
        self.message_log: List[str] = []

    def setup_game(self, party: List[PartyMember], locations: Dict[str, Location], events: Dict[str, GameEvent], start_location_id: str):
        """Sets up the initial state with party, locations, events, and start location."""
        self.party_members = party
        self.locations = locations
        self.events = events
        start_loc = self.locations.get(start_location_id)
        if start_loc:
            self.current_location = start_loc
            self.log_message(f"Game started. Party arrives at {start_loc.name}.")
        else:
            # Handle error: start location ID not found
            self.log_message(f"Error: Start location ID '{start_location_id}' not found in loaded locations.")
            # Potentially raise an exception or set game to error state
            self.game_over = True
            self.loss_reason = "Game setup error: Invalid start location."

    def log_message(self, message: str):
        """Adds a message to the game log."""
        print(f"LOG: {message}") # Temporary console feedback
        self.message_log.append(message)

    def get_and_clear_messages(self) -> List[str]:
        """Returns the current message log and clears it."""
        messages = self.message_log[:] # Create a copy
        self.message_log = []
        return messages

    def apply_daily_party_effects(self):
        """Applies daily effects to all living party members."""
        self.log_message(f"--- Daily Effects (Start of Day {self.current_day}) ---")
        if not self.party_members:
            return

        for member in self.party_members:
            if member.is_alive():
                member.apply_daily_effects() # Call the member's daily update method
                # Log significant changes reported by the method (e.g., starving damage)
                # This might require apply_daily_effects to return messages or check status after call
        self.log_message("--------------------------------")


    def check_game_over_conditions(self):
        """Checks for win or loss conditions and updates game state if met."""
        if self.game_over: # Don't check if already over
            return

        # 1. Win Condition: Reached destination
        if self.current_location and self.current_location.is_destination:
            self.set_game_over(win=True, reason=f"Congratulations! The party reached {self.current_location.name} safely.")
            return

        # 2. Loss Condition: Ran out of time
        if self.time_remaining < 0:
            self.set_game_over(win=False, reason="The impending disaster arrived... you ran out of time.")
            return

        # 3. Loss Condition: Entire party perished
        if not any(member.is_alive() for member in self.party_members):
            self.set_game_over(win=False, reason="The entire party has perished in the Everglades.")
            return

        # 4. Loss Condition: Canoe destroyed (optional, could be made recoverable)
        if self.resources.get('canoe_health', 0) <= 0:
             # Decide if this is an instant loss or just a major setback
             # self.set_game_over(win=False, reason="The canoe, your lifeline, has been destroyed.")
             self.log_message("Warning: The canoe has been destroyed!")
             # Maybe add a status effect or make travel impossible without fixing it

    def advance_day(self):
        """Advances the game by one day, applies effects, and checks game over."""
        if self.game_over:
            self.log_message("Cannot advance day: Game is already over.")
            return

        self.current_day += 1
        self.time_remaining -= 1
        self.log_message(f"\n=== Day {self.current_day} | Time Remaining: {self.time_remaining} days ===")

        # Apply daily effects (hunger, status effects)
        self.apply_daily_party_effects()

        # TODO: Add logic for daily event checks/triggers here
        # self.trigger_random_event() or similar

        # Check for game over conditions after applying effects and decrementing time
        self.check_game_over_conditions()


    def set_game_over(self, win: bool, reason: str):
        """Sets the game over status and logs the reason."""
        if not self.game_over: # Prevent setting multiple times
            self.game_over = True
            self.win_condition_met = win
            self.loss_reason = reason
            self.log_message(f"--- GAME OVER ---")
            self.log_message(reason)

    def get_party_status_summary(self) -> str:
        """Returns a multi-line string summarizing the status of each party member."""
        if not self.party_members:
            return "Party: None"
        summary = ["Party Status:"]
        for member in self.party_members:
            summary.append(f"  - {member}") # Uses PartyMember.__str__
        return "\n".join(summary)

    def get_resource_summary(self) -> str:
        """Returns a string summarizing key resources."""
        summary = [f"{name.replace('_', ' ').capitalize()}: {value}" for name, value in self.resources.items()]
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
            # f"Active Events: {', '.join(map(str, self.active_events)) if self.active_events else 'None'}\n"
            f"Game Over: {self.game_over} " + (f"(Win: {self.win_condition_met})" if self.game_over else "")
        )
        if self.game_over and self.loss_reason:
             status += f"\nReason: {self.loss_reason}"

        # Include recent messages
        # if self.message_log:
        #    status += "\n--- Recent Log ---\n" + "\n".join(self.message_log[-5:]) # Show last 5 messages

        return status + "\n------------------"


# Example Usage (requires PartyMember, Location, GameEvent classes to be defined and importable)
if __name__ == '__main__':
    # This example assumes you have defined/loaded Locations and Events elsewhere
    # and can import the necessary classes.

    # 1. Import necessary classes (if running this file directly, adjust paths or use dummy classes)
    try:
        from character import PartyMember
        from world import Location
        from events import GameEvent, sudden_storm_effect, found_berries_effect, snake_bite_effect
    except ImportError:
        print("Could not import classes. Define dummy classes for testing.")
        # Define minimal dummy classes if imports fail when running directly
        class PartyMember:
            def __init__(self, name, **kwargs): self.name=name; self.health=100; self.hunger=100; self.status_effects=set()
            def is_alive(self): return self.health > 0
            def apply_daily_effects(self): self.hunger-=10; print(f"{self.name} got hungrier.")
            def __str__(self): return f"{self.name} (HP:{self.health}, Hunger:{self.hunger})"
        class Location:
            def __init__(self, location_id, name, description, connections=None, is_destination=False, **kwargs):
                self.location_id=location_id; self.name=name; self.description=description
                self.connections=connections or {}; self.is_destination=is_destination
            def __str__(self): return self.name
        class GameEvent:
            def __init__(self, event_id, name, description, event_type, apply_effect):
                 self.event_id=event_id; self.name=name; self.description=description
                 self.event_type=event_type; self.apply_effect=apply_effect
            def trigger(self, gs): print(f"Event: {self.name}"); msg = self.apply_effect(gs); print(f"Outcome: {msg}"); gs.active_events.append(self)
            def __str__(self): return self.name
        def dummy_effect(gs): return "Something happened."
        sudden_storm_effect = dummy_effect
        found_berries_effect = dummy_effect
        snake_bite_effect = dummy_effect


    # 2. Create sample data
    # Locations
    locs = {
        "start": Location("start", "Shaded Hammock", "Starting point.", {"paddle east": "slough"}),
        "slough": Location("slough", "Murky Slough", "Slow water.", {"paddle west": "start", "paddle north": "destination"}),
        "destination": Location("destination", "Coastal Mound", "The goal!", {}, is_destination=True)
    }
    # Events
    events = {
        "storm": GameEvent("storm", "Storm", "Clouds gather.", "Weather", sudden_storm_effect),
        "berries": GameEvent("berries", "Berries", "Found food.", "Resource", found_berries_effect),
        "snake": GameEvent("snake", "Snake", "Danger!", "Wildlife", snake_bite_effect)
    }
    # Party
    party = [PartyMember("Leader"), PartyMember("Scout")]

    # 3. Initialize GameState
    game = GameState(initial_time_limit=5) # Short time limit for testing

    # 4. Setup Game
    game.setup_game(party, locs, events, "start")
    print("--- Initial Game State ---")
    print(game)
    initial_messages = game.get_and_clear_messages()
    print("\nInitial Log:\n" + "\n".join(initial_messages))

    # 5. Simulate a few turns
    for i in range(3):
        if game.game_over: break
        game.advance_day()
        print(f"\n--- After Day {game.current_day-1} Actions ---")
        # Simulate triggering an event (replace with actual event logic)
        if random.random() < 0.5 and game.events: # 50% chance
            event_to_trigger = random.choice(list(game.events.values()))
            event_to_trigger.trigger(game)

        print(game)
        day_messages = game.get_and_clear_messages()
        print("\nLog for Day:\n" + "\n".join(day_messages))


    # 6. Simulate reaching destination (if not already game over)
    if not game.game_over:
        print("\n--- Moving to Destination ---")
        destination_loc = game.locations.get("destination")
        if destination_loc:
             game.current_location = destination_loc
             game.log_message(f"Party arrived at {destination_loc.name}.")
             game.check_game_over_conditions() # Check win condition
             print(game)
             final_messages = game.get_and_clear_messages()
             print("\nFinal Log:\n" + "\n".join(final_messages))
        else:
             print("Error: Could not find destination location.")

