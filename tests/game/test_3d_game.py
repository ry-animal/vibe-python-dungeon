"""
Test script for the 3D renderer.
"""
import sys
import pygame
from dungeon_descent.core.engine import Engine
from dungeon_descent.rendering.renderer_3d import RoguelikeGL

def main():
    # Initialize the game engine
    engine = Engine()
    
    # Create the 3D renderer
    renderer = RoguelikeGL(engine)
    
    # Hide mouse cursor and grab input
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    # Main game loop
    running = True
    while running:
        # Handle input
        running = renderer.handle_input()
        
        # Update game state
        engine.update()
        
        # Render the frame
        running = renderer.render() and running
    
    # Cleanup
    renderer.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 