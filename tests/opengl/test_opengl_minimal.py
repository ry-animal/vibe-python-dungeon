"""
Minimal OpenGL test script to verify OpenGL functionality.
"""
import sys
import time
import pygame
from pygame.locals import *

# Initialize pygame with strong error handling
pygame.init()
print("Pygame initialized")

try:
    # Try to import OpenGL
    print("Importing OpenGL modules...")
    from OpenGL.GL import *
    from OpenGL.GLU import *
    print("OpenGL modules imported successfully")
    
    # Create a simple window with OpenGL support
    print("Creating OpenGL window...")
    display = pygame.display.set_mode((640, 480), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("OpenGL Test")
    
    # Basic OpenGL setup
    print("Setting up OpenGL...")
    glClearColor(0.0, 0.0, 0.8, 1.0)  # Blue background
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 640/480, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5.0)  # Move back 5 units
    
    # Main loop
    print("Entering main loop...")
    running = True
    frames = 0
    start_time = time.time()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw a simple red triangle
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0, 0.0)  # Red
        glVertex3f(-1.0, -1.0, 0.0)
        glVertex3f(1.0, -1.0, 0.0)
        glVertex3f(0.0, 1.0, 0.0)
        glEnd()
        
        # Update display
        pygame.display.flip()
        
        # FPS counter
        frames += 1
        if frames % 60 == 0:
            current_time = time.time()
            fps = frames / (current_time - start_time)
            print(f"FPS: {fps:.1f}")
            frames = 0
            start_time = current_time
        
        # Cap at 60 FPS
        pygame.time.delay(16)
    
    # Clean up
    pygame.quit()
    print("Test completed successfully")

except Exception as e:
    print(f"Error during OpenGL test: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1) 