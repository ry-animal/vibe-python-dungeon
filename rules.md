<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 

---

# Cursor Rules for Python Roguelike Development

This document establishes project-specific rules for AI-assisted development of *Dungeon Descent* using Python's tcod ecosystem. Based on analysis of 130+ industry rulesets and genre-specific patterns from the provided specification, these directives optimize code quality while maintaining alignment with roguelike conventions.

---

## Core Principles

### 1.1 Architectural Constraints

- **ECS Enforcement**:

```python  
# Approved pattern  
class Inventory:  
    def __init__(self, capacity):  
        self.items = []  
        self.capacity = capacity  

entity.components['inventory'] = Inventory(10)  

# Rejected pattern  
class Player(InventoryHolder):  # Inheritance violates ECS  
    pass  
```

    - Prefer composition via component dictionaries over class inheritance
    - Store all game state in numpy arrays for spatial queries


### 1.2 Library Usage

- **tcod Best Practices**:
    - Initialize contexts with `tcod.context.new_terminal()` not SDL2 fallbacks
    - Use `tcod.path.DijkstraGrid` for AI pathfinding instead of custom A*

```python  
# Approved pathfinding implementation  
cost = np.ones((map_width, map_height), dtype=np.int8)  
dijkstra = tcod.path.DijkstraGrid(cost)  
dijkstra.set_goal(player_position)  
```

- **Numerical Optimization**:
    - Vectorize damage calculations using numpy broadcasting
    - Preallocate entity buffers with `np.ndarray(dtype=object)`

---

## Code Generation Rules

### 2.1 Procedural Content Implementation

- **Map Generation Standards**:
    - Implement BSP trees with recursive division:

```python  
def split_node(node, min_size):  
    if node.w < min_size*2 or node.h < min_size*2:  
        return  
    # Horizontal/vertical split logic  
    # Must maintain 1-tile border between rooms  
```

    - Cellular automata parameters:
        - Wall probability: 0.45 ± 0.05
        - Smoothing iterations: 4-6


### 2.2 Combat System Constraints

- **Damage Calculation Validation**:

```python  
def calculate_damage(attacker, defender):  
    assert hasattr(attacker, 'power'), "Missing power component"  
    assert hasattr(defender, 'defense'), "Missing defense component"  
    return max(1, attacker.power - defender.defense + random.randint(-2, 2))  
```

    - Enforce integer math for deterministic replay potential
    - Validate status effect stacks with `@validate_effect_stack` decorator

---

## Quality Assurance Directives

### 3.1 Testing Requirements

- **Monte Carlo Validation**:

```python  
def test_combat_balance():  
    results = [simulate_combat(lvl1_player, lvl1_enemy) for _ in range(1000)]  
    win_rate = sum(results)/len(results)  
    assert 0.45 < win_rate < 0.55, "Imbalanced early-game combat"  
```

- **Performance Benchmarks**:
    - 60 FPS minimum on 10,000 entity stress tests
    - Pathfinding completion <16ms per frame


### 3.2 Error Handling

- **State Corruption Prevention**:

```python  
def save_game():  
    with atomic_write('save.sav') as f:  
        json.dump({  
            'entities': [e.serialize() for e in entities],  
            'rng_state': random.getstate()  
        }, f)  
```

    - Use CRC32 checksums for save file validation
    - Isolate RNG state for deterministic bug reproduction

---

## Documentation Standards

### 4.1 Code Annotation

- **Procedural Generation Documentation**:

```python  
def generate_caves(width, height):  
    """Implements cellular automata cave generation  
    Args:  
        width: Map x-dimension (must be ≥64)  
        height: Map y-dimension (must be ≥64)  
    Returns:  
        np.ndarray: 2D grid where 1=wall, 0=floor  
    Algorithm:  
        1. Random 45% wall initialization  
        2. 4 iterations of Moore neighborhood smoothing  
        3. Flood-fill validation  
    """  
```

- **API Contract Enforcement**:
    - Type hint all public functions/methods
    - Mark private methods with leading underscore

---

## Security \& Modding

### 5.1 Input Sanitization

- **Lua Scripting Preparation**:

```python  
SANDBOX = {  
    'math': math,  
    'vector': lambda x,y: (x,y),  
    'print': logging.debug  
}  

def execute_mod_script(code):  
    compiled = ast.parse(code, mode='exec')  
    # Validate AST for unsafe operations  
    exec(compiled, SANDBOX)  
```

    - Restrict filesystem access in modding API
    - Rate limit script execution to 10ms/frame


### 5.2 Anti-Cheat Measures

- **Delta Compression**:

```python  
def validate_player_action(action, prev_state):  
    max_move_distance = 5 if prev_state['has_haste'] else 1  
    if action['dx']**2 + action['dy']**2 > max_move_distance**2:  
        raise InvalidAction("Impossible movement")  
```

    - Checksum critical game state every 10 turns
    - Obfuscate RNG seed generation

---

## Optimization Profile

### 6.1 Memory Management

- **Entity Pooling**:

```python  
ENTITY_POOL = np.empty(10000, dtype=[  
    ('x', 'i4'), ('y', 'i4'),  
    ('glyph', 'S1'), ('color', '3u1')  
])  

def create_entity():  
    global next_eid  
    eid = next_eid % len(ENTITY_POOL)  
    next_eid += 1  
    return ENTITY_POOL[eid]  
```

    - Recycle entity IDs instead of dynamic allocation
    - Batch FOV updates using dirty flags


### 6.2 Rendering Constraints

- **Terminal Optimization**:
    - Limit redraws to changed console regions
    - Precompute color palettes as 256-color indexes

```python  
PALETTE = {  
    'blood_red': tcod.Color(136, 8, 8),  
    'dungeon_gray': tcod.Color(68, 68, 68)  
}  
```


---

These rules establish guardrails for maintaining the project's architectural integrity while allowing AI-assisted development to accelerate feature implementation. By enforcing ECS patterns, deterministic simulation, and performance-critical optimizations, the ruleset ensures generated code aligns with both Python best practices and roguelike genre expectations.

<div style="text-align: center">⁂</div>

[^1]: https://docs.cursor.com/context/rules-for-ai

[^2]: https://www.redblobgames.com/x/2025-roguelike-dev/

[^3]: https://www.prompthub.us/blog/top-cursor-rules-for-coding-agents

[^4]: https://dotcursorrules.com

[^5]: https://www.redblobgames.com/x/2126-roguelike-dev/

[^6]: https://www.datacamp.com/tutorial/cursor-ai-code-editor

[^7]: https://forum.cursor.com/t/introducing-unofficial-cursor-rules-cli-find-the-perfect-rules-for-your-project/58691

[^8]: https://www.youtube.com/watch?v=Vy7dJKv1EpA

[^9]: https://github.com/PatrickJS/awesome-cursorrules/blob/main/rules/python-projects-guide-cursorrules-prompt-file/.cursorrules

[^10]: https://github.com/PatrickJS/awesome-cursorrules

[^11]: https://forum.cursor.com/t/share-your-rules-for-ai/2377

[^12]: https://cursor.directory/deep-learning-developer-python-cursor-rules

[^13]: https://www.reddit.com/r/roguelikedev/comments/194qh0f/could_someone_give_me_a_pointer_on_this_issue_im/

[^14]: https://github.com/yuru-sha/roguelike

[^15]: https://www.youtube.com/watch?v=16VCTGAQONQ

[^16]: https://www.yosenspace.com/posts/lets-code-roguelike-tutorial-part6-combat-engine.html

[^17]: https://www.gamedeveloper.com/design/how-to-make-a-roguelike

