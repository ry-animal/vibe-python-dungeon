#!/usr/bin/env python3
"""
Dungeon Descent 3D - A roguelike game with 3D rendering
"""
import sys
import time
from engine import Engine, Entity
from renderer_3d import RoguelikeGL

def main():
    """Main entry point for the 3D roguelike game."""
    print("Starting Dungeon Descent 3D...")
    
    # Initialize the engine (game state)
    engine = Engine()
    print(f"Created game engine with {len(engine.active_entities)} entities")
    
    # Initialize the 3D renderer
    print("Creating 3D renderer...")
    renderer = RoguelikeGL(engine)
    
    # Main game loop
    running = True
    last_frame = time.time()
    frames = 0
    
    print("Entering main loop...")
    while running:
        # Handle input (returns False if the game should exit)
        running = renderer.handle_input()
        
        # Render the scene
        renderer.render()
        
        # Calculate FPS
        frames += 1
        if frames % 100 == 0:
            now = time.time()
            fps = 100 / (now - last_frame)
            print(f"FPS: {fps:.1f}")
            last_frame = now
    
    print("Game ended.")

if __name__ == "__main__":
    main() 