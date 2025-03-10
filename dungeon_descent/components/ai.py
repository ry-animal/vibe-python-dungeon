"""
AI component for entity behavior.
"""
import math
import numpy as np
import random
import tcod
from typing import Tuple, Optional

# Forward imports to avoid circular dependencies
from dungeon_descent.components.fighter import Fighter


class AI:
    """
    Component for entities that have AI behavior.
    
    Attributes:
        entity (Entity): Entity this AI controls
        state (str): Current AI state
        wander_radius (int): Maximum wander distance
        awareness_distance (int): Maximum distance to detect player
        last_known_player_pos (tuple): Last known player position
    """
    def __init__(self, entity: 'Entity'):
        """
        Initialize an AI component.
        
        Args:
            entity: Entity this AI controls
        """
        self.entity = entity
        # Start with idle state, will change based on distance to player
        self.state = "idle"
        self.wander_radius = 5
        self.last_known_player_pos = None
        # Each enemy has awareness distance
        self.awareness_distance = 8
        if hasattr(entity, 'name'):
            # More powerful enemies can see farther
            if entity.name == "Troll":
                self.awareness_distance = 12
            elif entity.name == "Orc":
                self.awareness_distance = 10
            elif entity.name == "Zombie":
                self.awareness_distance = 6  # Zombies have poor vision
        
    def perform(self) -> None:
        """Execute AI behavior based on current state."""
        if not hasattr(self.entity, 'engine') or not self.entity.engine.player:
            return
            
        # Calculate distance to player
        player = self.entity.engine.player
        dx = abs(player.x - self.entity.x)
        dy = abs(player.y - self.entity.y)
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Determine current state based on distance and health
        if "fighter" in self.entity.components:
            fighter = self.entity.components["fighter"]
            health_ratio = fighter.hp / fighter.max_hp
            
            # State transitions
            if health_ratio < 0.3:  # Less than 30% health
                self.state = "flee"
                self.last_known_player_pos = (player.x, player.y)
            elif distance <= self.awareness_distance:
                self.state = "alert"
                self.last_known_player_pos = (player.x, player.y)
            else:
                self.state = "idle"
                
        # Execute behavior based on state
        if self.state == "idle":
            self._wander()
        elif self.state == "alert":
            self._chase_player()
        elif self.state == "flee":
            self._escape()
            
    def _wander(self) -> None:
        """Random movement within wander radius."""
        # 70% chance to move, 30% chance to stand still
        if random.random() < 0.3:
            return

        # Choose a random direction
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        
        # Skip diagonal movement 50% of the time for more natural movement
        if dx != 0 and dy != 0 and random.random() < 0.5:
            if random.random() < 0.5:
                dx = 0
            else:
                dy = 0
        
        # Calculate new position
        new_x = self.entity.x + dx
        new_y = self.entity.y + dy
        
        # Check if the move is valid (in bounds and not a wall)
        engine = self.entity.engine
        if (0 <= new_x < engine.width and 0 <= new_y < engine.height and
                not engine.game_map[new_x, new_y]):
            
            # Check for blocking entities
            for entity in engine.active_entities:
                if (entity != self.entity and entity.blocks_movement and 
                        entity.x == new_x and entity.y == new_y):
                    return  # Can't move there, blocked
            
            # Move to new position
            self.entity.x = new_x
            self.entity.y = new_y
            
    def _chase_player(self) -> None:
        """Use tcod pathfinding to move toward player."""
        # Use entity.engine to access game state
        engine = self.entity.engine
        
        # Create cost map (1 for open tiles, 0 for walls)
        cost = np.ones_like(engine.game_map.tiles, dtype=np.int8)
        cost[engine.game_map.tiles == 1] = 0  # Walls are impassable
        
        # Add entities as obstacles
        for entity in engine.active_entities:
            if entity.blocks_movement and entity != self.entity:
                cost[entity.x, entity.y] = 0
                
        # Create graph and pathfinder
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pf = tcod.path.Pathfinder(graph)
        pf.add_root((engine.player.x, engine.player.y))
        
        # Get path from enemy to player
        if cost[self.entity.x, self.entity.y]:  # If we're on a valid tile
            path = pf.path_to((self.entity.x, self.entity.y))
            if len(path) > 1:  # If there's a path
                next_x, next_y = path[-2]  # Step before the enemy position
                
                # Check if player is at destination (combat)
                if (next_x, next_y) == (engine.player.x, engine.player.y):
                    if "fighter" in self.entity.components and "fighter" in engine.player.components:
                        attacker = self.entity.components["fighter"]
                        defender = engine.player.components["fighter"]
                        damage = Fighter.calculate_damage(attacker, defender)
                        defender.take_damage(damage)
                        print(f"{self.entity.name} attacks you for {damage} damage!")
                else:
                    # Move toward player
                    self.entity.x, self.entity.y = next_x, next_y
        
    def _escape(self) -> None:
        """Use Dijkstra maps to flee from player."""
        # Use entity.engine to access game state
        engine = self.entity.engine
        
        # Create cost map (1 for open tiles, 0 for walls)
        cost = np.ones_like(engine.game_map.tiles, dtype=np.int8)
        cost[engine.game_map.tiles == 1] = 0  # Walls are impassable
        
        # Add entities as obstacles
        for entity in engine.active_entities:
            if entity.blocks_movement and entity != self.entity:
                cost[entity.x, entity.y] = 0
                
        # Create Dijkstra map centered on player
        dijkstra = tcod.path.Dijkstra(cost)
        dijkstra.set_goal(engine.player.x, engine.player.y)
        
        # Get the distance map
        distance_map = dijkstra.as_numpy() 
        
        # Find direction to move AWAY from player (highest distance value)
        available_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                nx, ny = self.entity.x + dx, self.entity.y + dy
                # Check map bounds and if tile is walkable
                if (0 <= nx < engine.width and 0 <= ny < engine.height and 
                        cost[nx, ny] and distance_map[nx, ny] < np.inf):
                    available_moves.append((nx, ny, distance_map[nx, ny]))
        
        if available_moves:
            # Move to the position with maximum distance from player
            best_move = max(available_moves, key=lambda x: x[2])
            self.entity.x, self.entity.y = best_move[0], best_move[1] 