"""
Script to run the 3D version of Dungeon Descent.
"""
import sys
import time
import pygame
from pygame.locals import *

# Try to load OpenGL with explicit error handling
try:
    print("Initializing OpenGL...")
    from OpenGL.GL import *
    from OpenGL.GLU import *
    print(f"OpenGL Vendor: {glGetString(GL_VENDOR).decode('utf-8') if glGetString(GL_VENDOR) else 'Unknown'}")
    print(f"OpenGL Renderer: {glGetString(GL_RENDERER).decode('utf-8') if glGetString(GL_RENDERER) else 'Unknown'}")
    print(f"OpenGL Version: {glGetString(GL_VERSION).decode('utf-8') if glGetString(GL_VERSION) else 'Unknown'}")
except Exception as e:
    print(f"Error initializing OpenGL: {e}")
    print("This could indicate a problem with your graphics drivers or PyOpenGL installation.")
    print("Please ensure you have proper OpenGL support on your system.")
    import traceback
    traceback.print_exc()
    sys.exit(1)

from dungeon_descent.core.engine import Engine
from dungeon_descent.rendering.renderer_3d import RoguelikeGL


def main():
    """
    Run the 3D version of Dungeon Descent.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    try:
        # Initialize pygame
        pygame.init()
        
        # Test creating a simple window to verify OpenGL works
        print("Testing OpenGL window creation...")
        test_display = pygame.display.set_mode((320, 240), pygame.OPENGL | pygame.DOUBLEBUF)
        glClearColor(1.0, 0.0, 0.0, 1.0)  # Red background for test
        glClear(GL_COLOR_BUFFER_BIT)
        pygame.display.flip()
        time.sleep(0.5)  # Show the red screen briefly
        pygame.display.quit()
        
        print("Starting Dungeon Descent 3D...")
        
        # Initialize the engine (game state)
        engine = Engine()
        print(f"Created game engine with {len(engine.active_entities)} entities")
        
        # Initialize the 3D renderer with a larger initial window for better visibility
        print("Creating 3D renderer...")
        renderer = RoguelikeGL(engine, width=1024, height=768)
        
        # Print starting position of player for debugging
        print(f"Player starting position: ({engine.player.x}, {engine.player.y})")
        
        # Main game loop
        running = True
        last_frame = time.time()
        frames = 0
        
        print("Entering main loop...")
        print("\nControls:")
        print("  WASD: Move character (in the direction the camera is facing)")
        print("  Mouse: Look around")
        print("  Arrow Keys: Alternative movement (cardinal directions)")
        print("  I: Open/close inventory")
        print("  V: Toggle first-person/third-person view (Press D to toggle debug mode)")
        print("  ESC: Quit game (or close inventory if open)")
        
        while running:
            # Handle input (returns False if the game should exit)
            running = renderer.handle_input()
            
            # Clear and render the scene
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            running = running and renderer.render()
            
            # Calculate FPS
            frames += 1
            if frames % 100 == 0:
                now = time.time()
                fps = 100 / (now - last_frame)
                print(f"FPS: {fps:.1f}")
                last_frame = now
        
        # Clean up resources
        renderer.cleanup()
        print("Game ended.")
        return 0
        
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main()) 