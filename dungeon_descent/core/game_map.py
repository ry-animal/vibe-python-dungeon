"""
Game map module containing the GameMap class.
"""
import numpy as np
from typing import Tuple, Optional


class GameMap:
    """
    Represents the game world/level.
    
    Attributes:
        width (int): Width of the map
        height (int): Height of the map
        tiles (numpy.ndarray): 2D array of tiles (1=wall, 0=floor)
    """
    def __init__(self, width: int, height: int):
        """
        Initialize a new game map.
        
        Args:
            width: Width of the map
            height: Height of the map
        """
        self.width = width
        self.height = height
        self.tiles = np.ones((width, height), dtype=np.int8)
        
    def in_bounds(self, x: int, y: int) -> bool:
        """
        Check if coordinates are within map bounds.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            
        Returns:
            bool: True if coordinates are within map bounds
        """
        return 0 <= x < self.width and 0 <= y < self.height
        
    def is_walkable(self, x: int, y: int) -> bool:
        """
        Check if a tile is walkable.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            
        Returns:
            bool: True if the tile is walkable (floor)
        """
        if not self.in_bounds(x, y):
            return False
        return self.tiles[x, y] == 0
        
    def __getitem__(self, key):
        """
        Allow accessing tiles directly using game_map[x, y].
        
        Args:
            key: Tuple of (x, y) coordinates or slice
            
        Returns:
            The tile value at the specified coordinates
        """
        return self.tiles[key] 