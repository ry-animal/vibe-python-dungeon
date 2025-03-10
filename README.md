# Dungeon Descent

A Python roguelike game with both 2D and 3D rendering capabilities. The game emphasizes procedural content generation, permadeath, turn-based combat, and emergent gameplay systems.

## Features

- Procedurally generated dungeons using BSP and cellular automata
- Turn-based combat with tactical depth
- Entity Component System (ECS) architecture
- 2D mode with ASCII/tileset rendering
- 3D mode with OpenGL rendering
- Dynamic field of view and lighting

## Installation

### From Source

1. Clone the repository:

```bash
git clone https://github.com/yourusername/dungeon-descent.git
cd dungeon-descent
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# Or
venv\Scripts\activate  # On Windows
```

3. Install the package in development mode:

```bash
pip install -e .
```

### Using Docker

The game is also containerized and can be run using Docker:

```bash
# Build the image
docker build -t dungeon-descent .

# Run in 2D mode (default)
docker run --rm -it dungeon-descent

# Run in 3D mode (requires X11 forwarding)
docker run --rm -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix dungeon-descent 3d
```

## Running the Game

### Command Line Interface

After installation, you can run the game using the following commands:

```bash
# Run the game (defaults to 2D mode)
dungeon-descent

# Run in 2D mode
dungeon-descent 2d
# Or
dungeon-descent-2d

# Run in 3D mode
dungeon-descent 3d
# Or
dungeon-descent-3d
```

### From Python

```python
# Run in 2D mode
from dungeon_descent.scripts.run_2d import main
main()

# Run in 3D mode
from dungeon_descent.scripts.run_3d import main
main()
```

## Controls

### 2D Mode Controls:

- **Arrow Keys**: Move character
- **ESC**: Exit game

### 3D Mode Controls:

- **WASD**: Move character (in the direction the camera is facing)
- **Mouse**: Look around
- **Arrow Keys**: Alternative movement (cardinal directions)
- **I**: Open/close inventory
- **V**: Toggle first-person/third-person view
- **ESC**: Quit game (or close inventory if open)

### Inventory:

- **Letter Keys (A-Z)**: Use/equip corresponding item
- **ESC**: Close inventory

## Game Mechanics

- Explore procedurally generated dungeons
- Fight enemies (move into them to attack)
- Collect and use items:
  - Potions: Heal HP
  - Scrolls: Area of effect attack
  - Swords: Increase attack power
  - Armor: Increase defense
- Status effects with stacking mechanics

## Project Structure

The project follows a modular architecture:

```
dungeon_descent/
├── __init__.py
├── __main__.py               # Main entry point
├── components/               # ECS components
│   ├── __init__.py
│   ├── ai.py                 # AI behavior
│   ├── fighter.py            # Combat stats
│   ├── inventory.py          # Item storage
│   └── status_effect.py      # Status effects
├── core/                     # Core game systems
│   ├── __init__.py
│   ├── engine.py             # Game engine
│   ├── entity.py             # Entity base class
│   ├── entity_factory.py     # Entity creation
│   └── game_map.py           # Map handling
├── generation/               # Procedural generation
│   ├── __init__.py
│   └── dungeon_generator.py  # Dungeon creation
├── rendering/                # Rendering systems
│   ├── __init__.py
│   ├── camera.py             # 3D camera
│   └── renderer_3d.py        # 3D renderer
└── scripts/                  # Entry point scripts
    ├── run_2d.py             # 2D mode runner
    └── run_3d.py             # 3D mode runner
```

## Development

This project follows an Entity Component System (ECS) architecture for maintainable and extensible code.

### Adding New Components

1. Create a new file in the `components` directory
2. Define your component class
3. Add the component to entities using `entity.add_component("name", component)`

### Adding New Entities

Use the entity factory to create entities:

```python
from dungeon_descent.core.entity_factory import create_entity

entity = create_entity(
    x=10,
    y=10,
    char="@",
    color=(255, 255, 255),
    name="Player",
    blocks_movement=True
)

# Add components
from dungeon_descent.components.fighter import Fighter
entity.add_component("fighter", Fighter(hp=30, defense=2, power=5))
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
# vibe-python-dungeon
