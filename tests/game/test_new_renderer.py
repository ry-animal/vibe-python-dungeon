#!/usr/bin/env python3
"""
Test script for the simplified 3D renderer.

This script sets up a simple game environment and
uses the simplified renderer to display the dungeon.
"""
import sys
import os
import math
import random
import pygame
from pygame.locals import *

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dungeon_descent.core.engine import Engine
from dungeon_descent.core.entity import Entity
from dungeon_descent.components.fighter import Fighter
from dungeon_descent.components.inventory import Inventory
from dungeon_descent.core.entity_factory import create_entity
from dungeon_descent.generation.dungeon_generator import generate_dungeon
from dungeon_descent.rendering.renderer_3d_simplified import RoguelikeGL


def main():
    """
    Main entry point for the test script.
    """
    # Create a new dungeon
    print("Generating dungeon...")
    dungeon_width, dungeon_height = 80, 50
    dungeon = generate_dungeon(
        width=dungeon_width,
        height=dungeon_height,
        min_room_size=6
    )
    
    # Create a simple game map structure
    class GameMap:
        def __init__(self, tiles, width, height):
            self.tiles = tiles
            self.width = width
            self.height = height
            self.rooms = []
            self.enemies = []
            self.items = []
            
        def __getitem__(self, key):
            x, y = key
            return self.tiles[x, y]
            
        def is_blocked(self, x, y):
            """Check if a position is blocked by a wall or entity."""
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return True
                
            # Check if the tile is a wall
            if self.tiles[x, y] == 1:
                return True
                
            # Check if there's an entity blocking the tile
            for entity in self.enemies:
                if entity.x == x and entity.y == y and entity.blocks_movement:
                    return True
                    
            return False
    
    # Convert numpy array to game map
    game_map = GameMap(dungeon, dungeon_width, dungeon_height)
    
    # Find a suitable player position (first floor tile)
    player_pos = None
    for y in range(dungeon_height):
        for x in range(dungeon_width):
            if dungeon[x, y] == 0:  # Floor tile
                player_pos = (x, y)
                break
        if player_pos:
            break
    
    print(f"Player spawn at {player_pos}")
    print(f"Map size: {dungeon_width}x{dungeon_height}")
    
    # Create a player entity
    player = Entity(
        x=player_pos[0],
        y=player_pos[1],
        char="@",
        color=(255, 255, 255),
        name="Player",
        blocks_movement=True,
    )
    player.add_component("fighter", Fighter(hp=30, defense=2, power=5))
    player.add_component("inventory", Inventory(capacity=26))
    player.position = (player_pos[0], player_pos[1])  # Add position attribute for renderer
    
    # Create some enemies
    enemies = []
    enemy_count = 20
    for _ in range(enemy_count):
        # Find a random walkable position
        while True:
            x = random.randint(0, dungeon_width - 1)
            y = random.randint(0, dungeon_height - 1)
            if not dungeon[x, y] and (x, y) != player_pos:
                break
        
        # Create an orc or troll
        if random.random() < 0.8:  # 80% chance of orc
            enemy = Entity(
                x=x,
                y=y,
                char="o",
                color=(63, 127, 63),
                name="Orc",
                blocks_movement=True,
            )
            enemy.add_component("fighter", Fighter(hp=10, defense=0, power=3))
            enemy.position = (x, y)  # Add position attribute for renderer
        else:  # 20% chance of troll
            enemy = Entity(
                x=x,
                y=y,
                char="T",
                color=(0, 127, 0),
                name="Troll",
                blocks_movement=True,
            )
            enemy.add_component("fighter", Fighter(hp=16, defense=1, power=4))
            enemy.position = (x, y)  # Add position attribute for renderer
        
        enemies.append(enemy)
    
    # Create some items
    items = []
    item_count = 15
    for _ in range(item_count):
        # Find a random walkable position
        while True:
            x = random.randint(0, dungeon_width - 1)
            y = random.randint(0, dungeon_height - 1)
            if not dungeon[x, y] and (x, y) != player_pos:
                # Make sure it's not on top of an enemy
                if not any(e.x == x and e.y == y for e in enemies):
                    break
        
        # Create a potion, scroll, sword or armor
        item_type = random.choice(["Health Potion", "Fireball Scroll", "Sword", "Armor"])
        
        if item_type == "Health Potion":
            item = Entity(
                x=x,
                y=y,
                char="!",
                color=(127, 0, 127),
                name="Health Potion",
                blocks_movement=False,
            )
            item.position = (x, y)  # Add position attribute for renderer
        elif item_type == "Fireball Scroll":
            item = Entity(
                x=x,
                y=y,
                char="~",
                color=(255, 255, 0),
                name="Fireball Scroll",
                blocks_movement=False,
            )
            item.position = (x, y)  # Add position attribute for renderer
        elif item_type == "Sword":
            item = Entity(
                x=x,
                y=y,
                char="/",
                color=(0, 191, 255),
                name="Sword",
                blocks_movement=False,
            )
            item.position = (x, y)  # Add position attribute for renderer
        else:  # Armor
            item = Entity(
                x=x,
                y=y,
                char="[",
                color=(139, 69, 19),
                name="Armor",
                blocks_movement=False,
            )
            item.position = (x, y)  # Add position attribute for renderer
        
        items.append(item)
    
    # Add entities to the game map
    game_map.enemies = enemies
    game_map.items = items
    
    # Create the engine
    engine = Engine(width=dungeon_width, height=dungeon_height)
    
    # Replace the engine's player and game map with our custom ones
    engine.player = player
    engine.game_map = game_map
    engine.active_entities.add(player)
    for enemy in enemies:
        engine.active_entities.add(enemy)
    
    # Add a dummy message_log to the engine
    class Message:
        def __init__(self, text):
            self.full_text = text
            
    class MessageLog:
        def __init__(self):
            self.messages = []
            
        def add_message(self, text):
            self.messages.append(Message(text))
            
    engine.message_log = MessageLog()
    engine.message_log.add_message("Welcome to Dungeon Descent!")
    engine.message_log.add_message("Use WASD to move, mouse to look around.")
    engine.message_log.add_message("Press F to toggle wireframe mode.")
    engine.message_log.add_message("Press V to toggle first/third person view.")
    engine.message_log.add_message("Press ESC to quit.")
    
    # Create the renderer
    renderer = RoguelikeGL(engine=engine, width=1024, height=768)
    
    # Add missing attributes
    renderer.use_fog = False
    renderer.wireframe_mode = False
    renderer.show_minimap = True
    renderer.show_inventory = False
    renderer.first_person = False
    
    # Set camera to player position
    px, py = player.x, player.y
    renderer.camera.position = [px, 0.5, py]
    
    # Print controls
    print("\nControls:")
    print("WASD: Move the camera")
    print("Mouse: Look around")
    print("F: Toggle wireframe mode")
    print("V: Toggle first/third person view")
    print("M: Toggle minimap")
    print("I: Toggle inventory")
    print("ESC: Quit")
    
    # Main game loop
    running = True
    while running:
        # Handle input
        running = renderer.handle_input()
        
        # Render the scene
        renderer.render()
        
        # Cap the frame rate
        renderer.clock.tick(60)
    
    # Clean up
    renderer.cleanup()


if __name__ == "__main__":
    main() 