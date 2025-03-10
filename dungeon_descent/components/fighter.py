"""
Fighter component for combat mechanics.
"""
from typing import Dict, Optional
import numpy as np
import random


class Fighter:
    """
    Component for entities that can fight.
    
    Attributes:
        hp (int): Current hit points
        max_hp (int): Maximum hit points
        defense (int): Defense value
        power (int): Attack power
        status_effects (dict): Status effects applied to this fighter
        entity (Optional[Entity]): Reference to the entity this component belongs to
    """
    def __init__(self, hp: int, defense: int, power: int):
        """
        Initialize a fighter component.
        
        Args:
            hp: Hit points
            defense: Defense value
            power: Attack power
        """
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.status_effects: Dict[str, 'StatusEffect'] = {}
        self.entity = None  # Will be set when attached to an entity
        
    def take_damage(self, amount: int) -> None:
        """
        Apply damage after defense calculation.
        
        Args:
            amount: Amount of damage to take
        """
        self.hp = max(0, self.hp - max(1, amount))
        
    @staticmethod
    def calculate_damage(attacker: 'Fighter', defender: 'Fighter') -> int:
        """
        Calculate damage using the formula from the spec with random variance.
        
        Damage = attacker.power - defender.defense + random(-2, 2)
        Minimum 1 damage per successful hit.
        
        Args:
            attacker: Attacking fighter
            defender: Defending fighter
            
        Returns:
            int: Amount of damage to deal
        """
        assert hasattr(attacker, 'power'), "Missing power component"
        assert hasattr(defender, 'defense'), "Missing defense component"
        
        # Vectorized calculation using numpy
        base_damage = np.array([attacker.power - defender.defense])
        random_variance = np.random.randint(-2, 3, size=1)  # -2 to +2 inclusive
        damage = base_damage + random_variance
        
        # Ensure minimum 1 damage
        return int(max(1, damage[0]))
    
    def apply_status_effect(self, effect: 'StatusEffect') -> None:
        """
        Apply a status effect to this Fighter.
        
        Args:
            effect: Status effect to apply
        """
        effect.apply(self.entity)
    
    def update_status_effects(self) -> None:
        """Update all status effects, decrementing duration and removing expired effects."""
        expired = []
        for name, effect in self.status_effects.items():
            effect.duration -= 1
            if effect.duration <= 0:
                expired.append(name)
        
        # Remove expired effects
        for name in expired:
            del self.status_effects[name] 