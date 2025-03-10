"""
Entity module containing the base Entity class used throughout the game.
"""
from typing import Dict, Any, Tuple, Optional


class Entity:
    """
    Base entity class for game objects.
    
    Attributes:
        x (int): X-coordinate in the game map
        y (int): Y-coordinate in the game map
        char (str): Character to represent the entity
        color (tuple): RGB color for the entity
        name (str): Name of the entity
        blocks_movement (bool): Whether the entity blocks movement
        visible (bool): Whether the entity is visible
        components (dict): Dictionary of components attached to the entity
        engine (optional): Reference to the game engine
    """
    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: Tuple[int, int, int],
        name: str,
        blocks_movement: bool = False,
        visible: bool = True,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.visible = visible
        self.components: Dict[str, Any] = {}
        self.engine = None  # Will be set when added to engine
        
    def update(self) -> None:
        """Update entity state, including status effects."""
        # Update fighter status effects if present
        if "fighter" in self.components:
            self.components["fighter"].update_status_effects()
            
    def add_component(self, name: str, component: Any) -> None:
        """Add a component with proper entity reference setup."""
        self.components[name] = component
        # Set entity reference if component has an entity attribute
        if hasattr(component, "entity"):
            component.entity = self 