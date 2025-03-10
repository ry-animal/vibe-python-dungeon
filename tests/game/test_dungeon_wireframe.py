"""
Simplified dungeon wireframe renderer.
"""
import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from dungeon_descent.core.engine import Engine

def draw_wireframe_cube(x, y, z):
    """Draw a wireframe cube at the given position."""
    # Define cube vertices
    vertices = [
        (x-0.5, y-0.5, z-0.5), (x+0.5, y-0.5, z-0.5), 
        (x+0.5, y+0.5, z-0.5), (x-0.5, y+0.5, z-0.5),
        (x-0.5, y-0.5, z+0.5), (x+0.5, y-0.5, z+0.5),
        (x+0.5, y+0.5, z+0.5), (x-0.5, y+0.5, z+0.5)
    ]
    
    # Define cube edges
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
        (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
        (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
    ]
    
    # Draw cube edges
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_wireframe_grid(center_x, center_y, size):
    """Draw a wireframe grid on the ground plane."""
    glColor3f(0.3, 0.3, 0.3)  # Dark gray for grid
    glBegin(GL_LINES)
    
    # Draw grid lines
    for i in range(-size, size + 1, 2):
        # X axis lines
        glVertex3f(center_x - size, 0, center_y + i)
        glVertex3f(center_x + size, 0, center_y + i)
        
        # Z axis lines
        glVertex3f(center_x + i, 0, center_y - size)
        glVertex3f(center_x + i, 0, center_y + size)
    
    glEnd()

def render_dungeon(engine, camera_distance=20.0):
    """Render the dungeon as wireframes."""
    game_map = engine.game_map
    
    # Get player position
    player_x, player_y = engine.player.x, engine.player.y
    
    # Setup viewport for top-down view
    glLoadIdentity()
    gluLookAt(
        player_x, camera_distance, player_y,  # Camera above player
        player_x, 0, player_y,                # Looking at player
        0, 0, -1                             # Up vector
    )
    
    # Draw a grid
    draw_wireframe_grid(player_x, player_y, 20)
    
    # Set render range (render area around player)
    render_distance = 15
    min_x = max(0, int(player_x) - render_distance)
    max_x = min(game_map.width, int(player_x) + render_distance)
    min_y = max(0, int(player_y) - render_distance)
    max_y = min(game_map.height, int(player_y) + render_distance)
    
    # Draw walls as wireframe cubes
    glColor3f(1.0, 1.0, 1.0)  # White for walls
    
    for y in range(min_y, max_y):
        for x in range(min_x, max_x):
            if game_map.tiles[x, y] == 1:  # Wall
                # Draw a wireframe cube
                draw_wireframe_cube(x, 0.5, y)
    
    # Draw player as a colored cube
    glColor3f(1.0, 1.0, 0.0)  # Yellow for player
    draw_wireframe_cube(player_x, 0.5, player_y)
    
    # Draw enemies as red cubes
    glColor3f(1.0, 0.0, 0.0)  # Red for enemies
    for entity in engine.active_entities:
        if entity != engine.player and hasattr(entity, 'ai'):
            draw_wireframe_cube(entity.x, 0.5, entity.y)

def main():
    """Main function."""
    # Initialize pygame and OpenGL
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Dungeon Wireframe")
    
    # Set up the perspective
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    
    # Initialize the game engine
    engine = Engine()
    
    # Set clear color to dark blue
    glClearColor(0.0, 0.0, 0.3, 1.0)
    
    # Set up the model view matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Camera distance
    camera_distance = 20.0
    
    # Main loop
    running = True
    clock = pygame.time.Clock()
    
    print(f"Player position: ({engine.player.x}, {engine.player.y})")
    print(f"Map size: {engine.game_map.width}x{engine.game_map.height}")
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Adjust camera distance with + and -
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    camera_distance = max(5.0, camera_distance - 1.0)
                elif event.key == pygame.K_MINUS:
                    camera_distance = min(30.0, camera_distance + 1.0)
                # Toggle enemies attacking with spacebar
                elif event.key == pygame.K_SPACE:
                    engine.update()
        
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Render the dungeon
        render_dungeon(engine, camera_distance)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    print("Starting dungeon wireframe renderer...")
    main() 