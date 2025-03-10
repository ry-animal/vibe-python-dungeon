"""
Dungeon generator module for procedural level generation.
"""
import numpy as np
import random
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class Room:
    """
    Represents a room in the dungeon.
    
    Attributes:
        x (int): X-coordinate of the top-left corner
        y (int): Y-coordinate of the top-left corner
        w (int): Width of the room
        h (int): Height of the room
    """
    x: int
    y: int
    w: int
    h: int


class BSPNode:
    """
    Binary space partition node for dungeon generation.
    
    Attributes:
        x (int): X-coordinate of the top-left corner
        y (int): Y-coordinate of the top-left corner
        w (int): Width of the node
        h (int): Height of the node
        left (BSPNode): Left child node
        right (BSPNode): Right child node
        room (Room): Room contained in this node
    """
    def __init__(self, x: int, y: int, w: int, h: int):
        """
        Initialize a BSP node.
        
        Args:
            x: X-coordinate of the top-left corner
            y: Y-coordinate of the top-left corner
            w: Width of the node
            h: Height of the node
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.left: Optional[BSPNode] = None
        self.right: Optional[BSPNode] = None
        self.room: Optional[Room] = None


def generate_dungeon(width: int, height: int, min_room_size: int = 6) -> np.ndarray:
    """
    Generate dungeon using BSP for rooms and cellular automata for caves.
    
    Args:
        width: Map width
        height: Map height
        min_room_size: Minimum size for rooms
        
    Returns:
        np.ndarray: 2D grid where 1=wall, 0=floor
    """
    print(f"Generating {width}x{height} dungeon...")
    
    # Initialize with walls
    dungeon = np.ones((width, height), dtype=np.int8)
    
    # Generate BSP tree
    root = BSPNode(0, 0, width, height)
    _split_node(root, min_room_size)
    
    # Create rooms
    rooms = []
    _create_rooms(root, rooms)
    print(f"Created {len(rooms)} rooms")
    
    # Carve rooms and corridors
    for room in rooms:
        _carve_room(dungeon, room)
    _connect_rooms(dungeon, rooms)
    
    # Apply cellular automata to create more open areas
    _apply_cave_generation(dungeon)
    
    # Ensure dungeon isn't too dense with walls
    wall_count = np.sum(dungeon)
    wall_percentage = wall_count / (width * height) * 100
    print(f"Wall percentage: {wall_percentage:.1f}%")
    
    # If the dungeon is too full of walls, open it up more
    if wall_percentage > 60:
        print("Dungeon too dense, opening up...")
        _open_up_dungeon(dungeon)
        wall_count = np.sum(dungeon)
        wall_percentage = wall_count / (width * height) * 100
        print(f"New wall percentage: {wall_percentage:.1f}%")
    
    return dungeon


def _split_node(node: BSPNode, min_size: int) -> None:
    """
    Recursively split node into binary space partition.
    
    Args:
        node: Node to split
        min_size: Minimum size for splitting
    """
    # Check if node is too small to split further
    if node.w < min_size * 2 or node.h < min_size * 2:
        return
        
    # Choose split direction (horizontal/vertical)
    split_horizontal = np.random.random() > node.w / (node.w + node.h)
    
    if split_horizontal:
        # Make sure we have enough space for a valid split point
        if node.h - min_size * 2 < 1:
            return  # Can't split horizontally
        # Generate random split point ensuring min_size space on both sides
        split_point = np.random.randint(min_size, node.h - min_size)
        node.left = BSPNode(node.x, node.y, node.w, split_point)
        node.right = BSPNode(node.x, node.y + split_point, node.w, node.h - split_point)
    else:
        # Make sure we have enough space for a valid split point
        if node.w - min_size * 2 < 1:
            return  # Can't split vertically
        # Generate random split point ensuring min_size space on both sides
        split_point = np.random.randint(min_size, node.w - min_size)
        node.left = BSPNode(node.x, node.y, split_point, node.h)
        node.right = BSPNode(node.x + split_point, node.y, node.w - split_point, node.h)
    
    _split_node(node.left, min_size)
    _split_node(node.right, min_size)


def _create_rooms(node: BSPNode, rooms: List[Room]) -> None:
    """
    Create rooms within BSP leaf nodes.
    
    Args:
        node: Node to create rooms in
        rooms: List to append rooms to
    """
    if node.left or node.right:
        if node.left:
            _create_rooms(node.left, rooms)
        if node.right:
            _create_rooms(node.right, rooms)
    else:
        # Create larger rooms - fill most of the node
        room_w = max(3, node.w - 4)  # Bigger rooms
        room_h = max(3, node.h - 4)  # Bigger rooms
        room_x = node.x + (node.w - room_w) // 2  # Center in node
        room_y = node.y + (node.h - room_h) // 2  # Center in node
        
        # Create room
        node.room = Room(room_x, room_y, room_w, room_h)
        rooms.append(node.room)


def _carve_room(dungeon: np.ndarray, room: Room) -> None:
    """
    Carve room into dungeon array.
    
    Args:
        dungeon: Dungeon array to carve into
        room: Room to carve
    """
    # Make sure room is within bounds
    x1 = max(0, room.x)
    y1 = max(0, room.y)
    x2 = min(dungeon.shape[0], room.x + room.w)
    y2 = min(dungeon.shape[1], room.y + room.h)
    
    dungeon[x1:x2, y1:y2] = 0


def _connect_rooms(dungeon: np.ndarray, rooms: List[Room]) -> None:
    """
    Create corridors between adjacent rooms.
    
    Args:
        dungeon: Dungeon array to carve into
        rooms: List of rooms to connect
    """
    for i in range(len(rooms) - 1):
        start = _get_room_center(rooms[i])
        end = _get_room_center(rooms[i + 1])
        _create_corridor(dungeon, start, end)
    
    # Add more corridors to ensure connectivity
    for i in range(len(rooms) // 2):
        room1 = random.choice(rooms)
        room2 = random.choice(rooms)
        if room1 != room2:
            start = _get_room_center(room1)
            end = _get_room_center(room2)
            _create_corridor(dungeon, start, end)


def _get_room_center(room: Room) -> Tuple[int, int]:
    """
    Get center coordinates of a room.
    
    Args:
        room: Room to get center of
        
    Returns:
        Tuple[int, int]: Center coordinates (x, y)
    """
    return (room.x + room.w // 2, room.y + room.h // 2)


def _create_corridor(dungeon: np.ndarray, start: Tuple[int, int], end: Tuple[int, int]) -> None:
    """
    Create L-shaped corridor between points.
    
    Args:
        dungeon: Dungeon array to carve into
        start: Start coordinates (x, y)
        end: End coordinates (x, y)
    """
    x1, y1 = start
    x2, y2 = end
    
    # Ensure corridor is within dungeon bounds
    x1 = max(0, min(dungeon.shape[0] - 1, x1))
    y1 = max(0, min(dungeon.shape[1] - 1, y1))
    x2 = max(0, min(dungeon.shape[0] - 1, x2))
    y2 = max(0, min(dungeon.shape[1] - 1, y2))
    
    # Horizontal then vertical
    if np.random.random() > 0.5:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            dungeon[x, y1] = 0
        for y in range(min(y1, y2), max(y1, y2) + 1):
            dungeon[x2, y] = 0
    # Vertical then horizontal
    else:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            dungeon[x1, y] = 0
        for x in range(min(x1, x2), max(x1, x2) + 1):
            dungeon[x, y2] = 0


def _apply_cave_generation(dungeon: np.ndarray) -> None:
    """
    Apply cellular automata to create natural cave formations.
    
    Args:
        dungeon: Dungeon array to apply cellular automata to
    """
    wall_chance = 0.45  # As specified in rules
    iterations = np.random.randint(4, 7)  # 4-6 iterations as specified in rules
    
    # Apply to 20% of walls for more caves (increased from 10%)
    wall_mask = (dungeon == 1) & (np.random.random(dungeon.shape) < 0.2)
    cave_area = np.random.random(dungeon.shape) < wall_chance
    cave_area = cave_area & wall_mask
    
    # Apply cellular automata iterations
    for _ in range(iterations):
        new_cave = np.copy(cave_area)
        for x in range(1, dungeon.shape[0] - 1):
            for y in range(1, dungeon.shape[1] - 1):
                if not wall_mask[x, y]:
                    continue
                # Count walls in Moore neighborhood
                walls = np.sum(cave_area[x-1:x+2, y-1:y+2])
                # Apply cellular automata rules
                if walls >= 5:
                    new_cave[x, y] = 1
                else:
                    new_cave[x, y] = 0
        cave_area = new_cave
    
    # Apply cave generation to dungeon
    dungeon[wall_mask] = cave_area[wall_mask]


def _open_up_dungeon(dungeon: np.ndarray) -> None:
    """
    Apply additional steps to make the dungeon more open.
    
    Args:
        dungeon: Dungeon array to open up
    """
    # Do several iterations of "opening up" - removing isolated walls
    for _ in range(3):
        for x in range(1, dungeon.shape[0] - 1):
            for y in range(1, dungeon.shape[1] - 1):
                if dungeon[x, y] == 1:  # Wall
                    # Count floor neighbors
                    floor_neighbors = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dungeon[x+dx, y+dy] == 0:
                                floor_neighbors += 1
                    
                    # If this wall has 4+ floor neighbors, make it a floor
                    if floor_neighbors >= 4:
                        dungeon[x, y] = 0
    
    # Create a few more random corridors
    for _ in range(10):
        x1 = np.random.randint(5, dungeon.shape[0] - 5)
        y1 = np.random.randint(5, dungeon.shape[1] - 5)
        x2 = np.random.randint(5, dungeon.shape[0] - 5)
        y2 = np.random.randint(5, dungeon.shape[1] - 5)
        
        _create_corridor(dungeon, (x1, y1), (x2, y2)) 