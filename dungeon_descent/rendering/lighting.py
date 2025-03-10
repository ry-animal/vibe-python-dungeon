"""
Lighting and material management for 3D rendering.
"""
from OpenGL.GL import *
import numpy as np


def setup_lighting():
    """
    Set up basic lighting for the scene.
    """
    # Enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up ambient light
    ambient_light = [0.3, 0.3, 0.3, 1.0]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_light)
    
    # Configure light 0 (main light)
    light_position = [0.0, 20.0, 0.0, 1.0]  # Positioned above the scene
    diffuse_light = [0.8, 0.8, 0.8, 1.0]    # Bright white light
    specular_light = [0.5, 0.5, 0.5, 1.0]   # Some specularity
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)


def setup_torch_lighting(position, color=(1.0, 0.7, 0.3), intensity=1.0):
    """
    Set up a torch/point light at the given position.
    
    Args:
        position: (x, y, z) position for the light
        color: (r, g, b) color of the light
        intensity: Brightness multiplier for the light
    """
    # Enable the second light
    glEnable(GL_LIGHT1)
    
    # Set up light properties
    light_position = [position[0], position[1], position[2], 1.0]  # w=1.0 for point light
    
    # Scale color by intensity
    r, g, b = color
    diffuse_light = [r * intensity, g * intensity, b * intensity, 1.0]
    
    # Some ambient contribution
    ambient_light = [r * 0.1, g * 0.1, b * 0.1, 1.0]
    
    # Falloff parameters (distance attenuation)
    # constant, linear, quadratic
    attenuation = [1.0, 0.05, 0.01]
    
    glLightfv(GL_LIGHT1, GL_POSITION, light_position)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_light)
    
    # Set up attenuation
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, attenuation[0])
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, attenuation[1])
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, attenuation[2])


def disable_torch_lighting():
    """Disable the torch light (GL_LIGHT1)."""
    glDisable(GL_LIGHT1)


def set_material_properties(ambient=(0.2, 0.2, 0.2, 1.0), 
                           diffuse=(0.8, 0.8, 0.8, 1.0),
                           specular=(0.0, 0.0, 0.0, 1.0),
                           shininess=0.0):
    """
    Set material properties for subsequent rendered objects.
    
    Args:
        ambient: RGBA ambient color
        diffuse: RGBA diffuse color
        specular: RGBA specular color
        shininess: Shininess factor (0-128)
    """
    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMaterialf(GL_FRONT, GL_SHININESS, shininess)


def setup_fog(color=(0.5, 0.5, 0.5, 1.0), start=20.0, end=60.0, density=0.04):
    """
    Set up fog in the scene.
    
    Args:
        color: RGBA fog color
        start: Distance at which fog begins
        end: Distance at which fog reaches maximum
        density: Fog density for exponential fog
    """
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_LINEAR)  # GL_LINEAR, GL_EXP, or GL_EXP2
    glFogfv(GL_FOG_COLOR, color)
    glFogf(GL_FOG_START, start)
    glFogf(GL_FOG_END, end)
    glFogf(GL_FOG_DENSITY, density)
    glHint(GL_FOG_HINT, GL_NICEST)


def disable_fog():
    """Disable fog effects."""
    glDisable(GL_FOG) 