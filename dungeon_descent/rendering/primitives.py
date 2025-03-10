"""
Primitive drawing functions for 3D rendering.
"""
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


def draw_cube(position, color, size=1.0):
    """
    Draw a cube at the given position with the given color and size.
    
    Args:
        position: (x, y, z) position
        color: (r, g, b) color
        size: Size multiplier
    """
    x, y, z = position
    
    # Make sure color intensity is high enough to be visible
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


def draw_floor_tile(x, z, color=(0.4, 0.4, 0.4)):
    """
    Draw a flat floor tile at the given position.
    
    Args:
        x: X position
        z: Z position
        color: RGB color tuple
    """
    glPushMatrix()
    glTranslatef(x, -0.5, z)
    
    glColor3fv(color)
    
    # Draw a simple quad for the floor
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)  # Normal pointing up
    glVertex3f(-0.5, 0, -0.5)
    glVertex3f(0.5, 0, -0.5)
    glVertex3f(0.5, 0, 0.5)
    glVertex3f(-0.5, 0, 0.5)
    glEnd()
    
    glPopMatrix()


def draw_cylinder(position, color, radius=0.5, height=1.0, segments=12):
    """
    Draw a cylinder at the given position.
    
    Args:
        position: (x, y, z) position
        color: (r, g, b) color
        radius: Radius of the cylinder
        height: Height of the cylinder
        segments: Number of segments for the cylinder
    """
    x, y, z = position
    
    # Ensure color is visible
    color_r, color_g, color_b = color
    color_r = max(0.4, color_r)
    color_g = max(0.4, color_g)
    color_b = max(0.4, color_b)
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    glColor3f(color_r, color_g, color_b)
    
    # Bottom face (circle)
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, -1, 0)  # Normal pointing down
    glVertex3f(0, -height/2, 0)  # Center
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        glVertex3f(radius * math.cos(angle), -height/2, radius * math.sin(angle))
    glEnd()
    
    # Top face (circle)
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 1, 0)  # Normal pointing up
    glVertex3f(0, height/2, 0)  # Center
    for i in range(segments + 1):
        angle = 2.0 * math.pi * (segments - i) / segments  # Reverse order for normal direction
        glVertex3f(radius * math.cos(angle), height/2, radius * math.sin(angle))
    glEnd()
    
    # Side faces (cylinder wall)
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        c = math.cos(angle)
        s = math.sin(angle)
        
        # Normal points outward
        glNormal3f(c, 0, s)
        
        glVertex3f(radius * c, -height/2, radius * s)
        glVertex3f(radius * c, height/2, radius * s)
    glEnd()
    
    glPopMatrix()


def draw_sphere(position, color, radius=0.5, segments=12):
    """
    Draw a sphere at the given position.
    
    Args:
        position: (x, y, z) position
        color: (r, g, b) color
        radius: Radius of the sphere
        segments: Number of segments for the sphere (higher = smoother)
    """
    x, y, z = position
    
    # Ensure color is visible
    color_r, color_g, color_b = color
    color_r = max(0.4, color_r)
    color_g = max(0.4, color_g)
    color_b = max(0.4, color_b)
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    glColor3f(color_r, color_g, color_b)
    
    # Create a sphere quadric
    sphere = gluNewQuadric()
    gluQuadricNormals(sphere, GLU_SMOOTH)
    
    # Draw the sphere
    gluSphere(sphere, radius, segments, segments)
    
    # Free the quadric
    gluDeleteQuadric(sphere)
    
    glPopMatrix()


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


def draw_axes(length=5.0):
    """
    Draw coordinate axes for debugging.
    
    Args:
        length: Length of each axis
    """
    # Disable lighting for axes
    glDisable(GL_LIGHTING)
    
    # X axis (red)
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(length, 0, 0)
    glEnd()
    
    # Y axis (green)
    glBegin(GL_LINES)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, length, 0)
    glEnd()
    
    # Z axis (blue)
    glBegin(GL_LINES)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, length)
    glEnd()
    
    # Re-enable lighting if it was on
    glEnable(GL_LIGHTING) 