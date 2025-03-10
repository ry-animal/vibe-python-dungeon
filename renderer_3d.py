import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from typing import Tuple, List, Dict, Set

class Camera:
    def __init__(self):
        # Position the camera at player position plus a small eye height
        self.position = [0, 0.8, 0]  # Eye height slightly below 1 unit (walls are 1 unit tall)
        self.rotation = [0, 0, 0]    # Start with no rotation
        self.move_speed = 0.2        # Slower movement for better control
        self.rotate_speed = 1.5      # Slightly less sensitive rotation
        
    def apply(self):
        """Apply camera transformation to the OpenGL matrix stack."""
        # Reset the view matrix
        glLoadIdentity()
        
        # Apply rotations
        glRotatef(self.rotation[0], 1, 0, 0)  # Pitch (around x-axis)
        glRotatef(self.rotation[1], 0, 1, 0)  # Yaw (around y-axis)
        glRotatef(self.rotation[2], 0, 0, 1)  # Roll (around z-axis)
        
        # Apply translation (negative because we're moving the world, not the camera)
        glTranslatef(-self.position[0], -self.position[1], -self.position[2])
    
    def move(self, direction: str):
        """Move camera in the specified direction."""
        # Convert rotation to radians
        yaw = math.radians(self.rotation[1])
        
        if direction == "forward":
            self.position[0] -= math.sin(yaw) * self.move_speed
            self.position[2] -= math.cos(yaw) * self.move_speed
        elif direction == "backward":
            self.position[0] += math.sin(yaw) * self.move_speed
            self.position[2] += math.cos(yaw) * self.move_speed
        elif direction == "left":
            self.position[0] -= math.cos(yaw) * self.move_speed
            self.position[2] += math.sin(yaw) * self.move_speed
        elif direction == "right":
            self.position[0] += math.cos(yaw) * self.move_speed
            self.position[2] -= math.sin(yaw) * self.move_speed
        elif direction == "up":
            self.position[1] += self.move_speed
        elif direction == "down":
            self.position[1] -= self.move_speed
    
    def rotate(self, dx: float, dy: float):
        """Rotate camera based on mouse movement."""
        self.rotation[1] += dx * self.rotate_speed
        self.rotation[0] += dy * self.rotate_speed
        
        # Limit pitch rotation to avoid flipping
        self.rotation[0] = max(-89, min(89, self.rotation[0]))
        
    def set_position_from_player(self, player_x, player_y):
        """Update camera position based on player position."""
        # Center the map
        map_center_x = self.engine.width / 2 if hasattr(self, 'engine') else 0
        map_center_z = self.engine.height / 2 if hasattr(self, 'engine') else 0
        
        # Convert player grid position to world coordinates
        world_x = player_x - map_center_x
        world_z = player_y - map_center_z
        
        # Set camera position, keeping current height
        self.position[0] = world_x
        self.position[2] = world_z

class RoguelikeGL:
    def __init__(self, engine, width=800, height=600):
        self.engine = engine
        self.width = width
        self.height = height
        self.camera = Camera()
        self.camera.engine = engine  # Give camera a reference to engine
        self.show_inventory = False
        self.first_person = True     # First-person view by default
        
        # Position camera at player's location initially
        if engine.player:
            map_center_x = engine.width / 2
            map_center_z = engine.height / 2
            player_world_x = engine.player.x - map_center_x
            player_world_z = engine.player.y - map_center_z
            self.camera.position[0] = player_world_x
            self.camera.position[2] = player_world_z
        
        # Colors
        self.colors = {
            "floor": (0.5, 0.5, 0.5),   # Gray
            "wall": (0.6, 0.3, 0.1),    # Brown
            "player": (0.0, 0.0, 1.0),  # Blue
            "kobold": (1.0, 0.0, 0.0),  # Red
            "rat": (0.8, 0.5, 0.2),     # Light brown
            "orc": (0.0, 0.7, 0.0),     # Green
            "zombie": (0.5, 0.8, 0.2),  # Greenish
            "troll": (0.8, 0.0, 0.8),   # Purple
            "potion": (0.0, 0.8, 0.8),  # Cyan
            "scroll": (0.8, 0.8, 0.0),  # Yellow
            "sword": (0.6, 0.6, 0.6),   # Silver
            "armor": (0.4, 0.4, 0.4)    # Dark Silver
        }
        
        # Animation properties
        self.animation_time = 0
        
        # Textures
        self.textures = {}
        
        # Initialize pygame and OpenGL
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), DOUBLEBUF|OPENGL)
        pygame.display.set_caption("Dungeon Descent 3D")
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # Clock for frame timing
        self.clock = pygame.time.Clock()
        
        # Setup OpenGL
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(75, (width/height), 0.1, 50.0)  # Wider FOV (75) for better visibility
        glMatrixMode(GL_MODELVIEW)
        
        # Setup fonts for HUD
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 18)
        self.big_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # HUD surface
        self.hud_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Enemy positions debug information
        self.debug_enemy_positions = []
        for entity in engine.active_entities:
            if entity != engine.player:
                self.debug_enemy_positions.append(
                    f"{entity.name} at ({entity.x}, {entity.y})"
                )
        
        # Enable features
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Setup light
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 1, 0, 0))  # Directional light from above
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.4, 0.4, 0.4, 1))  # Brighter ambient
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1))  # Slightly less intense diffuse
        
        # Enable fog for atmosphere (but less dense for better visibility)
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, (0.1, 0.1, 0.2, 1))  # Bluish fog
        glFogf(GL_FOG_DENSITY, 0.03)  # Less dense fog
        glFogi(GL_FOG_MODE, GL_EXP)   # Less aggressive fog falloff
        
    def draw_cube(self, position, color, size=1.0):
        """Draw a cube at the given position with the given color and size."""
        x, y, z = position
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(size, size, size)
        
        glColor3fv(color)
        
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
        
        glPopMatrix()
    
    def draw_floor_tile(self, x, z):
        """Draw a single floor tile at the given position."""
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
        
    def draw_item(self, position, item_type):
        """Draw an item at the given position."""
        x, y, z = position
        color = self.colors.get(item_type, self.colors["potion"])
        
        # Animate items - make them hover and rotate
        hover_offset = math.sin(self.animation_time * 2) * 0.1
        
        glPushMatrix()
        glTranslatef(x, y + hover_offset, z)
        glRotatef(self.animation_time * 30, 0, 1, 0)  # Rotate around y-axis
        
        if item_type == "potion":
            self.draw_potion(color)
        elif item_type == "scroll":
            self.draw_scroll(color)
        elif item_type == "sword":
            self.draw_sword(color)
        elif item_type == "armor":
            self.draw_armor(color)
        else:
            # Default item shape
            self.draw_cube((0, 0, 0), color, 0.4)
            
        glPopMatrix()
    
    def draw_potion(self, color):
        """Draw a potion bottle."""
        # Base
        glColor3fv(color)
        glPushMatrix()
        glScalef(0.2, 0.3, 0.2)
        self.draw_cylinder(8)
        glPopMatrix()
        
        # Neck
        glPushMatrix()
        glTranslatef(0, 0.3, 0)
        glScalef(0.1, 0.15, 0.1)
        self.draw_cylinder(8)
        glPopMatrix()
        
        # Cork
        glColor3f(0.6, 0.3, 0.1)  # Brown cork
        glPushMatrix()
        glTranslatef(0, 0.45, 0)
        glScalef(0.12, 0.1, 0.12)
        self.draw_cylinder(8)
        glPopMatrix()
    
    def draw_scroll(self, color):
        """Draw a scroll."""
        # Scroll paper
        glColor3fv(color)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glScalef(0.3, 0.3, 0.01)
        self.draw_cylinder(16)
        glPopMatrix()
        
        # Scroll handle (left)
        glColor3f(0.5, 0.3, 0.1)  # Wood color
        glPushMatrix()
        glTranslatef(-0.3, 0, 0)
        glRotatef(90, 0, 0, 1)
        glScalef(0.05, 0.05, 0.3)
        self.draw_cylinder(8)
        glPopMatrix()
        
        # Scroll handle (right)
        glPushMatrix()
        glTranslatef(0.3, 0, 0)
        glRotatef(90, 0, 0, 1)
        glScalef(0.05, 0.05, 0.3)
        self.draw_cylinder(8)
        glPopMatrix()
    
    def draw_sword(self, color):
        """Draw a sword."""
        # Blade
        glColor3fv(color)
        glPushMatrix()
        glTranslatef(0, 0.2, 0)
        glScalef(0.08, 0.4, 0.02)
        self.draw_cube((0, 0, 0), (1, 1, 1), 1.0)
        glPopMatrix()
        
        # Guard
        glColor3f(0.3, 0.3, 0.3)  # Darker metal
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glScalef(0.2, 0.05, 0.05)
        self.draw_cube((0, 0, 0), (1, 1, 1), 1.0)
        glPopMatrix()
        
        # Handle
        glColor3f(0.6, 0.3, 0.1)  # Brown wood
        glPushMatrix()
        glTranslatef(0, -0.15, 0)
        glScalef(0.05, 0.2, 0.05)
        self.draw_cube((0, 0, 0), (1, 1, 1), 1.0)
        glPopMatrix()
        
        # Pommel
        glColor3f(0.8, 0.8, 0.0)  # Gold
        glPushMatrix()
        glTranslatef(0, -0.3, 0)
        glScalef(0.08, 0.08, 0.08)
        self.draw_sphere(8)
        glPopMatrix()
    
    def draw_armor(self, color):
        """Draw a piece of armor."""
        # Chest plate
        glColor3fv(color)
        glPushMatrix()
        glScalef(0.3, 0.4, 0.15)
        self.draw_cube((0, 0, 0), (1, 1, 1), 1.0)
        glPopMatrix()
        
        # Shoulders
        glPushMatrix()
        glTranslatef(-0.25, 0.1, 0)
        glScalef(0.1, 0.1, 0.1)
        self.draw_sphere(8)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.25, 0.1, 0)
        glScalef(0.1, 0.1, 0.1)
        self.draw_sphere(8)
        glPopMatrix()
    
    def draw_cylinder(self, segments):
        """Draw a cylinder centered at origin."""
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
        """Draw a sphere centered at origin."""
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

    def render_hud(self):
        """Render the HUD overlay."""
        # Clear the HUD surface
        self.hud_surface.fill((0, 0, 0, 0))
        
        # Draw player stats if player exists
        if self.engine.player and "fighter" in self.engine.player.components:
            fighter = self.engine.player.components["fighter"]
            
            # Player health bar
            health_text = f"HP: {fighter.hp}/{fighter.max_hp}"
            health_surface = self.font.render(health_text, True, (255, 255, 255))
            
            # Health bar background
            bar_width = 200
            pygame.draw.rect(self.hud_surface, (80, 80, 80), (20, 20, bar_width, 20))
            
            # Health bar fill
            health_percent = fighter.hp / fighter.max_hp
            fill_width = int(bar_width * health_percent)
            fill_color = (0, 255, 0) if health_percent > 0.5 else (255, 255, 0) if health_percent > 0.25 else (255, 0, 0)
            pygame.draw.rect(self.hud_surface, fill_color, (20, 20, fill_width, 20))
            
            # Draw health text
            self.hud_surface.blit(health_surface, (25, 22))
            
            # Player stats
            stats_text = f"Power: {fighter.power}  Defense: {fighter.defense}"
            stats_surface = self.font.render(stats_text, True, (255, 255, 255))
            self.hud_surface.blit(stats_surface, (20, 50))
            
            # Player position
            pos_text = f"Position: ({self.engine.player.x}, {self.engine.player.y})"
            pos_surface = self.font.render(pos_text, True, (200, 200, 200))
            self.hud_surface.blit(pos_surface, (20, 75))
            
            # Instructions
            instr_text = "Arrow keys: Move | WASD: Camera | I: Inventory | Esc: Quit"
            instr_surface = self.font.render(instr_text, True, (180, 180, 180))
            self.hud_surface.blit(instr_surface, (20, self.height - 30))
        
        # Draw minimap
        self.render_minimap()
        
        # Draw compass
        compass_center = (self.width - 70, 70)
        compass_radius = 50
        # Draw compass circle
        pygame.draw.circle(self.hud_surface, (50, 50, 50, 180), compass_center, compass_radius)
        pygame.draw.circle(self.hud_surface, (200, 200, 200), compass_center, compass_radius, 2)
        
        # Draw compass directions
        directions = [
            ("N", 0, -1, (255, 255, 255)), 
            ("E", 1, 0, (255, 255, 255)),
            ("S", 0, 1, (255, 255, 255)), 
            ("W", -1, 0, (255, 255, 255))
        ]
        
        # Get camera yaw in radians (0 = north, increasing clockwise)
        camera_yaw = math.radians(self.camera.rotation[1])
        
        for label, dx, dy, color in directions:
            # Calculate angle for this direction
            dir_angle = math.atan2(dx, -dy)  # Convert to OpenGL coordinate system
            
            # Adjust for camera rotation
            adjusted_angle = dir_angle - camera_yaw
            
            # Calculate position on compass
            x = compass_center[0] + math.sin(adjusted_angle) * (compass_radius - 15)
            y = compass_center[1] + math.cos(adjusted_angle) * (compass_radius - 15)
            
            # Draw direction label
            label_surface = self.font.render(label, True, color)
            label_rect = label_surface.get_rect(center=(x, y))
            self.hud_surface.blit(label_surface, label_rect)
        
        # Draw crosshair
        crosshair_size = 10
        pygame.draw.line(self.hud_surface, (255, 255, 255), 
                         (self.width // 2 - crosshair_size, self.height // 2),
                         (self.width // 2 + crosshair_size, self.height // 2), 2)
        pygame.draw.line(self.hud_surface, (255, 255, 255), 
                         (self.width // 2, self.height // 2 - crosshair_size),
                         (self.width // 2, self.height // 2 + crosshair_size), 2)
        
        # Draw debug information about enemies
        if len(self.debug_enemy_positions) > 0:
            debug_y = 100
            debug_title = self.font.render("Enemies in dungeon:", True, (255, 200, 200))
            self.hud_surface.blit(debug_title, (20, debug_y))
            
            for i, enemy_info in enumerate(self.debug_enemy_positions[:5]):  # Show first 5 enemies only
                debug_y += 20
                enemy_surface = self.font.render(enemy_info, True, (200, 150, 150))
                self.hud_surface.blit(enemy_surface, (30, debug_y))
            
            if len(self.debug_enemy_positions) > 5:
                more_text = f"... and {len(self.debug_enemy_positions) - 5} more"
                more_surface = self.font.render(more_text, True, (200, 150, 150))
                self.hud_surface.blit(more_surface, (30, debug_y + 20))
        
        # Blit HUD surface to screen
        self.screen.blit(self.hud_surface, (0, 0))

    def render_minimap(self):
        """Render a minimap in the corner of the screen."""
        mm_size = 120  # Size of minimap
        mm_x = self.width - mm_size - 20  # Position in bottom right
        mm_y = self.height - mm_size - 20
        cell_size = 4  # Size of each map cell
        
        # Draw minimap background
        pygame.draw.rect(self.hud_surface, (0, 0, 0, 180), (mm_x, mm_y, mm_size, mm_size))
        pygame.draw.rect(self.hud_surface, (100, 100, 100), (mm_x, mm_y, mm_size, mm_size), 1)
        
        # Calculate visible map portion centered on player
        visible_cells = mm_size // cell_size
        half_cells = visible_cells // 2
        
        # Get player position (or center if no player)
        if self.engine.player:
            center_x = self.engine.player.x
            center_y = self.engine.player.y
        else:
            center_x = self.engine.width // 2
            center_y = self.engine.height // 2
        
        # Calculate map boundaries
        start_x = max(0, center_x - half_cells)
        end_x = min(self.engine.width, center_x + half_cells)
        start_y = max(0, center_y - half_cells)
        end_y = min(self.engine.height, center_y + half_cells)
        
        # Draw map cells
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Calculate minimap position
                mm_cell_x = mm_x + (x - start_x) * cell_size
                mm_cell_y = mm_y + (y - start_y) * cell_size
                
                # Draw walls
                if self.engine.game_map[x, y] == 1:
                    pygame.draw.rect(self.hud_surface, (150, 75, 0), 
                                    (mm_cell_x, mm_cell_y, cell_size, cell_size))
                else:
                    pygame.draw.rect(self.hud_surface, (50, 50, 50), 
                                    (mm_cell_x, mm_cell_y, cell_size, cell_size))
        
        # Draw entities on minimap
        for entity in self.engine.active_entities:
            # Skip entities outside visible range
            if not (start_x <= entity.x < end_x and start_y <= entity.y < end_y):
                continue
            
            # Calculate minimap position
            mm_entity_x = mm_x + (entity.x - start_x) * cell_size + cell_size // 2
            mm_entity_y = mm_y + (entity.y - start_y) * cell_size + cell_size // 2
            
            # Determine color
            if entity == self.engine.player:
                color = (0, 0, 255)  # Blue for player
                size = 3
            elif entity.name.lower() in ["potion", "scroll", "sword", "armor"]:
                color = (0, 255, 255)  # Cyan for items
                size = 2
            else:
                color = (255, 0, 0)  # Red for enemies
                size = 2
            
            # Draw entity dot
            pygame.draw.circle(self.hud_surface, color, (mm_entity_x, mm_entity_y), size)

    def render_inventory(self):
        """Render the inventory screen."""
        if not self.show_inventory or "inventory" not in self.engine.player.components:
            return
            
        inventory = self.engine.player.components["inventory"]
        
        # Darken the background
        dark_overlay = pygame.Surface((self.width, self.height))
        dark_overlay.fill((0, 0, 0))
        dark_overlay.set_alpha(150)
        self.screen.blit(dark_overlay, (0, 0))
        
        # Draw inventory panel
        panel_width = self.width * 0.6
        panel_height = self.height * 0.7
        panel_x = (self.width - panel_width) / 2
        panel_y = (self.height - panel_height) / 2
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height))
        panel.fill((50, 40, 30))
        pygame.draw.rect(panel, (100, 80, 60), (0, 0, panel_width, panel_height), 4)
        
        # Title
        title = self.big_font.render("INVENTORY", True, (255, 255, 255))
        panel.blit(title, ((panel_width - title.get_width()) / 2, 20))
        
        # Draw items
        item_spacing = 40
        start_y = 70
        
        for i, item in enumerate(inventory.items):
            if item is None:
                continue
                
            # Item slot (A-Z)
            slot_letter = chr(65 + i)  # ASCII A-Z
            letter_surface = self.font.render(f"{slot_letter})", True, (255, 255, 255))
            panel.blit(letter_surface, (40, start_y + i * item_spacing))
            
            # Item name
            name_surface = self.font.render(item.name, True, pygame.Color(*item.color))
            panel.blit(name_surface, (80, start_y + i * item_spacing))
            
            # Use/Equip/Drop text
            action_text = "Use" if item.name in ["Potion", "Scroll"] else "Equip"
            action_surface = self.font.render(f"[{action_text}]", True, (150, 150, 150))
            panel.blit(action_surface, (panel_width - 80, start_y + i * item_spacing))
        
        # Instructions
        instructions = self.font.render("Press letter to use/equip, ESC to close", True, (200, 200, 200))
        panel.blit(instructions, ((panel_width - instructions.get_width()) / 2, panel_height - 40))
        
        # Blit panel to screen
        self.screen.blit(panel, (panel_x, panel_y))

    def render(self):
        """Render the 3D scene."""
        # Update animation time
        self.animation_time += 0.01
        
        # Update camera position based on player position
        if self.engine.player and self.first_person:
            map_center_x = self.engine.width / 2
            map_center_z = self.engine.height / 2
            player_world_x = self.engine.player.x - map_center_x
            player_world_z = self.engine.player.y - map_center_z
            
            # Set camera position to player position
            self.camera.position[0] = player_world_x
            self.camera.position[2] = player_world_z
        
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Apply camera transformation
        self.camera.apply()
        
        # Center the map
        map_center_x = self.engine.width / 2
        map_center_z = self.engine.height / 2
        
        # Calculate visible area for performance optimization
        # Only render what's visible (roughly)
        view_distance = 15  # Units to render in each direction
        player_x = self.engine.player.x if self.engine.player else 0
        player_y = self.engine.player.y if self.engine.player else 0
        
        min_x = max(0, player_x - view_distance)
        max_x = min(self.engine.width, player_x + view_distance)
        min_y = max(0, player_y - view_distance)
        max_y = min(self.engine.height, player_y + view_distance)
        
        # Draw floor and walls (only within view distance)
        for z in range(min_y, max_y):
            for x in range(min_x, max_x):
                # Convert to OpenGL coordinates (centered at origin)
                gl_x = x - map_center_x
                gl_z = z - map_center_z
                
                # Skip rendering if too far from player
                dx = x - player_x
                dz = z - player_y
                if dx*dx + dz*dz > view_distance*view_distance:
                    continue
                    
                if self.engine.game_map[x, z] == 1:  # Wall
                    self.draw_cube((gl_x, 0, gl_z), self.colors["wall"])
                else:  # Floor
                    self.draw_floor_tile(gl_x, gl_z)
        
        # Draw entities (only within view distance)
        for entity in self.engine.active_entities:
            # Skip rendering entities too far away
            dx = entity.x - player_x
            dy = entity.y - player_y
            if dx*dx + dy*dy > view_distance*view_distance:
                continue
            
            # Convert to OpenGL coordinates
            gl_x = entity.x - map_center_x
            gl_z = entity.y - map_center_z  # Note: entity.y is the row in the map (z in OpenGL)
            
            # Skip drawing the player in first-person mode
            if entity == self.engine.player and self.first_person:
                continue
            
            # Determine entity color and visualization
            if entity == self.engine.player:
                # Draw player model
                color = self.colors["player"]
                self.draw_cube((gl_x, 0.5, gl_z), color, 0.8)
            elif entity.name.lower() in ["potion", "scroll", "sword", "armor"]:
                # Draw item
                self.draw_item((gl_x, 0.5, gl_z), entity.name.lower())
            else:
                # Draw enemy
                color = self.colors.get(entity.name.lower(), self.colors["kobold"])
                self.draw_cube((gl_x, 0.5, gl_z), color, 0.8)
        
        # Draw weapon in first-person view
        if self.first_person:
            self.draw_first_person_weapon()
        
        # Render HUD
        self.render_hud()
        
        # Render inventory if open
        self.render_inventory()
        
        # Limit frame rate
        self.clock.tick(60)
            
        # Swap buffers
        pygame.display.flip()

    def draw_first_person_weapon(self):
        """Draw a weapon/hand model in first-person view."""
        # Save the modelview matrix
        glPushMatrix()
        
        # Reset the view
        glLoadIdentity()
        
        # Apply weapon position and rotation
        # Weapon should be in the bottom right of the screen
        glTranslatef(0.5, -0.3, -1.0)  # Position in front of camera
        
        # Add slight bobbing for walking effect
        bob_amount = math.sin(self.animation_time * 3) * 0.02
        glTranslatef(0, bob_amount, 0)
        
        # Add slight rotation animation
        glRotatef(math.sin(self.animation_time) * 2, 0, 1, 0)
        
        # Scale the weapon
        glScalef(0.2, 0.2, 0.2)
        
        # Draw the weapon (simple sword)
        # Draw sword
        self.draw_sword(self.colors["sword"])
        
        # Restore the modelview matrix
        glPopMatrix()

    def handle_input(self):
        """Handle keyboard and mouse input for camera control."""
        # Handle mouse movement for camera rotation
        if pygame.mouse.get_focused() and not self.show_inventory:
            # Get relative mouse movement
            dx, dy = pygame.mouse.get_rel()
            if dx != 0 or dy != 0:
                self.camera.rotate(dx * 0.1, -dy * 0.1)  # Invert y-axis
        
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Camera movement (only when inventory is closed)
        if not self.show_inventory:
            # Directional movement using WASD
            move_dir = None
            
            # Simple cardinal direction movement based on camera orientation
            # Forward is the direction the camera is mainly pointing
            yaw = self.camera.rotation[1] % 360
            
            # Determine primary direction based on camera yaw
            if keys[K_w]:  # Forward
                # Forward depends on which direction we're facing
                if 45 <= yaw < 135:  # Facing right
                    move_dir = (1, 0)  # Move right
                elif 135 <= yaw < 225:  # Facing back
                    move_dir = (0, 1)  # Move down
                elif 225 <= yaw < 315:  # Facing left
                    move_dir = (-1, 0)  # Move left
                else:  # Facing forward
                    move_dir = (0, -1)  # Move up
            elif keys[K_s]:  # Backward (opposite of forward)
                if 45 <= yaw < 135:  # Facing right
                    move_dir = (-1, 0)  # Move left
                elif 135 <= yaw < 225:  # Facing back
                    move_dir = (0, -1)  # Move up
                elif 225 <= yaw < 315:  # Facing left
                    move_dir = (1, 0)  # Move right
                else:  # Facing forward
                    move_dir = (0, 1)  # Move down
            elif keys[K_a]:  # Left (90 degrees counter-clockwise from forward)
                if 45 <= yaw < 135:  # Facing right
                    move_dir = (0, -1)  # Move up
                elif 135 <= yaw < 225:  # Facing back
                    move_dir = (-1, 0)  # Move left
                elif 225 <= yaw < 315:  # Facing left
                    move_dir = (0, 1)  # Move down
                else:  # Facing forward
                    move_dir = (-1, 0)  # Move left
            elif keys[K_d]:  # Right (90 degrees clockwise from forward)
                if 45 <= yaw < 135:  # Facing right
                    move_dir = (0, 1)  # Move down
                elif 135 <= yaw < 225:  # Facing back
                    move_dir = (1, 0)  # Move right
                elif 225 <= yaw < 315:  # Facing left
                    move_dir = (0, -1)  # Move up
                else:  # Facing forward
                    move_dir = (1, 0)  # Move right
            
            # Apply movement to player if a direction was selected
            if move_dir:
                move_x, move_y = move_dir
                self.engine.move_player(move_x, move_y)
                self.engine.update()

        # Process individual events
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.show_inventory:
                        self.show_inventory = False
                    else:
                        return False
                elif event.key == K_i:  # Toggle inventory
                    self.show_inventory = not self.show_inventory
                    pygame.mouse.set_visible(self.show_inventory)
                    pygame.event.set_grab(not self.show_inventory)
                elif event.key == K_v:  # Toggle first/third person view
                    self.first_person = not self.first_person
                    # Reset camera position
                    if self.engine.player:
                        map_center_x = self.engine.width / 2
                        map_center_z = self.engine.height / 2
                        player_world_x = self.engine.player.x - map_center_x
                        player_world_z = self.engine.player.y - map_center_z
                        
                        if self.first_person:
                            self.camera.position[0] = player_world_x
                            self.camera.position[1] = 0.8  # Eye height
                            self.camera.position[2] = player_world_z
                        else:
                            # Third person camera behind player
                            self.camera.position[0] = player_world_x
                            self.camera.position[1] = 5  # Higher viewpoint
                            self.camera.position[2] = player_world_z + 5  # Behind player
                            self.camera.rotation[0] = 30  # Look down at player
                elif self.show_inventory and 97 <= event.key <= 122:  # Letters a-z
                    # Use/equip item
                    item_index = event.key - 97  # Convert ASCII to 0-25
                    self.use_item(item_index)
                elif not self.show_inventory:
                    # Game controls (arrow keys for player movement)
                    if event.key == K_UP:
                        self.engine.move_player(0, -1)
                        self.engine.update()
                    elif event.key == K_DOWN:
                        self.engine.move_player(0, 1)
                        self.engine.update()
                    elif event.key == K_LEFT:
                        self.engine.move_player(-1, 0)
                        self.engine.update()
                    elif event.key == K_RIGHT:
                        self.engine.move_player(1, 0)
                        self.engine.update()
                
        return True
    
    def use_item(self, item_index):
        """Use or equip an item from the inventory."""
        if "inventory" not in self.engine.player.components:
            return
            
        inventory = self.engine.player.components["inventory"]
        if item_index >= len(inventory.items) or inventory.items[item_index] is None:
            return
            
        item = inventory.items[item_index]
        print(f"Using {item.name}...")
        
        # Implement effects based on item type
        if item.name == "Potion":
            # Heal the player
            if "fighter" in self.engine.player.components:
                fighter = self.engine.player.components["fighter"]
                heal_amount = 10
                fighter.hp = min(fighter.max_hp, fighter.hp + heal_amount)
                print(f"You healed for {heal_amount} HP!")
                inventory.items[item_index] = None  # Remove consumed item
        elif item.name == "Scroll":
            # Cast a fireball (damage enemies in range)
            for entity in self.engine.active_entities:
                if entity != self.engine.player and "fighter" in entity.components:
                    # Calculate distance
                    dx = abs(entity.x - self.engine.player.x)
                    dy = abs(entity.y - self.engine.player.y)
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance <= 3:  # 3-tile radius
                        # Damage formula: 10 damage at center, decreasing with distance
                        damage = max(1, int(10 - distance * 3))
                        entity.components["fighter"].take_damage(damage)
                        print(f"The fireball hits {entity.name} for {damage} damage!")
                        
                        if entity.components["fighter"].hp <= 0:
                            print(f"You killed {entity.name}!")
                            self.engine.active_entities.remove(entity)
            
            inventory.items[item_index] = None  # Remove consumed item
        elif item.name == "Sword":
            # Equip sword (increase power)
            if "fighter" in self.engine.player.components:
                fighter = self.engine.player.components["fighter"]
                fighter.power += 2
                print("You equip the sword. Power increased by 2!")
                inventory.items[item_index] = None  # Remove equipped item
        elif item.name == "Armor":
            # Equip armor (increase defense)
            if "fighter" in self.engine.player.components:
                fighter = self.engine.player.components["fighter"]
                fighter.defense += 2
                print("You equip the armor. Defense increased by 2!")
                inventory.items[item_index] = None  # Remove equipped item 