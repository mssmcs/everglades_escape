"""
Main entry point and game loop for Everglades Escape.
Handles user interaction, orchestrates actions, and displays state.
"""

import random
import sys

# Assuming src package structure allows these imports
from src.game_state import GameState
from src.character import PartyMember
from src.world import Location
from src.events import GameEvent, sudden_storm_effect, found_berries_effect, snake_bite_effect # Example events

# --- Constants ---
INITIAL_TIME_LIMIT = 30
INITIAL_FOOD = 20
INITIAL_CANOE_HEALTH = 100

# --- Hazard Probabilities & Effects ---
HAZARD_PROBABILITY = {
    "submerged logs": 0.25,
    "alligator": 0.15,
    "snakes": 0.20,
    "difficult terrain": 0.10
}
HAZARD_CANOE_DAMAGE = {
    "submerged logs": (5, 15),
}
HAZARD_PERSON_DAMAGE = {
    "alligator": (15, 30),
    "snakes": (10, 20)
}

# --- Placeholder Data Loading ---
# (load_locations, load_events, create_initial_party remain the same as previous version)
def load_locations() -> dict[str, Location]:
    """Loads or defines the game locations."""
    # Added/updated hazards
    start_hammock = Location(
        location_id="start_hammock",
        name="Shaded Hammock",
        description="A small, relatively dry island of hardwood trees.",
        connections={"paddle east": "murky_slough", "trek south": "shallow_marsh"},
        hazards=["snakes"], # Added snakes
        resource_availability={"wood": 0.5, "herbs": 0.2}
    )
    murky_slough = Location(
        location_id="murky_slough",
        name="Murky Slough",
        description="A slow-moving channel of dark water, thick with vegetation.",
        connections={"paddle west": "start_hammock", "paddle north": "river_fork"},
        hazards=["submerged logs", "alligator"], # Keep both
        resource_availability={"fish": 0.6, "reeds": 0.8}
    )
    shallow_marsh = Location(
        location_id="shallow_marsh",
        name="Shallow Marsh",
        description="Expansive sawgrass marsh, difficult for canoes.",
        connections={"trek north": "start_hammock"},
        hazards=["difficult terrain", "snakes"], # Already had snakes
        resource_availability={"reeds": 0.9, "small_game": 0.1}
    )
    river_fork = Location(
        location_id="river_fork",
        name="River Fork",
        description="Where the slough meets a wider, slow-moving river.",
        connections={"paddle south": "murky_slough", "paddle downstream": "coastal_mound"},
        hazards=["submerged logs", "alligator"], # Added alligator possibility
        resource_availability={"fish": 0.8, "water": 1.0}
    )
    coastal_mound = Location(
        location_id="coastal_mound",
        name="Coastal Mound (Safe Haven)",
        description="A large shell mound near the coast, offering safety.",
        connections={"paddle upstream": "river_fork"}, # Can maybe only go back?
        is_destination=True
    )
    return {
        loc.location_id: loc for loc in [
            start_hammock, murky_slough, shallow_marsh, river_fork, coastal_mound
        ]
    }

def load_events() -> dict[str, GameEvent]:
    """Loads or defines the possible game events."""
    # Using example events from events.py for now
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
    snake_event = GameEvent( # Keep the specific event too if desired, or rely on hazard
        event_id="snake_bite_01", name="Snake Attack!",
        description="Rustling in the undergrowth!", event_type="Wildlife",
        apply_effect=snake_bite_effect
    )
    return {
        event.event_id: event for event in [storm_event, berry_event, snake_event]
    }

def create_initial_party() -> list[PartyMember]:
    """Creates the starting party members."""
    # Example party
    leader = PartyMember(name="Chayton", max_health=110)
    scout = PartyMember(name="Api", initial_hunger=80)
    gatherer = PartyMember(name="Nokomis", max_health=90, initial_hunger=90)
    return [leader, scout, gatherer]

# --- View Functions (Text-Based) ---

def display_game_state(game_state: GameState):
    """Displays the current game status to the player."""
    print("\n" + "=" * 40)
    # Print core status using GameState's string representation helper (or direct access)
    location_name = game_state.current_location.name if game_state.current_location else "Unknown"
    print(f"Day: {game_state.current_day} | Time Remaining: {game_state.time_remaining} days | Location: {location_name}")
    print(game_state.get_resource_summary())
    print(game_state.get_party_status_summary())

    # Print and clear the message log from GameState
    messages = game_state.get_and_clear_messages()
    if messages:
        print("\n--- Log ---")
        for msg in messages:
            print(f"- {msg}") # Display messages logged by Model/Controller
        print("-----------")

    print("=" * 40 + "\n")


def display_available_actions(game_state: GameState) -> dict[str, tuple[str, str | None]]:
    """Displays available actions and returns a mapping for input handling."""
    print("Available Actions:")
    actions = {}
    action_index = 1

    canoe_functional = game_state.resources.get('canoe_health', 0) > 0

    # Travel Actions
    if game_state.current_location:
        travel_options = game_state.current_location.get_possible_travel_actions()
        if travel_options:
            print("  Travel:")
            for travel_action in travel_options:
                requires_canoe = "paddle" in travel_action.lower()
                if requires_canoe and not canoe_functional:
                    actions[str(action_index)] = ("disabled_travel", travel_action)
                    print(f"    {action_index}. {travel_action.capitalize()} (Canoe Damaged!)")
                else:
                    actions[str(action_index)] = ("travel", travel_action)
                    print(f"    {action_index}. {travel_action.capitalize()}")
                action_index += 1

    # Other Actions
    print("  Other:")
    actions[str(action_index)] = ("forage", None)
    print(f"    {action_index}. Forage for food/resources")
    action_index += 1
    actions[str(action_index)] = ("rest", None)
    print(f"    {action_index}. Rest")
    action_index += 1
    if 'canoe_health' in game_state.resources and game_state.resources['canoe_health'] < INITIAL_CANOE_HEALTH:
         actions[str(action_index)] = ("repair", None)
         print(f"    {action_index}. Repair Canoe (NYI)")
         action_index += 1
    actions[str(action_index)] = ("status", None)
    print(f"    {action_index}. Check detailed status (NYI)")
    action_index += 1
    actions[str(action_index)] = ("quit", None)
    print(f"    {action_index}. Quit Game")
    action_index += 1

    return actions

def get_player_input(valid_actions: dict[str, tuple[str, str | None]]) -> tuple[str, str | None] | None:
    """Gets and validates player input."""
    while True:
        choice = input("Choose an action number: ").strip()
        if choice in valid_actions:
            action_type, details = valid_actions[choice]
            if action_type == "disabled_travel":
                 print("Cannot perform this travel action, the canoe is too damaged!")
                 continue
            return action_type, details
        elif choice.lower() in ['q', 'quit']:
             return ("quit", None)
        else:
            print("Invalid choice. Please enter a number from the list.")


# --- Controller Functions ---

# Modified to accept game_state for logging calls within PartyMember methods
def check_travel_hazards(game_state: GameState):
    """Checks hazards and applies effects, logging via game_state."""
    if not game_state.current_location: return
    hazards = game_state.current_location.hazards
    if not hazards: return

    living_members = [m for m in game_state.party_members if m.is_alive()]
    if not living_members: return # Skip injury checks if no one alive

    for hazard in hazards:
        probability = HAZARD_PROBABILITY.get(hazard, 0)
        if random.random() < probability:
            # Log encounter via game_state's log
            game_state.log_message(f"Hazard encountered: {hazard.capitalize()}!")

            # Canoe Damage
            if hazard in HAZARD_CANOE_DAMAGE:
                min_dmg, max_dmg = HAZARD_CANOE_DAMAGE[hazard]
                damage = random.randint(min_dmg, max_dmg)
                current_canoe_health = game_state.resources.get('canoe_health', 0)
                if current_canoe_health > 0:
                    new_canoe_health = max(0, current_canoe_health - damage)
                    game_state.resources['canoe_health'] = new_canoe_health
                    # Log damage details
                    game_state.log_message(f"The canoe strikes {hazard}, taking {damage} damage! Health: {new_canoe_health}")
                    if new_canoe_health <= 0:
                        game_state.log_message("The canoe is critically damaged and unusable!")

            # Person Damage
            elif hazard in HAZARD_PERSON_DAMAGE:
                min_dmg, max_dmg = HAZARD_PERSON_DAMAGE[hazard]
                damage = random.randint(min_dmg, max_dmg)
                target_member = random.choice(living_members)
                game_state.log_message(f"A {hazard} attacks!")
                # Pass game_state to take_damage and add_status_effect for logging
                target_member.take_damage(damage, game_state)
                target_member.add_status_effect("injured", game_state)

            # Other Hazard Types
            elif hazard == "difficult terrain":
                 game_state.log_message("Travel through difficult terrain was strenuous.")
            # Add more hazard effects here...

# Modified execute_action to pass game_state where needed
def execute_action(game_state: GameState, action_type: str, details: str | None):
    """Interprets action, calls model updates, and triggers time advancement."""
    action_advances_day = False

    if action_type == "travel":
        if details and game_state.current_location:
            destination_id = game_state.current_location.get_destination_id(details)
            if destination_id and destination_id in game_state.locations:
                # Log start of travel before hazards/costs
                game_state.log_message(f"Party begins to travel via '{details}'...")

                # Pass game_state for hazard logging
                check_travel_hazards(game_state)

                canoe_broken = game_state.resources.get('canoe_health', 0) <= 0
                requires_canoe = "paddle" in details.lower()

                if requires_canoe and canoe_broken:
                     game_state.log_message("Travel aborted! The canoe is too damaged.")
                else:
                    game_state.current_location = game_state.locations[destination_id]
                    game_state.log_message(f"Party arrives at {game_state.current_location.name}.")
                    action_advances_day = True
            else:
                game_state.log_message(f"Cannot travel via '{details}'.") # Simplified msg
        else:
             game_state.log_message("Invalid travel details.")

    elif action_type == "forage":
        # TODO: Location-based foraging
        food_found = random.randint(1, 5)
        game_state.resources['food'] += food_found
        game_state.log_message(f"Party forages. Found {food_found} food.") # Use central log
        action_advances_day = True

    elif action_type == "rest":
        game_state.log_message("Party rests for the day.")
        action_advances_day = True

    elif action_type == "repair":
         game_state.log_message("Canoe repair not yet implemented.")

    elif action_type == "status":
        game_state.log_message("Detailed status check not yet implemented.")

    # (quit handled in main loop)
    elif action_type != "quit":
        game_state.log_message(f"Unknown action type: {action_type}")

    # --- Advance Day if Action Consumed Time ---
    if action_advances_day and not game_state.game_over:
        game_state.advance_day()


# --- Main Game Loop ---
# (game_loop function remains the same)
def game_loop():
    """Runs the main game loop."""
    print("Welcome to Everglades Escape!")
    locations = load_locations()
    events = load_events()
    party = create_initial_party()
    game_state = GameState(
        initial_time_limit=INITIAL_TIME_LIMIT,
        initial_food=INITIAL_FOOD,
        initial_canoe_health=INITIAL_CANOE_HEALTH
    )
    start_location_id = "start_hammock"
    if start_location_id not in locations:
        print(f"FATAL ERROR: Start location '{start_location_id}' not found.")
        sys.exit(1)
    game_state.setup_game(party, locations, events, start_location_id)

    while not game_state.game_over:
        display_game_state(game_state) # View
        if game_state.game_over: break
        available_actions = display_available_actions(game_state) # View
        player_choice = get_player_input(available_actions) # Controller (Input)
        if player_choice is None: continue
        action_type, action_details = player_choice
        if action_type == "quit":
            print("Quitting game. Goodbye!")
            break
        # Controller (Action Orchestration) -> Model Update -> Time Advance
        execute_action(game_state, action_type, action_details)

    # --- Game Over Display ---
    print("\n" + "="*10 + " GAME OVER " + "="*10)
    if game_state.win_condition_met: print("Result: VICTORY!")
    else: print("Result: DEFEAT")
    if game_state.loss_reason: print(f"Reason: {game_state.loss_reason}")
    print(f"Game lasted {game_state.current_day - 1} days.")
    display_game_state(game_state) # Show final state

# --- Entry Point ---
if __name__ == "__main__":
    game_loop()