"""
Inventory component for item management.
"""
from typing import List, Optional


class Inventory:
    """
    Component for entities that can carry items.
    
    Attributes:
        items (list): List of items in the inventory
        capacity (int): Maximum number of items that can be carried
    """
    def __init__(self, capacity: int = 26):
        """
        Initialize an inventory component.
        
        Args:
            capacity: Maximum number of items (default: 26, for A-Z keys)
        """
        self.items: List[Optional['Entity']] = [None] * capacity
        self.capacity = capacity
        
    def add_item(self, item: 'Entity') -> bool:
        """
        Add item to first available slot.
        
        Args:
            item: Item to add to inventory
            
        Returns:
            bool: True if item was added, False if inventory is full
        """
        for i in range(self.capacity):
            if self.items[i] is None:
                self.items[i] = item
                return True
        return False 