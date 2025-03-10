from typing import List, Optional, Dict, Callable, Any
import numpy as np
import random
import tcod
import functools
import math

def validate_effect_stack(func: Callable) -> Callable:
    """Decorator to validate status effect stacks."""
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
    """Status effect that can be applied to entities with Fighter components."""
    def __init__(self, name: str, duration: int, stacks: int = 1, max_stacks: int = 3):
        self.name = name
        self.duration = duration
        self.stacks = stacks
        self.max_stacks = max_stacks
        self.active_effects: List['StatusEffect'] = []
    
    @validate_effect_stack
    def apply(self, entity: 'Entity') -> None:
        """Apply this effect to an entity."""
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

class Fighter:
    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.status_effects: Dict[str, StatusEffect] = {}
        self.entity = None  # Will be set when attached to an entity
        
    def take_damage(self, amount: int) -> None:
        """Apply damage after defense calculation."""
        self.hp = max(0, self.hp - max(1, amount))
        
    @staticmethod
    def calculate_damage(attacker: 'Fighter', defender: 'Fighter') -> int:
        """Calculate damage using the formula from the spec with random variance.
        
        Damage = attacker.power - defender.defense + random(-2, 2)
        Minimum 1 damage per successful hit.
        """
        assert hasattr(attacker, 'power'), "Missing power component"
        assert hasattr(defender, 'defense'), "Missing defense component"
        
        # Vectorized calculation using numpy
        base_damage = np.array([attacker.power - defender.defense])
        random_variance = np.random.randint(-2, 3, size=1)  # -2 to +2 inclusive
        damage = base_damage + random_variance
        
        # Ensure minimum 1 damage
        return int(max(1, damage[0]))
    
    def apply_status_effect(self, effect: StatusEffect) -> None:
        """Apply a status effect to this Fighter."""
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

class Inventory:
    def __init__(self, capacity: int = 26):
        self.items: List[Optional['Entity']] = [None] * capacity
        self.capacity = capacity
        
    def add_item(self, item: 'Entity') -> bool:
        """Add item to first available slot."""
        for i in range(self.capacity):
            if self.items[i] is None:
                self.items[i] = item
                return True
        return False

class AI:
    def __init__(self, entity: 'Entity'):
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
        # Use entity.engine to access game state without circular import
        engine = self.entity.engine
        
        # Create cost map (1 for open tiles, 0 for walls)
        cost = np.ones_like(engine.game_map, dtype=np.int8)
        cost[engine.game_map == 1] = 0  # Walls are impassable
        
        # Add entities as obstacles
        for entity in engine.active_entities:
            if entity.blocks_movement and entity != self.entity:
                cost[entity.x, entity.y] = 0
                
        # Create Dijkstra map
        dijkstra = tcod.path.DijkstraGrid(cost)
        dijkstra.set_goal(engine.player.x, engine.player.y)
        
        # Get direction to move
        if cost[self.entity.x, self.entity.y]:  # If we're on a valid tile
            path = dijkstra.path_from((self.entity.x, self.entity.y))
            if len(path) > 1:  # If there's a path
                next_x, next_y = path[1]  # First step after current position
                
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
        # Use entity.engine to access game state without circular import
        engine = self.entity.engine
        
        # Create cost map (1 for open tiles, 0 for walls)
        cost = np.ones_like(engine.game_map, dtype=np.int8)
        cost[engine.game_map == 1] = 0  # Walls are impassable
        
        # Add entities as obstacles
        for entity in engine.active_entities:
            if entity.blocks_movement and entity != self.entity:
                cost[entity.x, entity.y] = 0
                
        # Create Dijkstra map centered on player
        dijkstra = tcod.path.DijkstraGrid(cost)
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
