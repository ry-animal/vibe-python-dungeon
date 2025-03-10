"""
Simplified 3D renderer module using PyOpenGL.
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
from .primitives import (
    draw_cube, draw_floor_tile, draw_wireframe_cube,
    draw_wireframe_grid, draw_axes, draw_cylinder, draw_sphere
)
from .lighting import (
    setup_lighting, setup_torch_lighting, disable_torch_lighting,
    setup_fog, disable_fog
)
from .textures import TextureManager, enable_texturing, disable_texturing


class RoguelikeGL:
    """
    3D renderer for the roguelike game using OpenGL.
    
    This is a simplified version of the main renderer that uses
    modular components for drawing primitives, lighting, and textures.
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
        
        # Initialize rendering options
        self.use_fog = False
        self.wireframe_mode = False
        self.show_minimap = True
        self.show_inventory = False
        self.first_person = False
        self.show_hud = True
        self.debug_mode = True
        
        # Initialize Pygame with OpenGL
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Dungeon Descent 3D")
        
        # Initialize camera
        self.camera = Camera()
        self.camera.position = [0.0, 10.0, 0.0]
        self.camera.target = [0.0, 0.0, 0.0]
        
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
        self.animation_time = 0.0
        
        # Initialize texture manager
        self.texture_manager = TextureManager()
        
        # For smooth mouse movement
        pygame.mouse.set_visible(False)  # Hide the mouse cursor
        pygame.mouse.set_pos(width // 2, height // 2)
        self.mouse_x, self.mouse_y = width // 2, height // 2
        
    def _setup_opengl(self):
        """Set up the OpenGL state."""
        # Set the viewport
        glViewport(0, 0, self.width, self.height)
        
        # Set up the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 100.0)
        
        # Set up the modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Enable backface culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Enable lighting
        setup_lighting()
        
        # Set up fog if enabled
        if self.use_fog:
            setup_fog()
        
        # Set the clear color (sky color)
        glClearColor(0.1, 0.1, 0.2, 1.0)
    
    def toggle_wireframe(self):
        """Toggle wireframe rendering mode."""
        self.wireframe_mode = not self.wireframe_mode
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    def render(self):
        """Render the scene using OpenGL."""
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Reset the modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Apply the camera transform based on view mode
        if self.first_person:
            self.camera.apply_first_person()
        else:
            # In third-person mode, set the camera target to the player position
            player_x, player_y = self.engine.player.position
            self.camera.target = [player_x, 0.0, player_y]
            self.camera.apply_third_person()
        
        # Draw coordinate axes for debugging
        if self.debug_mode:
            draw_axes()
        
        # Render the dungeon
        self._render_dungeon()
        
        # Render entities (player, enemies, items)
        self._render_entities()
        
        # Draw the HUD
        if self.show_hud:
            self._render_hud()
        
        # Render inventory if open
        if self.show_inventory:
            self._render_inventory()
        
        # Update the display
        pygame.display.flip()
    
    def _render_dungeon(self):
        """Render the dungeon walls and floor."""
        # Get the dungeon map
        dungeon = self.engine.game_map
        
        # Only render what's near the player
        player_x, player_y = self.engine.player.position
        render_distance = 15  # How far to render in each direction
        
        # Calculate the visible bounds
        min_x = max(0, player_x - render_distance)
        max_x = min(dungeon.width, player_x + render_distance)
        min_y = max(0, player_y - render_distance)
        max_y = min(dungeon.height, player_y + render_distance)
        
        # Draw the floor grid first
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                draw_floor_tile(x, y, self.colors['floor'])
        
        # Draw walls
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                # In our simplified map, 1 = wall, 0 = floor
                if dungeon.tiles[x, y] == 1:
                    if self.wireframe_mode:
                        draw_wireframe_cube(x, 0.0, y)
                    else:
                        draw_cube((x, 0.0, y), self.colors['wall'])
    
    def _render_entities(self):
        """Render the player, enemies, and items."""
        # Draw the player
        player = self.engine.player
        if not self.first_person:  # Don't render player in first-person mode
            draw_cube((player.position[0], 0.0, player.position[1]), self.colors['player'], 0.8)
        
        # Draw enemies
        for entity in self.engine.game_map.enemies:
            color = self.colors.get(entity.name.lower(), self.colors['default'])
            draw_cube((entity.position[0], 0.0, entity.position[1]), color, 0.8)
        
        # Draw items
        for entity in self.engine.game_map.items:
            color = self.colors.get(entity.name.lower(), self.colors['default'])
            if entity.name.lower() == 'potion':
                draw_cylinder((entity.position[0], -0.25, entity.position[1]), color, 0.25, 0.5)
            elif entity.name.lower() == 'scroll':
                # Draw a small cylinder for scrolls
                draw_cylinder((entity.position[0], -0.25, entity.position[1]), color, 0.2, 0.1)
            else:
                # Default item representation
                draw_sphere((entity.position[0], -0.25, entity.position[1]), color, 0.25)
    
    def _render_hud(self):
        """Render the HUD with player information."""
        # Clear the HUD surface
        self.hud_surface.fill((0, 0, 0, 0))
        
        # Render player stats
        player = self.engine.player
        health_text = f"HP: {player.fighter.hp}/{player.fighter.max_hp}"
        attack_text = f"Attack: {player.fighter.power}"
        defense_text = f"Defense: {player.fighter.defense}"
        
        # Render the texts
        health_surface = self.font.render(health_text, True, (255, 0, 0))
        attack_surface = self.font.render(attack_text, True, (255, 255, 255))
        defense_surface = self.font.render(defense_text, True, (255, 255, 255))
        
        # Position the texts on the HUD
        self.hud_surface.blit(health_surface, (10, 10))
        self.hud_surface.blit(attack_surface, (10, 40))
        self.hud_surface.blit(defense_surface, (10, 70))
        
        # If there are messages to display, show them
        if self.engine.message_log:
            y_offset = self.height - 100
            for i, message in enumerate(self.engine.message_log.messages[-5:]):
                msg_surface = self.font.render(message.full_text, True, (255, 255, 255))
                self.hud_surface.blit(msg_surface, (10, y_offset + i * 20))
        
        # Draw a small map in the corner if enabled
        if self.show_minimap:
            self._render_minimap()
        
        # Display the HUD
        temp_surface = self.hud_surface.convert_alpha()
        pygame_surface = pygame.display.get_surface()
        pygame_surface.blit(temp_surface, (0, 0))
    
    def _render_minimap(self):
        """Render a small minimap in the corner of the screen."""
        minimap_size = 150
        minimap_pos = (self.width - minimap_size - 10, 10)
        
        # Create a small surface for the minimap
        minimap = pygame.Surface((minimap_size, minimap_size))
        minimap.fill((0, 0, 0))
        
        # Get the dungeon map
        dungeon = self.engine.game_map
        player_x, player_y = self.engine.player.position
        
        # Calculate the scale factor and offset
        scale = minimap_size / max(dungeon.width, dungeon.height)
        scale = min(scale, 3.0)  # Limit the scale to prevent tiny maps
        
        # Calculate the center of the minimap
        center_x = minimap_size // 2
        center_y = minimap_size // 2
        
        # Calculate the offset to center the player
        offset_x = center_x - int(player_x * scale)
        offset_y = center_y - int(player_y * scale)
        
        # Draw the walls
        for y in range(dungeon.height):
            for x in range(dungeon.width):
                px = int(x * scale) + offset_x
                py = int(y * scale) + offset_y
                
                # Skip if outside minimap
                if px < 0 or px >= minimap_size or py < 0 or py >= minimap_size:
                    continue
                
                if dungeon.tiles[x, y].is_wall:
                    minimap.set_at((px, py), (100, 100, 100))
                else:
                    minimap.set_at((px, py), (50, 50, 50))
        
        # Draw the entities
        for entity in self.engine.game_map.enemies:
            px = int(entity.position[0] * scale) + offset_x
            py = int(entity.position[1] * scale) + offset_y
            if 0 <= px < minimap_size and 0 <= py < minimap_size:
                minimap.set_at((px, py), (255, 0, 0))
        
        # Draw the player
        px = int(player_x * scale) + offset_x
        py = int(player_y * scale) + offset_y
        if 0 <= px < minimap_size and 0 <= py < minimap_size:
            # Draw a 3x3 player marker
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < minimap_size and 0 <= ny < minimap_size:
                        minimap.set_at((nx, ny), (0, 255, 0))
        
        # Add the minimap to the HUD
        self.hud_surface.blit(minimap, minimap_pos)
    
    def _render_inventory(self):
        """Render the player's inventory."""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Title
        title_surface = self.big_font.render("Inventory", True, (255, 255, 255))
        overlay.blit(title_surface, (self.width // 2 - title_surface.get_width() // 2, 50))
        
        # Render inventory items
        y_offset = 100
        for i, item in enumerate(self.engine.player.inventory.items):
            key = chr(ord('a') + i)
            item_text = f"{key}) {item.name}"
            item_surface = self.font.render(item_text, True, (255, 255, 255))
            overlay.blit(item_surface, (self.width // 2 - 100, y_offset))
            y_offset += 30
        
        # Display instructions
        instructions = "Press ESC to close inventory. Press letter to use item."
        instr_surface = self.font.render(instructions, True, (200, 200, 200))
        overlay.blit(instr_surface, (self.width // 2 - instr_surface.get_width() // 2, self.height - 50))
        
        # Blit the overlay to the screen
        pygame_surface = pygame.display.get_surface()
        pygame_surface.blit(overlay, (0, 0))
    
    def handle_input(self):
        """Handle user input for the renderer."""
        # Get mouse movement for camera rotation
        new_mouse_x, new_mouse_y = pygame.mouse.get_pos()
        mouse_dx = new_mouse_x - self.mouse_x
        mouse_dy = new_mouse_y - self.mouse_y
        
        # Adjust the camera based on mouse movement
        if mouse_dx != 0 or mouse_dy != 0:
            self.camera.rotate(mouse_dx * 0.2, mouse_dy * 0.2)
            
            # Reset mouse position to center
            pygame.mouse.set_pos(self.width // 2, self.height // 2)
            self.mouse_x, self.mouse_y = self.width // 2, self.height // 2
        
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        forward = 0
        right = 0
        
        # Movement
        if keys[K_w]:
            forward += 0.1
        if keys[K_s]:
            forward -= 0.1
        if keys[K_a]:
            right -= 0.1
        if keys[K_d]:
            right += 0.1
        
        # Apply camera movement
        if forward != 0 or right != 0:
            self.camera.move(forward, right)
            
            # Update player position based on camera if in first-person mode
            if self.first_person:
                # Convert 3D position to 2D grid position
                new_x = int(round(self.camera.position[0]))
                new_y = int(round(self.camera.position[2]))  # Z in 3D is Y in 2D
                
                # Only move if the new position is valid
                if not self.engine.game_map.is_blocked(new_x, new_y):
                    self.engine.player.position = (new_x, new_y)
        
        # Toggle wireframe mode
        if keys[K_f]:
            self.toggle_wireframe()
        
        # Toggle first/third person
        if keys[K_v]:
            self.first_person = not self.first_person
            
            # If switching to first person, move camera to player
            if self.first_person:
                px, py = self.engine.player.position
                self.camera.position = [px, 0.5, py]
        
        # Toggle minimap
        if keys[K_m]:
            self.show_minimap = not self.show_minimap
        
        # Toggle inventory
        if keys[K_i]:
            self.show_inventory = not self.show_inventory
        
        # Process pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.show_inventory:
                        self.show_inventory = False
                    else:
                        return False
                    
                # Use inventory items
                if self.show_inventory and ord('a') <= event.key <= ord('z'):
                    index = event.key - ord('a')
                    if index < len(self.engine.player.inventory.items):
                        self.engine.player.inventory.use(index)
                        self.show_inventory = False
        
        return True
    
    def cleanup(self):
        """Clean up resources."""
        # Cleanup textures
        self.texture_manager.cleanup()
        pygame.quit() 