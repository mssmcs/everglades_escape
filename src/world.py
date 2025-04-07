# src/world.py

from typing import List, Dict, Optional

class Location:
    """Represents a distinct area in the game world."""

    def __init__(self,
                 location_id: str, # Unique identifier
                 name: str,
                 description: str,
                 connections: Optional[Dict[str, str]] = None, # Maps action/direction -> destination location_id
                 hazards: Optional[List[str]] = None, # e.g., ["snakes", "submerged logs"]
                 resource_availability: Optional[Dict[str, float]] = None, # e.g., {"fish": 0.7, "herbs": 0.3} probability
                 is_destination: bool = False):
        """
        Initializes a location.

        Args:
            location_id: A unique string identifier for this location.
            name: The display name of the location.
            description: Text describing the location.
            connections: Dictionary mapping travel actions/directions (e.g., "paddle north",
                         "follow west slough") to the location_id of the destination.
            hazards: A list of potential dangers present at this location.
            resource_availability: A dictionary mapping resource names to their
                                   availability (e.g., probability 0.0-1.0).
            is_destination: True if this is the target destination to win the game.
        """
        self.location_id: str = location_id
        self.name: str = name
        self.description: str = description
        # Use empty dict/list if None is passed to avoid shared mutable defaults
        self.connections: Dict[str, str] = connections if connections is not None else {}
        self.hazards: List[str] = hazards if hazards is not None else []
        self.resource_availability: Dict[str, float] = resource_availability if resource_availability is not None else {}
        self.is_destination: bool = is_destination

    def get_possible_travel_actions(self) -> List[str]:
        """Returns the list of possible travel actions from this location."""
        return list(self.connections.keys())

    def get_destination_id(self, travel_action: str) -> Optional[str]:
        """Gets the destination location ID for a given travel action."""
        return self.connections.get(travel_action)

    def __str__(self) -> str:
        """String representation of the location."""
        conn_str = ", ".join(self.connections.keys())
        return (f"{self.name} ({self.location_id})\n"
                f"  Description: {self.description}\n"
                f"  Connections: {conn_str if conn_str else 'None'}\n"
                f"  Hazards: {', '.join(self.hazards) if self.hazards else 'None'}\n"
                f"  Resources: {self.resource_availability}\n"
                f"  Is Destination: {self.is_destination}")


# Example Usage (optional, for testing this file directly)
if __name__ == '__main__':
    start_hammock = Location(
        location_id="start_hammock",
        name="Shaded Hammock",
        description="A small, relatively dry island of hardwood trees.",
        connections={"paddle east": "murky_slough", "trek south": "shallow_marsh"},
        resource_availability={"wood": 0.5, "herbs": 0.2}
    )
    murky_slough = Location(
        location_id="murky_slough",
        name="Murky Slough",
        description="A slow-moving channel of dark water, thick with vegetation.",
        connections={"paddle west": "start_hammock", "paddle north": "river_fork"},
        hazards=["submerged logs", "alligator"],
        resource_availability={"fish": 0.6, "reeds": 0.8}
    )
    destination = Location(
        location_id="safe_haven",
        name="Coastal Mound (Safe Haven)",
        description="A large shell mound near the coast, offering safety.",
        is_destination=True
    )

    print("--- Locations ---")
    print(start_hammock)
    print("\n" + str(murky_slough))
    print("\n" + str(destination))
    print(f"\nTravel options from {start_hammock.name}: {start_hammock.get_possible_travel_actions()}")
    dest_id = start_hammock.get_destination_id("paddle east")
    print(f"Destination ID for 'paddle east' from {start_hammock.name}: {dest_id}")
    print("-" * 20)

