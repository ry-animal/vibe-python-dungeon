"""
Entity factory module for creating and pooling game entities.
"""
import numpy as np
from typing import Tuple, Optional
from dungeon_descent.core.entity import Entity


# Global entity pool as specified in the rules
ENTITY_POOL_SIZE = 10000
ENTITY_POOL = np.empty(ENTITY_POOL_SIZE, dtype=object)
next_eid = 0


def create_entity(
    x: int,
    y: int,
    char: str,
    color: Tuple[int, int, int],
    name: str,
    blocks_movement: bool = False,
    visible: bool = True,
) -> Entity:
    """
    Create an entity from the pool instead of dynamic allocation.
    
    Args:
        x: X-coordinate
        y: Y-coordinate
        char: Character representation
        color: RGB color tuple
        name: Entity name
        blocks_movement: Whether entity blocks movement
        visible: Whether entity is visible
        
    Returns:
        An Entity instance either newly created or recycled from the pool
    """
    global next_eid
    eid = next_eid % ENTITY_POOL_SIZE
    next_eid += 1
    
    if ENTITY_POOL[eid] is None:
        ENTITY_POOL[eid] = Entity(x, y, char, color, name, blocks_movement, visible)
    else:
        # Reuse existing entity
        entity = ENTITY_POOL[eid]
        entity.x = x
        entity.y = y
        entity.char = char
        entity.color = color
        entity.name = name
        entity.blocks_movement = blocks_movement
        entity.visible = visible
        entity.components.clear()  # Reset components
        
    return ENTITY_POOL[eid] 