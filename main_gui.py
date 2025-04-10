# Main entry point and game loop for Everglades Escape (Pygame Version).
import pygame
import sys
import random

# Assuming src package structure allows these imports
from src.game_state import GameState
from src.character import PartyMember
from src.world import Location
from src.events import GameEvent, sudden_storm_effect, found_berries_effect, snake_bite_effect # Example events
import src.gui as gui # Import the gui module

# --- Constants ---
# Constants moved to gui.py where possible
INITIAL_TIME_LIMIT = 30
INITIAL_FOOD = 20
INITIAL_CANOE_HEALTH = 100

# --- Hazard Probabilities & Effects (Keep for game logic) ---
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


# --- Placeholder Data Loading (Same as text version) ---
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

# --- Controller Functions (Adapted from text version) ---
# Keep hazard checking and action execution logic here for now
# Could be moved to GameState or a dedicated Controller class later

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


def execute_action(game_state: GameState, action_type: str, details: str | None):
    """Interprets action, calls model updates, and triggers time advancement."""
    action_advances_day = False

    if action_type == "travel":
        if details and game_state.current_location:
            destination_id = game_state.current_location.get_destination_id(details)
            if destination_id and destination_id in game_state.locations:
                game_state.log_message(f"Party begins to travel via '{details}'...")
                check_travel_hazards(game_state) # Check for hazards BEFORE moving

                canoe_broken = game_state.resources.get('canoe_health', 0) <= 0
                requires_canoe = "paddle" in details.lower()

                if requires_canoe and canoe_broken:
                     game_state.log_message("Travel aborted! The canoe is too damaged.")
                else:
                    game_state.current_location = game_state.locations[destination_id]
                    game_state.log_message(f"Party arrives at {game_state.current_location.name}.")
                    action_advances_day = True # Successful travel takes time
            else:
                game_state.log_message(f"Cannot travel via '{details}'.") # Log failed attempt
        else:
             game_state.log_message("Invalid travel details.")

    elif action_type == "forage":
        # TODO: Implement location-based foraging based on resource_availability
        food_found = random.randint(1, 5)
        game_state.resources['food'] += food_found
        game_state.log_message(f"Party forages. Found {food_found} food.")
        action_advances_day = True

    elif action_type == "rest":
        game_state.log_message("Party rests for the day.")
        # TODO: Implement healing/recovery during rest
        action_advances_day = True

    elif action_type == "repair":
         game_state.log_message("Canoe repair not yet implemented.")
         # TODO: Implement repair logic (requires resources, time)
         # action_advances_day = True # Repair would take time

    elif action_type == "disabled_travel":
         game_state.log_message("Cannot perform this travel action, the canoe is too damaged!")
         # Does not advance day

    # (quit handled in main loop)
    elif action_type != "quit":
        game_state.log_message(f"Unknown or invalid action type: {action_type}")

    # --- Advance Day if Action Consumed Time ---
    if action_advances_day and not game_state.game_over:
        game_state.advance_day() # advance_day handles daily consumption, effects, game over checks

# --- Main Game Loop (Pygame Version) ---
def game_loop_gui():
    """Runs the main Pygame game loop."""
    pygame.init()
    screen = pygame.display.set_mode((gui.SCREEN_WIDTH, gui.SCREEN_HEIGHT))
    pygame.display.set_caption("Everglades Escape")
    clock = pygame.time.Clock()

    # --- Game Initialization ---
    print("Loading game data...") # Keep console message for loading
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
        pygame.quit()
        sys.exit(1)
    game_state.setup_game(party, locations, events, start_location_id)
    print("Game loaded. Starting GUI...")

    # --- GUI Element Initialization ---
    action_buttons = gui.create_action_buttons(game_state)
    # Keep track of messages for the log area
    message_history = list(game_state.get_and_clear_messages()) # Get initial messages

    running = True
    while running and not game_state.game_over:
        # --- Event Handling ---
        chosen_action_type = None
        chosen_action_details = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                chosen_action_type = "quit" # Treat closing window as quit
            # Handle button events
            for button in action_buttons:
                action_type, action_details = button.handle_event(event)
                if action_type:
                    chosen_action_type = action_type
                    chosen_action_details = action_details
                    break # Process one button click per frame

        # --- Action Execution ---
        if chosen_action_type:
            if chosen_action_type == "quit":
                running = False
                game_state.log_message("Quitting game.")
            else:
                execute_action(game_state, chosen_action_type, chosen_action_details)
                # Refresh buttons in case state change affects them (e.g., canoe fixed)
                action_buttons = gui.create_action_buttons(game_state)
                # Add new messages to history
                message_history.extend(game_state.get_and_clear_messages())

        # --- Drawing ---
        screen.fill(gui.BACKGROUND_COLOR) # Clear screen

        # Draw UI Areas
        gui.draw_status_area(screen, game_state)
        gui.draw_party_area(screen, game_state)
        gui.draw_main_area(screen, game_state) # Draws description, resources
        gui.draw_log_area(screen, message_history)

        # Draw Buttons
        for button in action_buttons:
            button.draw(screen)

        pygame.display.flip() # Update the full screen

        # --- Frame Rate ---
        clock.tick(30) # Limit frame rate to 30 FPS

    # --- Game Over Sequence ---
    print("\nGame Over!") # Console message
    if game_state.loss_reason: print(f"Reason: {game_state.loss_reason}")

    # Display final state on screen for a few seconds
    if game_state.game_over:
        screen.fill(gui.BACKGROUND_COLOR)
        gui.draw_status_area(screen, game_state)
        gui.draw_party_area(screen, game_state)
        gui.draw_main_area(screen, game_state)
        # Display Game Over Message centrally
        result_text = "VICTORY!" if game_state.win_condition_met else "DEFEAT"
        reason_text = game_state.loss_reason if game_state.loss_reason else ""
        final_msg = f"GAME OVER: {result_text}\n{reason_text}\nGame lasted {game_state.current_day - 1} days."

        msg_rect = pygame.Rect(0, 0, 400, 200)
        msg_rect.center = screen.get_rect().center

        # Simple overlay box
        overlay_rect = msg_rect.inflate(20, 20)
        pygame.draw.rect(screen, (50, 0, 0) if not game_state.win_condition_met else (0, 50, 0), overlay_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 150), overlay_rect, 3, border_radius=10) # Border

        gui.draw_text(screen, final_msg, gui.FONT_MEDIUM, gui.TEXT_COLOR, msg_rect, wrap=True)

        pygame.display.flip()
        pygame.time.wait(5000) # Wait 5 seconds before closing


    pygame.quit()
    sys.exit()


# --- Entry Point ---
if __name__ == "__main__":
    game_loop_gui()