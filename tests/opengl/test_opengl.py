"""
Simple OpenGL test script to verify OpenGL functionality.
"""
import sys
import time
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Initialize pygame
pygame.init()
print("Pygame initialized")

# Set up the display with OpenGL
print("Creating OpenGL window...")
display = pygame.display.set_mode((640, 480), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("OpenGL Test")

# Initialize OpenGL
glViewport(0, 0, 640, 480)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, (640/480), 0.1, 50.0)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glTranslatef(0.0, 0.0, -5)

# Enable depth test
glEnable(GL_DEPTH_TEST)

print("OpenGL initialized")
print(f"OpenGL Version: {glGetString(GL_VERSION).decode('utf-8')}")
print(f"OpenGL Vendor: {glGetString(GL_VENDOR).decode('utf-8')}")
print(f"OpenGL Renderer: {glGetString(GL_RENDERER).decode('utf-8')}")

# Main loop
print("Entering main loop...")
running = True
rotation = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5)
    
    # Rotate the scene
    glRotatef(rotation, 1, 1, 1)
    rotation += 1
    
    # Draw a colorful cube
    glBegin(GL_QUADS)
    
    # Front face (red)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-1.0, -1.0, 1.0)
    glVertex3f(1.0, -1.0, 1.0)
    glVertex3f(1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    
    # Back face (green)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    glVertex3f(1.0, 1.0, -1.0)
    glVertex3f(1.0, -1.0, -1.0)
    
    # Top face (blue)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(1.0, 1.0, 1.0)
    glVertex3f(1.0, 1.0, -1.0)
    
    # Bottom face (yellow)
    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(1.0, -1.0, -1.0)
    glVertex3f(1.0, -1.0, 1.0)
    glVertex3f(-1.0, -1.0, 1.0)
    
    # Right face (magenta)
    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(1.0, -1.0, -1.0)
    glVertex3f(1.0, 1.0, -1.0)
    glVertex3f(1.0, 1.0, 1.0)
    glVertex3f(1.0, -1.0, 1.0)
    
    # Left face (cyan)
    glColor3f(0.0, 1.0, 1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(-1.0, -1.0, 1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    
    glEnd()
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    pygame.time.delay(16)

# Clean up
pygame.quit()
print("Test completed successfully") 