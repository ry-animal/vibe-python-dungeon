"""
3D renderer module using PyOpenGL.
"""
import math
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from ..core.engine import Engine
from .camera_3d import Camera


class RoguelikeGL:
    """
    3D renderer for the roguelike game using OpenGL.
    
    Attributes:
        engine: Game engine instance
        width: Screen width
        height: Screen height
        camera: Camera for 3D navigation
        colors: Dictionary of colors for different entities
        animation_time: Timer for animations
        textures: Dictionary of textures
        screen: Pygame display surface
        clock: Pygame clock for timing
        font: Font for UI text
        big_font: Larger font for titles
        hud_surface: Surface for HUD elements
        first_person: Whether to use first-person view
        show_inventory: Whether to show the inventory
    """
    
    def __init__(self, engine: Engine, width: int = 1024, height: int = 768):
        """
        Initialize the 3D renderer.
        
        Args:
            engine: Game engine instance
            width: Screen width
            height: Screen height
        """
        self.engine = engine
        self.width = width
        self.height = height
        
        # Initialize Pygame with OpenGL
        pygame.init()
        pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Dungeon Descent 3D")
        
        # Initialize camera
        self.camera = Camera()
        self.camera.position = [0.0, 10.0, 0.0]
        self.camera.target = [0.0, 0.0, 0.0]
        self.camera.up = [0.0, 1.0, 0.0]
        
        # Setup colors
        self.colors = {
            'white': (1.0, 1.0, 1.0),
            'black': (0.0, 0.0, 0.0),
            'red': (1.0, 0.0, 0.0),
            'green': (0.0, 1.0, 0.0),
            'blue': (0.0, 0.0, 1.0),
            'yellow': (1.0, 1.0, 0.0),
            'wall': (0.5, 0.5, 0.5),
            'floor': (0.3, 0.3, 0.3),
            'player': (0.0, 0.5, 1.0),
            'orc': (0.0, 0.8, 0.0),
            'troll': (0.0, 0.6, 0.0),
            'potion': (0.8, 0.0, 0.8),
            'scroll': (0.8, 0.8, 0.0),
            'sword': (0.7, 0.7, 0.7),
            'armor': (0.5, 0.5, 0.7),
            'default': (0.7, 0.7, 0.7)
        }
        
        # Initialize OpenGL
        self._setup_opengl()
        
        # Setup UI elements
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 32)
        self.hud_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # View settings
        self.first_person = True
        self.show_inventory = False
        self.animation_time = 0.0
        self.textures = {}
        
        # Debug mode - makes everything super visible
        self.debug_mode = True
        
        # For smooth mouse movement
        pygame.mouse.set_visible(False)  # Hide the mouse cursor
        pygame.event.set_grab(True)  # Capture the mouse
        pygame.mouse.set_pos(width // 2, height // 2)  # Center the mouse
        self.mouse_last_pos = (width // 2, height // 2)
        
        # Load textures
        self.load_textures()
    
    def _setup_opengl(self):
        """Set up the OpenGL rendering environment."""
        # Set the viewport
        glViewport(0, 0, self.width, self.height)
        
        # Set up the projection matrix - use same values as working test
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        
        # Switch to model view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Set clear color to dark blue for consistency with working test
        glClearColor(0.0, 0.0, 0.4, 1.0)
        
        # Minimal OpenGL setup - similar to working test script
        glDisable(GL_DEPTH_TEST)  # Disable depth testing initially
        glDisable(GL_CULL_FACE)   # Disable culling
        glDisable(GL_LIGHTING)    # Disable lighting
    
    def draw_cube(self, position, color, size=1.0):
        """
        Draw a cube at the given position with the given color and size.
        
        Args:
            position: (x, y, z) position
            color: (r, g, b) color
            size: Size multiplier
        """
        x, y, z = position
        
        # Make sure color intensity is high enough to be visible
        # Convert RGB to HSL, increase lightness, then back to RGB
        color_r, color_g, color_b = color
        
        # Make sure none of the color components are too dark
        color_r = max(0.4, color_r)
        color_g = max(0.4, color_g)
        color_b = max(0.4, color_b)
        
        # Set emission to make cubes more visible
        glMaterialfv(GL_FRONT, GL_EMISSION, (color_r * 0.2, color_g * 0.2, color_b * 0.2, 1.0))
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(size, size, size)
        
        glColor3f(color_r, color_g, color_b)
        
        # Define vertices of a cube (centered at origin)
        vertices = [
            (-0.5, -0.5, -0.5),  # 0 - bottom left back
            (0.5, -0.5, -0.5),   # 1 - bottom right back
            (0.5, 0.5, -0.5),    # 2 - top right back
            (-0.5, 0.5, -0.5),   # 3 - top left back
            (-0.5, -0.5, 0.5),   # 4 - bottom left front
            (0.5, -0.5, 0.5),    # 5 - bottom right front
            (0.5, 0.5, 0.5),     # 6 - top right front
            (-0.5, 0.5, 0.5)     # 7 - top left front
        ]
        
        # Define faces using vertex indices
        faces = [
            (0, 1, 2, 3),  # Back face
            (4, 5, 6, 7),  # Front face
            (0, 4, 7, 3),  # Left face
            (1, 5, 6, 2),  # Right face
            (3, 2, 6, 7),  # Top face
            (0, 1, 5, 4)   # Bottom face
        ]
        
        # Draw each face as a quad
        glBegin(GL_QUADS)
        for face in faces:
            # Add a slight normal variation for each face for better lighting
            if face == faces[0]:   # Back
                glNormal3f(0, 0, -1)
            elif face == faces[1]: # Front
                glNormal3f(0, 0, 1)
            elif face == faces[2]: # Left
                glNormal3f(-1, 0, 0)
            elif face == faces[3]: # Right
                glNormal3f(1, 0, 0)
            elif face == faces[4]: # Top
                glNormal3f(0, 1, 0)
            elif face == faces[5]: # Bottom
                glNormal3f(0, -1, 0)
                
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
        
        # Reset emission
        glMaterialfv(GL_FRONT, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))
        
        glPopMatrix()
    
    def draw_floor_tile(self, x, z):
        """
        Draw a single floor tile at the given position.
        
        Args:
            x: X-coordinate
            z: Z-coordinate
        """
        glPushMatrix()
        glTranslatef(x, -0.5, z)
        glColor3fv(self.colors["floor"])
        
        # Top face of the tile
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)  # Normal pointing up
        glVertex3f(-0.5, 0, -0.5)
        glVertex3f(0.5, 0, -0.5)
        glVertex3f(0.5, 0, 0.5)
        glVertex3f(-0.5, 0, 0.5)
        glEnd()
        
        glPopMatrix()
    
    def draw_cylinder(self, segments):
        """
        Draw a cylinder centered at origin.
        
        Args:
            segments: Number of segments for smoothness
        """
        # Top and bottom circles
        for y in [0.5, -0.5]:
            glBegin(GL_TRIANGLE_FAN)
            glNormal3f(0, 1 if y > 0 else -1, 0)
            glVertex3f(0, y, 0)  # Center
            for i in range(segments + 1):
                angle = 2.0 * math.pi * i / segments
                x = math.cos(angle)
                z = math.sin(angle)
                glVertex3f(x, y, z)
            glEnd()
        
        # Side faces
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x = math.cos(angle)
            z = math.sin(angle)
            glNormal3f(x, 0, z)
            glVertex3f(x, 0.5, z)
            glVertex3f(x, -0.5, z)
        glEnd()
    
    def draw_sphere(self, segments):
        """
        Draw a sphere centered at origin.
        
        Args:
            segments: Number of segments for smoothness
        """
        for i in range(segments):
            lat0 = math.pi * (-0.5 + (i / segments))
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + ((i + 1) / segments))
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)
            
            glBegin(GL_QUAD_STRIP)
            for j in range(segments + 1):
                lng = 2 * math.pi * (j / segments)
                x = math.cos(lng)
                y = math.sin(lng)
                
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0, y * zr0, z0)
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd() 

    def render(self, input_handler=None):
        """
        Render the game world in 3D.
        
        Args:
            input_handler: Optional input handler for processing events
        
        Returns:
            True if the game should continue, False if it should exit
        """
        # Process events if input handler is provided
        if input_handler:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                # Handle other events using the input handler
                if input_handler.handle_event(event):
                    return False
        
        # Handle events directly
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Reset the view matrix
        glLoadIdentity()
        
        # Set camera position - similar to working test
        player_x, player_y = self.engine.player.x, self.engine.player.y
        
        # Position camera above and behind player looking at player
        glTranslatef(-player_x, -2.0, -player_y - 5.0)
        
        print(f"Player position: ({player_x}, {player_y})")
        
        # Draw a wireframe grid on the ground plane
        self._draw_wireframe_grid(player_x, player_y, 10)
        
        # Draw the dungeon as wireframes
        self._render_wireframe_dungeon()
        
        # Draw the player as a wireframe cube
        self._draw_player_wireframe()
        
        # Update the display
        pygame.display.flip()
        
        # Limit the frame rate
        self.clock.tick(60)
        
        return True
    
    def _draw_wireframe_grid(self, center_x, center_y, size):
        """Draw a wireframe grid on the ground plane."""
        glColor3f(0.5, 0.5, 0.5)  # Gray for grid
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
    
    def _render_wireframe_dungeon(self):
        """Render the dungeon as wireframes."""
        game_map = self.engine.game_map
        
        # Get player position
        player_x, player_y = int(self.engine.player.x), int(self.engine.player.y)
        
        # Set render range (render 15 tiles around player)
        render_distance = 15
        min_x = max(0, player_x - render_distance)
        max_x = min(game_map.width, player_x + render_distance)
        min_y = max(0, player_y - render_distance)
        max_y = min(game_map.height, player_y + render_distance)
        
        # Draw walls as wireframe cubes
        glColor3f(1.0, 1.0, 1.0)  # White for walls
        
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                if game_map.tiles[x, y] == 1:  # Wall
                    # Draw a wireframe cube
                    self._draw_wireframe_cube(x, 0.5, y)
    
    def _draw_wireframe_cube(self, x, y, z):
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
    
    def _draw_player_wireframe(self):
        """Draw the player as a wireframe cube."""
        x, y = self.engine.player.x, self.engine.player.y
        
        # Use a bright color for the player
        glColor3f(1.0, 1.0, 0.0)  # Yellow
        
        # Draw a slightly taller cube for the player
        vertices = [
            (x-0.3, 0, y-0.3), (x+0.3, 0, y-0.3), 
            (x+0.3, 1.0, y-0.3), (x-0.3, 1.0, y-0.3),
            (x-0.3, 0, y+0.3), (x+0.3, 0, y+0.3),
            (x+0.3, 1.0, y+0.3), (x-0.3, 1.0, y+0.3)
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
    
    def _render_axes(self):
        """Render coordinate axes for debugging."""
        glDisable(GL_LIGHTING)
        
        # X axis (red)
        glBegin(GL_LINES)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(5, 0, 0)
        glEnd()
        
        # Y axis (green)
        glBegin(GL_LINES)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 5, 0)
        glEnd()
        
        # Z axis (blue)
        glBegin(GL_LINES)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 5)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def _render_debug_scene(self, player_x, player_y):
        """Render a simple debug scene with bright colors to verify rendering works."""
        # Draw a grid on the ground plane
        glBegin(GL_LINES)
        for i in range(-10, 11, 2):  # Draw fewer lines for performance
            # X lines (bright red)
            glColor3f(1.0, 0.0, 0.0)  # Red for X
            glVertex3f(player_x - 10, -0.5, player_y + i)
            glVertex3f(player_x + 10, -0.5, player_y + i)
            
            # Z lines (bright blue)
            glColor3f(0.0, 0.0, 1.0)  # Blue for Z
            glVertex3f(player_x + i, -0.5, player_y - 10)
            glVertex3f(player_x + i, -0.5, player_y + 10)
        glEnd()
        
        # Draw huge colorful cubes for better visibility
        for dx in range(-5, 6, 2):
            for dz in range(-5, 6, 2):
                glPushMatrix()
                glTranslatef(player_x + dx*2, 0, player_y + dz*2)
                
                # Draw a large cube (4x4x4) with extremely bright colors
                glBegin(GL_QUADS)
                # Front face (bright red)
                glColor3f(1.0, 0.0, 0.0)
                glVertex3f(-1.0, -1.0, 1.0)
                glVertex3f(1.0, -1.0, 1.0)
                glVertex3f(1.0, 1.0, 1.0)
                glVertex3f(-1.0, 1.0, 1.0)
                
                # Back face (bright green)
                glColor3f(0.0, 1.0, 0.0)
                glVertex3f(-1.0, -1.0, -1.0)
                glVertex3f(-1.0, 1.0, -1.0)
                glVertex3f(1.0, 1.0, -1.0)
                glVertex3f(1.0, -1.0, -1.0)
                
                # Top face (bright blue)
                glColor3f(0.0, 0.0, 1.0)
                glVertex3f(-1.0, 1.0, -1.0)
                glVertex3f(-1.0, 1.0, 1.0)
                glVertex3f(1.0, 1.0, 1.0)
                glVertex3f(1.0, 1.0, -1.0)
                
                # Bottom face (bright yellow)
                glColor3f(1.0, 1.0, 0.0)
                glVertex3f(-1.0, -1.0, -1.0)
                glVertex3f(1.0, -1.0, -1.0)
                glVertex3f(1.0, -1.0, 1.0)
                glVertex3f(-1.0, -1.0, 1.0)
                
                # Right face (bright magenta)
                glColor3f(1.0, 0.0, 1.0)
                glVertex3f(1.0, -1.0, -1.0)
                glVertex3f(1.0, 1.0, -1.0)
                glVertex3f(1.0, 1.0, 1.0)
                glVertex3f(1.0, -1.0, 1.0)
                
                # Left face (bright cyan)
                glColor3f(0.0, 1.0, 1.0)
                glVertex3f(-1.0, -1.0, -1.0)
                glVertex3f(-1.0, -1.0, 1.0)
                glVertex3f(-1.0, 1.0, 1.0)
                glVertex3f(-1.0, 1.0, -1.0)
                glEnd()
                
                glPopMatrix()
    
    def _render_dungeon(self):
        """Render the dungeon walls and floor."""
        game_map = self.engine.game_map
        
        # Get player position to prioritize rendering nearby tiles
        player_x, player_y = int(self.engine.player.x), int(self.engine.player.y)
        
        # Set render range (render 15 tiles around player)
        render_distance = 15
        min_x = max(0, player_x - render_distance)
        max_x = min(game_map.width, player_x + render_distance)
        min_y = max(0, player_y - render_distance)
        max_y = min(game_map.height, player_y + render_distance)
        
        # Draw all tiles with distinct colors for debugging
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                # Draw floor for all cells (blue)
                glPushMatrix()
                glTranslatef(float(x), -0.5, float(y))
                glColor3f(0.0, 0.0, 0.8)  # Bright blue for floor
                
                # Draw a flat square for the floor
                glBegin(GL_QUADS)
                glVertex3f(-0.5, 0.0, -0.5)
                glVertex3f(0.5, 0.0, -0.5)
                glVertex3f(0.5, 0.0, 0.5)
                glVertex3f(-0.5, 0.0, 0.5)
                glEnd()
                
                glPopMatrix()
                
                # Draw walls as big red cubes
                if game_map.tiles[x, y] == 1:  # Wall
                    glPushMatrix()
                    glTranslatef(float(x), 0.5, float(y))
                    glColor3f(1.0, 0.0, 0.0)  # Bright red for walls
                    
                    # Draw a cube
                    self._draw_debug_cube()
                    
                    glPopMatrix()
    
    def _draw_debug_cube(self):
        """Draw a simple cube without any lighting or textures."""
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        # Top face
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Bottom face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glEnd()
    
    def _render_entities(self):
        """Render all entities in the game."""
        # Sort entities by render order if they have it, otherwise render all of them
        entities = sorted(
            self.engine.active_entities,
            key=lambda x: getattr(x, 'render_order', 0) if hasattr(x, 'render_order') else 0
        )
        
        # Render all entities
        for entity in entities:
            self._render_entity(entity)
    
    def _render_entity(self, entity):
        """
        Render a single entity.
        
        Args:
            entity: The entity to render
        """
        glPushMatrix()
        glTranslatef(entity.x, 0.5, entity.y)  # Position at entity location, 1 unit tall
        
        # Choose a distinct color based on entity type
        if entity == self.engine.player:
            # Player is yellow
            glColor3f(1.0, 1.0, 0.0)
        elif entity.char == "o":  # Orc
            # Orcs are green
            glColor3f(0.0, 1.0, 0.0)
        elif entity.char == "T":  # Troll
            # Trolls are dark green
            glColor3f(0.0, 0.7, 0.0)
        elif entity.char == "!":  # Potion
            # Potions are magenta
            glColor3f(1.0, 0.0, 1.0)
        elif entity.char == "Z":  # Zombie
            # Zombies are cyan
            glColor3f(0.0, 1.0, 1.0)
        elif entity.char == "k":  # Kobold
            # Kobolds are orange
            glColor3f(1.0, 0.5, 0.0)
        elif entity.char == "/":  # Scroll
            # Scrolls are bright yellow
            glColor3f(1.0, 1.0, 0.3)
        elif entity.char == ")":  # Weapon
            # Weapons are light gray
            glColor3f(0.8, 0.8, 0.8)
        elif entity.char == "[":  # Armor
            # Armor is blue
            glColor3f(0.3, 0.3, 1.0)
        else:
            # All other entities are white
            glColor3f(1.0, 1.0, 1.0)
        
        # Draw a distinctive shape for the entity
        if entity == self.engine.player:
            # Draw player as a taller cube
            glScalef(0.5, 1.0, 0.5)
            self._draw_debug_cube()
        else:
            # Draw other entities as smaller colored cubes
            glScalef(0.3, 0.6, 0.3)
            self._draw_debug_cube()
        
        glPopMatrix()
    
    def _render_ui(self):
        """Render the user interface."""
        # Switch to orthographic projection for 2D UI
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth testing for UI elements
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Clear the HUD surface
        self.hud_surface.fill((0, 0, 0, 180))
        
        # Render HUD content
        self._render_health_bar()
        self._render_message_log()
        
        # Render inventory if shown
        if self.show_inventory:
            self._render_inventory()
        
        # Draw the HUD surface onto the screen
        scaled_surface = pygame.transform.scale(self.hud_surface, (self.width, self.height))
        surface_data = pygame.image.tostring(scaled_surface, "RGBA", True)
        
        glDrawPixels(self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, surface_data)
        
        # Re-enable depth testing and lighting
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        # Restore matrices
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def _render_health_bar(self):
        """Render the player's health bar."""
        player = self.engine.player
        
        # Use the fighter component from the player's components dictionary
        if "fighter" in player.components:
            fighter = player.components["fighter"]
            
            bar_width = 200
            bar_height = 20
            
            x = 10
            y = 10
            
            # Background
            pygame.draw.rect(self.hud_surface, (128, 0, 0), (x, y, bar_width, bar_height))
            
            # Health percentage
            health_pct = fighter.hp / fighter.max_hp
            fill_width = int(health_pct * bar_width)
            
            # Foreground
            pygame.draw.rect(self.hud_surface, (255, 0, 0), (x, y, fill_width, bar_height))
            
            # Text
            text = f"HP: {fighter.hp}/{fighter.max_hp}"
            text_surf = self.font.render(text, True, (255, 255, 255))
            self.hud_surface.blit(text_surf, (x + 5, y + 2))
    
    def _render_message_log(self):
        """Render the message log."""
        y = 40
        
        # Check if the engine has a message_log attribute
        if hasattr(self.engine, "message_log") and hasattr(self.engine.message_log, "messages"):
            # Render the last few messages
            for i, message in enumerate(self.engine.message_log.messages[-5:]):
                text_surf = self.font.render(message.full_text, True, message.color)
                self.hud_surface.blit(text_surf, (10, y + i * 20))
        else:
            # Render a static message if there's no message log
            text_surf = self.font.render("Welcome to Dungeon Descent 3D!", True, (255, 255, 255))
            self.hud_surface.blit(text_surf, (10, y))
    
    def _render_inventory(self):
        """Render the inventory screen."""
        # Semi-transparent background
        inventory_surf = pygame.Surface((400, 500), pygame.SRCALPHA)
        inventory_surf.fill((0, 0, 0, 220))
        
        # Title
        title = self.big_font.render("INVENTORY", True, (255, 255, 255))
        inventory_surf.blit(title, (10, 10))
        
        # Check if the player has an inventory component
        if "inventory" in self.engine.player.components:
            inventory = self.engine.player.components["inventory"]
            
            # Items
            y = 50
            if hasattr(inventory, "items") and inventory.items:
                for i, item in enumerate(inventory.items):
                    if item is not None:  # Skip None items
                        key = chr(ord('a') + i)
                        item_text = f"({key}) {item.name}"
                        text_surf = self.font.render(item_text, True, (255, 255, 255))
                        inventory_surf.blit(text_surf, (20, y + i * 25))
            else:
                text_surf = self.font.render("No items in inventory", True, (200, 200, 200))
                inventory_surf.blit(text_surf, (20, y))
        else:
            # No inventory component
            text_surf = self.font.render("No inventory available", True, (200, 200, 200))
            inventory_surf.blit(text_surf, (20, 50))
        
        # Exit instruction
        exit_text = "Press ESC to close inventory"
        text_surf = self.font.render(exit_text, True, (200, 200, 200))
        inventory_surf.blit(text_surf, (10, 450))
        
        # Center the inventory on screen
        x = (self.width - 400) // 2
        y = (self.height - 500) // 2
        self.hud_surface.blit(inventory_surf, (x, y))
    
    def toggle_view(self):
        """Toggle between first-person and third-person view."""
        self.first_person = not self.first_person
    
    def toggle_inventory(self):
        """Toggle the inventory display."""
        self.show_inventory = not self.show_inventory
    
    def load_textures(self):
        """Load textures for entities and environment."""
        self.textures = {}
        
        # Define texture paths and names
        texture_info = {
            "wall": "wall.png",
            "floor": "floor.png",
            "player": "player.png",
            "enemy": "enemy.png",
            "item": "item.png"
        }
        
        # Load each texture
        for name, file in texture_info.items():
            texture_path = os.path.join(os.path.dirname(__file__), "textures", file)
            
            # Try to load the texture - if it doesn't exist, create a placeholder
            try:
                if os.path.exists(texture_path):
                    texture_surface = pygame.image.load(texture_path)
                else:
                    # Create a placeholder texture
                    texture_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
                    if name == "wall":
                        texture_surface.fill((100, 100, 100))
                    elif name == "floor":
                        texture_surface.fill((50, 50, 50))
                    elif name == "player":
                        texture_surface.fill((0, 0, 200))
                    elif name == "enemy":
                        texture_surface.fill((200, 0, 0))
                    elif name == "item":
                        texture_surface.fill((200, 200, 0))
                    # Add a grid pattern for visibility
                    for i in range(0, 64, 8):
                        pygame.draw.line(texture_surface, (0, 0, 0), (i, 0), (i, 63), 1)
                        pygame.draw.line(texture_surface, (0, 0, 0), (0, i), (63, i), 1)
                
                # Convert to a format suitable for OpenGL
                texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
                width, height = texture_surface.get_size()
                
                # Generate texture ID
                texture_id = glGenTextures(1)
                
                # Bind and set up the texture
                glBindTexture(GL_TEXTURE_2D, texture_id)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
                
                # Store the texture ID
                self.textures[name] = texture_id
                
            except Exception as e:
                print(f"Error loading texture {name}: {e}")
                # In case of error, create a fallback texture
                self.textures[name] = None
    
    def cleanup(self):
        """Clean up resources when shutting down."""
        # Delete OpenGL textures
        for texture_id in self.textures.values():
            if texture_id is not None:
                glDeleteTextures(1, [texture_id])
        
        # Quit pygame
        pygame.quit()
    
    def handle_input(self):
        """
        Handle keyboard and mouse input.
        
        Returns:
            bool: False if the game should exit, True otherwise
        """
        # Get keyboard state
        keys = pygame.key.get_pressed()
        
        # Movement
        forward = keys[pygame.K_w] - keys[pygame.K_s]
        right = keys[pygame.K_d] - keys[pygame.K_a]
        self.camera.move(forward, right)
        
        # Mouse look
        if pygame.mouse.get_focused():
            dx, dy = pygame.mouse.get_rel()
            self.camera.rotate(dx, dy)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_TAB:
                    self.first_person = not self.first_person
                elif event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    pygame.mouse.set_visible(self.show_inventory)
                    pygame.event.set_grab(not self.show_inventory)
        
        return True 