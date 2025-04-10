from main import INITIAL_CANOE_HEALTH
import pygame

# --- Constants ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
BACKGROUND_COLOR = (30, 30, 30) # Dark grey
TEXT_COLOR = (230, 230, 230) # Light grey
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (230, 230, 230)
LOG_AREA_COLOR = (40, 40, 40)

# --- UI Areas ---
# Define rectangles for different UI sections
STATUS_AREA_HEIGHT = 60
PARTY_AREA_WIDTH = 250
LOG_AREA_HEIGHT = 150
ACTION_AREA_HEIGHT = SCREEN_HEIGHT - STATUS_AREA_HEIGHT - LOG_AREA_HEIGHT

STATUS_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, STATUS_AREA_HEIGHT)
PARTY_RECT = pygame.Rect(0, STATUS_AREA_HEIGHT, PARTY_AREA_WIDTH, ACTION_AREA_HEIGHT)
MAIN_AREA_RECT = pygame.Rect(PARTY_AREA_WIDTH, STATUS_AREA_HEIGHT, SCREEN_WIDTH - PARTY_AREA_WIDTH, ACTION_AREA_HEIGHT)
LOG_RECT = pygame.Rect(0, SCREEN_HEIGHT - LOG_AREA_HEIGHT, SCREEN_WIDTH, LOG_AREA_HEIGHT)
ACTION_BUTTON_START_Y = STATUS_AREA_HEIGHT + 10 # Inside MAIN_AREA_RECT

# --- Fonts ---
pygame.font.init() # Initialize font module
FONT_SMALL = pygame.font.SysFont(None, 24)
FONT_MEDIUM = pygame.font.SysFont(None, 32)
FONT_LARGE = pygame.font.SysFont(None, 48)

# --- Button Class ---
class Button:
    """Simple clickable button."""
    def __init__(self, rect, text, action_type, action_details=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action_type = action_type
        self.action_details = action_details
        self.is_hovered = False
        # Add a flag for disabled state if needed for visual feedback
        self.is_disabled = (action_type == "disabled_travel")


    def draw(self, screen):
        color = BUTTON_HOVER_COLOR if self.is_hovered and not self.is_disabled else BUTTON_COLOR
        # Optionally dim the button if disabled
        if self.is_disabled:
             color = (50, 50, 50) # Darker grey for disabled
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        text_surf = FONT_SMALL.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        # Ignore events if disabled
        if self.is_disabled:
            self.is_hovered = False # Ensure hover effect turns off
            return None, None

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1: # Left click
                return self.action_type, self.action_details
        return None, None

# --- Drawing Functions ---

def draw_text(screen, text, font, color, rect, aa=True, wrap=False):
    """Draws text within a rect, optionally wrapping."""
    y = rect.top
    line_spacing = font.get_linesize()

    # Basic check for None or empty text
    if text is None:
        text = ""
    else:
        text = str(text) # Ensure text is a string

    if wrap:
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            # Handle potential multiple spaces or leading/trailing spaces
            word = word.strip()
            if not word: continue

            test_line = f"{current_line} {word}".strip() # Test adding the word
            test_width, _ = font.size(test_line)

            if test_width < rect.width:
                current_line = test_line
            else:
                # If the current line isn't empty, add it
                if current_line:
                    lines.append(current_line)
                # Check if the single word itself is too long
                word_width, _ = font.size(word)
                if word_width >= rect.width:
                    # Simple wrap: just put the long word on its own line
                    # More complex wrapping (breaking words) is needed for better handling
                    lines.append(word)
                    current_line = ""
                else:
                    # Start new line with the current word
                    current_line = word
        # Add the last line if it's not empty
        if current_line:
            lines.append(current_line)

        for line in lines:
            if y + line_spacing > rect.bottom:
                break # Don't draw past the bottom
            text_surface = font.render(line, aa, color)
            text_rect = text_surface.get_rect(topleft=(rect.left, y))
            screen.blit(text_surface, text_rect)
            y += line_spacing
    else:
        # Non-wrapping version
        text_surface = font.render(text, aa, color)
        text_rect = text_surface.get_rect(topleft=rect.topleft)
        # Optional: Add clipping if text exceeds rect width without wrapping
        # screen.blit(text_surface, text_rect, area=screen.get_clip()) # Needs clip rect set
        screen.blit(text_surface, text_rect)


def draw_status_area(screen, game_state):
    """Draws the top status bar."""
    pygame.draw.rect(screen, BACKGROUND_COLOR, STATUS_RECT)
    location_name = game_state.current_location.name if game_state.current_location else "Unknown"
    status_text = (f"Day: {game_state.current_day} | "
                   f"Time Remaining: {game_state.time_remaining} days | "
                   f"Location: {location_name}")
    draw_text(screen, status_text, FONT_MEDIUM, TEXT_COLOR, STATUS_RECT.inflate(-10, -10))


def draw_party_area(screen, game_state):
    """Draws the party member status on the left."""
    pygame.draw.rect(screen, BACKGROUND_COLOR, PARTY_RECT)
    title_rect = pygame.Rect(PARTY_RECT.left + 5, PARTY_RECT.top + 5, PARTY_RECT.width - 10, 30)
    draw_text(screen, "Party Status", FONT_MEDIUM, TEXT_COLOR, title_rect)

    y_offset = title_rect.bottom + 10
    line_height = FONT_SMALL.get_linesize() + 2 # Slightly more space for wrapped lines

    for member in game_state.party_members:
        member_text = str(member) # Use the existing __str__ method
        # Estimate required height based on potential wrapping
        # This is approximate; a better way might calculate lines needed
        num_lines_estimate = len(member_text.split(',')) + 1 # Rough estimate
        required_height = num_lines_estimate * line_height
        member_rect = pygame.Rect(PARTY_RECT.left + 10, y_offset, PARTY_RECT.width - 20, required_height)

        # Check if it fits before drawing
        if member_rect.bottom > PARTY_RECT.bottom - 5:
             break # Stop if no more space

        draw_text(screen, member_text, FONT_SMALL, TEXT_COLOR, member_rect, wrap=True)
        y_offset = member_rect.bottom + 10 # Position next element below this one


def draw_main_area(screen, game_state):
    """Draws the main interaction area (location description, actions)."""
    pygame.draw.rect(screen, BACKGROUND_COLOR, MAIN_AREA_RECT)

    # Location Description
    # Allocate more space for description
    loc_area_height = 120
    desc_rect = pygame.Rect(MAIN_AREA_RECT.left + 10, MAIN_AREA_RECT.top + 10, MAIN_AREA_RECT.width - 20, loc_area_height)
    loc_desc = game_state.current_location.description if game_state.current_location else "No location data."
    # Draw title slightly higher
    draw_text(screen, "Location:", FONT_MEDIUM, TEXT_COLOR, desc_rect)
    # Give description text its own rect below title
    desc_text_rect = pygame.Rect(desc_rect.left, desc_rect.top + 30, desc_rect.width, desc_rect.height - 30)
    draw_text(screen, loc_desc, FONT_SMALL, TEXT_COLOR, desc_text_rect, wrap=True)

    # Resources (simple display for now)
    res_area_height = 60
    res_rect = pygame.Rect(MAIN_AREA_RECT.left + 10, desc_rect.bottom + 10, MAIN_AREA_RECT.width - 20, res_area_height)
    res_text = game_state.get_resource_summary()
    draw_text(screen, res_text, FONT_SMALL, TEXT_COLOR, res_rect, wrap=True)


def draw_log_area(screen, messages):
    """Draws the message log at the bottom."""
    pygame.draw.rect(screen, LOG_AREA_COLOR, LOG_RECT)
    title_rect = pygame.Rect(LOG_RECT.left + 5, LOG_RECT.top + 5, LOG_RECT.width - 10, 25)
    draw_text(screen, "Log", FONT_MEDIUM, TEXT_COLOR, title_rect)

    y_offset = title_rect.bottom + 5
    line_height = FONT_SMALL.get_linesize()
    max_lines = (LOG_RECT.height - (title_rect.height + 10)) // line_height

    # Display latest messages first, up to max_lines
    lines_to_draw = messages[-(max_lines):] # Get the last N messages that fit
    for msg in reversed(lines_to_draw):
        msg_rect = pygame.Rect(LOG_RECT.left + 10, y_offset, LOG_RECT.width - 20, line_height)
        if y_offset + line_height > LOG_RECT.bottom - 5: break # Extra safety check
        draw_text(screen, f"- {msg}", FONT_SMALL, TEXT_COLOR, msg_rect, wrap=False) # No wrap needed for log lines usually
        y_offset += line_height


def create_action_buttons(game_state):
    """Creates Button objects based on available actions."""
    buttons = []
    button_width = 200
    button_height = 40
    padding = 10
    # Determine start position dynamically based on where description/resources end
    # Placeholder start Y - adjust based on dynamic content height if needed later
    start_y = MAIN_AREA_RECT.top + 10 + 120 + 10 + 60 + 20 # Top + Desc Height + Pad + Res Height + Pad

    x_pos = MAIN_AREA_RECT.left + padding
    y_pos = start_y

    max_x = MAIN_AREA_RECT.right - padding
    max_y = LOG_RECT.top - padding

    canoe_functional = game_state.resources.get('canoe_health', 0) > 0

    # Travel Actions
    if game_state.current_location:
        travel_options = game_state.current_location.get_possible_travel_actions()
        for travel_action in travel_options:
            requires_canoe = "paddle" in travel_action.lower()
            button_text = travel_action.capitalize()
            action_type = "travel"
            if requires_canoe and not canoe_functional:
                button_text += " (Canoe Damaged!)"
                # Keep type as travel, but button class handles disabled state
                action_type = "disabled_travel" # Set type for Button class to know

            rect = pygame.Rect(x_pos, y_pos, button_width, button_height)
            buttons.append(Button(rect, button_text, action_type, travel_action))

            # Advance position
            x_pos += button_width + padding
            if x_pos + button_width > max_x: # Move to next row
                x_pos = MAIN_AREA_RECT.left + padding
                y_pos += button_height + padding
            # Check vertical overflow
            if y_pos + button_height > max_y:
                 print("Warning: Not enough space for all action buttons!")
                 break # Stop adding buttons if out of space


    # Position Other Actions
    # Reset to start of next available column/row if needed
    # This simple logic might place them awkwardly, needs refinement
    if x_pos > MAIN_AREA_RECT.left + padding: # If travel actions took space
        pass # Continue in current row if space allows
    else: # If no travel actions, start from initial pos
        x_pos = MAIN_AREA_RECT.left + padding
        y_pos = start_y # Ensure y_pos is correct if no travel actions

    # Other Actions Definition
    other_actions_defs = [
        ("Forage", "forage", None),
        ("Rest", "rest", None),
        # Conditionally add the repair action *tuple*
        ("Repair Canoe (NYI)", "repair", None) if game_state.resources.get('canoe_health', 0) < INITIAL_CANOE_HEALTH else None,
        ("Quit Game", "quit", None)
    ]

    # Filter out None values *before* the loop
    valid_other_actions = [action for action in other_actions_defs if action is not None]

    # Loop through only valid tuples
    for text, type, details in valid_other_actions:
        # Check vertical overflow before creating rect
        if y_pos + button_height > max_y:
             print("Warning: Not enough space for all action buttons!")
             break

        rect = pygame.Rect(x_pos, y_pos, button_width, button_height)
        buttons.append(Button(rect, text, type, details))

        # Advance position
        x_pos += button_width + padding
        if x_pos + button_width > max_x: # Move to next row
            x_pos = MAIN_AREA_RECT.left + padding
            y_pos += button_height + padding

    return buttons