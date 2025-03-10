"""
Status effect component for game effects like poison, bleeding, etc.
"""
from typing import List, Callable
import functools


def validate_effect_stack(func: Callable) -> Callable:
    """
    Decorator to validate status effect stacks.
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Validate before applying effect
        if len(self.active_effects) >= self.max_stacks:
            # Find the effect with the shortest remaining duration
            shortest = min(self.active_effects, key=lambda e: e.duration)
            # Remove it
            self.active_effects.remove(shortest)
        return func(self, *args, **kwargs)
    return wrapper


class StatusEffect:
    """
    Status effect that can be applied to entities with Fighter components.
    
    Attributes:
        name (str): Name of the effect
        duration (int): Duration in turns
        stacks (int): Number of stacks
        max_stacks (int): Maximum number of stacks
        active_effects (list): List of active effects
    """
    def __init__(self, name: str, duration: int, stacks: int = 1, max_stacks: int = 3):
        """
        Initialize a status effect.
        
        Args:
            name: Name of the effect
            duration: Duration in turns
            stacks: Number of stacks (default: 1)
            max_stacks: Maximum number of stacks (default: 3)
        """
        self.name = name
        self.duration = duration
        self.stacks = stacks
        self.max_stacks = max_stacks
        self.active_effects: List['StatusEffect'] = []
    
    @validate_effect_stack
    def apply(self, entity: 'Entity') -> None:
        """
        Apply this effect to an entity.
        
        Args:
            entity: Entity to apply the effect to
        """
        if "status_effects" not in entity.components:
            entity.components["status_effects"] = {}
        
        effects = entity.components["status_effects"]
        if self.name in effects:
            # Increase stacks up to max
            effects[self.name].stacks = min(effects[self.name].stacks + self.stacks, self.max_stacks)
            # Reset duration
            effects[self.name].duration = self.duration
        else:
            # Add new effect
            effects[self.name] = self
            self.active_effects.append(self) 