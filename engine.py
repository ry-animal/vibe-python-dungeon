import tcod
import numpy as np
from typing import Set, Dict, Any, Optional
from map_gen import generate_dungeon
from components import Fighter, Inventory, AI
import random

# Global entity pool as specified in the rules
ENTITY_POOL_SIZE = 10000
ENTITY_POOL = np.empty(ENTITY_POOL_SIZE, dtype=object)
next_eid = 0

def create_entity(
    x: int,
    y: int,
    char: str,
    color: tuple[int, int, int],
    name: str,
    blocks_movement: bool = False,
    visible: bool = True,
) -> 'Entity':
    """Create an entity from the pool instead of dynamic allocation."""
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

class Engine:
    def __init__(self, width: int = 80, height: int = 50):
        """Initialize the game engine with ECS architecture.
        
        Args:
            width: Screen width in tiles (default: 80)
            height: Screen height in tiles (default: 50)
        """
        self.width = width
        self.height = height
        self.active_entities: Set[Entity] = set()
        
        # Initialize map and player
        self.game_map = generate_dungeon(width, height)
        self.player = self._create_player()
        self.active_entities.add(self.player)
        
        # Add some test enemies
        self._populate_dungeon()
        
        # Create console with specified dimensions
        self.console = tcod.console.Console(width, height, order="F")
        
    def _create_player(self) -> 'Entity':
        """Create and return the player entity."""
        # Find a good spot for the player that isn't close to walls
        attempts = 0
        max_attempts = 1000
        best_open_space = None
        best_open_count = -1
        
        while attempts < max_attempts:
            attempts += 1
            # Choose a random position
            x = random.randint(5, self.width - 5)
            y = random.randint(5, self.height - 5)
            
            if self.game_map[x, y]:  # Skip walls
                continue
            
            # Count open spaces in 5x5 area around position
            open_count = 0
            for cx in range(max(0, x-2), min(self.width, x+3)):
                for cy in range(max(0, y-2), min(self.height, y+3)):
                    if not self.game_map[cx, cy]:
                        open_count += 1
            
            # If we found a completely open 5x5 area, use it immediately
            if open_count == 25:
                print(f"Found perfect spawn at ({x}, {y})")
                player = create_entity(
                    x=x,
                    y=y,
                    char="@",
                    color=(255, 255, 255),
                    name="Player",
                    blocks_movement=True
                )
                player.engine = self  # Store reference to engine
                player.add_component("fighter", Fighter(hp=30, defense=2, power=5))
                player.add_component("inventory", Inventory())
                return player
            
            # Otherwise keep track of the best spot found
            if open_count > best_open_count:
                best_open_count = open_count
                best_open_space = (x, y)
        
        # If we couldn't find a perfect spot, use the best one found
        if best_open_space:
            x, y = best_open_space
            print(f"Using best spawn at ({x}, {y}) with {best_open_count} open spaces")
        else:
            # As a fallback, find any open space
            for x in range(self.width):
                for y in range(self.height):
                    if not self.game_map[x, y]:
                        print(f"Fallback spawn at ({x}, {y})")
                        break
                else:
                    continue
                break
        
        player = create_entity(
            x=x,
            y=y,
            char="@",
            color=(255, 255, 255),
            name="Player",
            blocks_movement=True
        )
        player.engine = self  # Store reference to engine
        player.add_component("fighter", Fighter(hp=30, defense=2, power=5))
        player.add_component("inventory", Inventory())
        return player
    
    def _populate_dungeon(self) -> None:
        """Add some test enemies and items to the dungeon."""
        # Add enemies
        enemy_types = [
            {"char": "k", "color": (255, 0, 0), "name": "Kobold", "hp": 10, "defense": 0, "power": 3},
            {"char": "r", "color": (139, 69, 19), "name": "Rat", "hp": 5, "defense": 0, "power": 2},
            {"char": "o", "color": (0, 128, 0), "name": "Orc", "hp": 15, "defense": 1, "power": 4},
            {"char": "z", "color": (0, 100, 0), "name": "Zombie", "hp": 20, "defense": 2, "power": 3},
            {"char": "T", "color": (128, 0, 128), "name": "Troll", "hp": 30, "defense": 3, "power": 8}
        ]
        
        # Generate more enemies for a populated dungeon
        num_enemies = min(20, self.width * self.height // 30)  # Roughly 1 enemy per 30 tiles, max 20
        print(f"Generating {num_enemies} enemies...")
        
        enemies_created = 0
        placement_attempts = 0
        max_attempts = 1000  # Prevent infinite loops
        
        while enemies_created < num_enemies and placement_attempts < max_attempts:
            placement_attempts += 1
            
            # Choose random position
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            # Skip walls and occupied spaces
            if self.game_map[x, y] or any(e.x == x and e.y == y for e in self.active_entities):
                continue
            
            # Choose an enemy type (trolls are rare)
            weights = [0.4, 0.3, 0.2, 0.08, 0.02]  # Probabilities for each enemy type
            enemy_info = random.choices(enemy_types, weights=weights, k=1)[0]
            
            # Create enemy
            enemy = create_entity(
                x=x,
                y=y,
                char=enemy_info["char"],
                color=enemy_info["color"],
                name=enemy_info["name"],
                blocks_movement=True
            )
            enemy.engine = self  # Store reference to engine
            enemy.add_component("fighter", Fighter(
                hp=enemy_info["hp"], 
                defense=enemy_info["defense"], 
                power=enemy_info["power"]
            ))
            enemy.add_component("ai", AI(enemy))
            self.active_entities.add(enemy)
            enemies_created += 1
            
        # Add some items
        item_types = [
            {"char": "!", "color": (0, 255, 255), "name": "Potion", "blocks_movement": False},
            {"char": "?", "color": (255, 255, 0), "name": "Scroll", "blocks_movement": False},
            {"char": "/", "color": (200, 200, 200), "name": "Sword", "blocks_movement": False},
            {"char": "[", "color": (150, 150, 150), "name": "Armor", "blocks_movement": False}
        ]
        
        num_items = min(15, self.width * self.height // 40)  # Roughly 1 item per 40 tiles, max 15
        print(f"Generating {num_items} items...")
        
        items_created = 0
        placement_attempts = 0
        
        while items_created < num_items and placement_attempts < max_attempts:
            placement_attempts += 1
            
            # Choose random position
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            # Skip walls and occupied spaces
            if self.game_map[x, y] or any(e.x == x and e.y == y for e in self.active_entities):
                continue
            
            # Choose a random item type
            item_info = random.choice(item_types)
            
            # Create item
            item = create_entity(
                x=x,
                y=y,
                char=item_info["char"],
                color=item_info["color"],
                name=item_info["name"],
                blocks_movement=item_info["blocks_movement"]
            )
            item.engine = self
            self.active_entities.add(item)
            items_created += 1
        
        print(f"Created {enemies_created} enemies and {items_created} items")
    
    def move_player(self, dx: int, dy: int) -> None:
        """Move player by the given amount if possible."""
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        # Check map bounds
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            # Check if the tile is walkable
            if not self.game_map[new_x, new_y]:
                # Check for blocking entities and combat
                blocked = False
                for entity in self.active_entities:
                    if entity.blocks_movement and entity.x == new_x and entity.y == new_y:
                        if "fighter" in entity.components:
                            # Attack instead of moving
                            attacker = self.player.components["fighter"]
                            defender = entity.components["fighter"]
                            damage = Fighter.calculate_damage(attacker, defender)
                            defender.take_damage(damage)
                            print(f"You hit {entity.name} for {damage} damage!")
                            if defender.hp <= 0:
                                print(f"You killed {entity.name}!")
                                self.active_entities.remove(entity)
                        blocked = True
                        break
                
                if not blocked:
                    # Move player
                    self.player.x = new_x
                    self.player.y = new_y
                    print(f"Moved to ({new_x}, {new_y})")
                    
                    # Check for items to pick up
                    items_at_location = [e for e in self.active_entities 
                                        if e.x == new_x and e.y == new_y and not e.blocks_movement]
                    
                    for item in items_at_location:
                        if "inventory" in self.player.components:
                            # Try to add to inventory
                            if self.player.components["inventory"].add_item(item):
                                print(f"You picked up {item.name}!")
                                self.active_entities.remove(item)
                            else:
                                print("Your inventory is full!")
            else:
                print("You bump into a wall.") # Feedback for hitting walls
        else:
            print("You bump into a wall.") # Feedback for hitting walls
    
    def update(self) -> None:
        """Process one game turn."""
        if self.player:
            # Process player
            self.player.update()
            
            # Process AI entities after player
            # Make a copy of entities since we might modify the set during update
            for entity in list(self.active_entities - {self.player}):
                # Update entity state
                entity.update()
                
                # Process AI
                if "ai" in entity.components:
                    entity.components["ai"].perform()
                    
                # Remove dead entities
                if "fighter" in entity.components and entity.components["fighter"].hp <= 0:
                    print(f"{entity.name} has been defeated!")
                    self.active_entities.remove(entity)
    
    def render(self, context: tcod.context.Context) -> None:
        """Render the current game state."""
        self.console.clear()
        
        # Render map
        for x in range(self.width):
            for y in range(self.height):
                if self.game_map[x, y]:
                    self.console.print(x, y, "#", (255, 255, 255))
                    
        # Render entities
        for entity in self.active_entities:
            if not entity.visible:
                continue
            self.console.print(
                entity.x, entity.y, entity.char, entity.color
            )
            
        context.present(self.console)

class Entity:
    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: tuple[int, int, int],
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

def main() -> None:
    print("Starting Dungeon Descent...")
    # Initialize game engine
    try:
        print("Initializing engine...")
        engine = Engine()
        print(f"Created engine with {len(engine.active_entities)} entities")
        print(f"Player position: ({engine.player.x}, {engine.player.y})")
        
        # Create window with tcod.context.new_terminal as required by the rules
        print("Creating terminal...")
        with tcod.context.new_terminal(
            engine.width,
            engine.height,
            title="Dungeon Descent",
            vsync=True,
        ) as context:
            print("Terminal created, entering main loop...")
            
            while True:
                engine.render(context)
                
                for event in tcod.event.wait():
                    print(f"Event received: {event.type}")
                    if event.type == "QUIT":
                        raise SystemExit()
                    elif event.type == "KEYDOWN":
                        print(f"Key pressed: {event.sym}")
                        # Movement keys
                        if event.sym == tcod.event.KeySym.UP:
                            engine.move_player(0, -1)
                        elif event.sym == tcod.event.KeySym.DOWN:
                            engine.move_player(0, 1)
                        elif event.sym == tcod.event.KeySym.LEFT:
                            engine.move_player(-1, 0)
                        elif event.sym == tcod.event.KeySym.RIGHT:
                            engine.move_player(1, 0)
                        elif event.sym == tcod.event.KeySym.ESCAPE:
                            raise SystemExit()
                        
                        engine.update()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
