"""
Camera module for 3D rendering.
"""
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

class Camera:
    """
    3D camera for the game.
    
    Attributes:
        position (list): Camera position [x, y, z]
        target (list): Look-at target [x, y, z]
        up (list): Up vector [x, y, z]
        yaw (float): Horizontal rotation in radians
        pitch (float): Vertical rotation in radians
    """
    
    def __init__(self):
        """Initialize the camera."""
        self.position = [0.0, 10.0, 0.0]
        self.target = [0.0, 0.0, 0.0]
        self.up = [0.0, 1.0, 0.0]
        
        # Camera angles
        self.yaw = 0.0  # Horizontal rotation
        self.pitch = 0.0  # Vertical rotation
        
        # Movement settings
        self.move_speed = 0.1
        self.mouse_sensitivity = 0.002
    
    @property
    def forward(self):
        """Get the forward vector based on current yaw and pitch."""
        return [
            math.cos(self.pitch) * math.sin(self.yaw),
            math.sin(self.pitch),
            math.cos(self.pitch) * math.cos(self.yaw)
        ]
    
    def apply_first_person(self):
        """Apply first-person camera transform."""
        glLoadIdentity()
        # Calculate forward vector
        forward = self.forward
        # Calculate the right vector
        right = [
            math.sin(self.yaw - math.pi/2),
            0,
            math.cos(self.yaw - math.pi/2)
        ]
        # Recalculate up vector
        up = np.cross(right, forward)
        
        # Set camera position and orientation
        target = [
            self.position[0] + forward[0],
            self.position[1] + forward[1],
            self.position[2] + forward[2]
        ]
        gluLookAt(
            self.position[0], self.position[1], self.position[2],
            target[0], target[1], target[2],
            up[0], up[1], up[2]
        )
    
    def apply_third_person(self):
        """Apply third-person camera transform."""
        glLoadIdentity()
        gluLookAt(
            self.position[0], self.position[1], self.position[2],
            self.target[0], self.target[1], self.target[2],
            self.up[0], self.up[1], self.up[2]
        )
    
    def rotate(self, dx, dy):
        """
        Rotate the camera based on mouse movement.
        
        Args:
            dx (float): Mouse X delta
            dy (float): Mouse Y delta
        """
        self.yaw += dx * self.mouse_sensitivity
        self.pitch -= dy * self.mouse_sensitivity
        
        # Clamp pitch to avoid gimbal lock
        self.pitch = max(-math.pi/2 + 0.1, min(math.pi/2 - 0.1, self.pitch))
    
    def move(self, forward, right):
        """
        Move the camera relative to its orientation.
        
        Args:
            forward (float): Forward/backward movement
            right (float): Right/left movement
        """
        # Calculate movement vectors
        forward_vec = [
            math.sin(self.yaw),
            0,
            math.cos(self.yaw)
        ]
        right_vec = [
            math.sin(self.yaw - math.pi/2),
            0,
            math.cos(self.yaw - math.pi/2)
        ]
        
        # Update position
        self.position[0] += (forward_vec[0] * forward + right_vec[0] * right) * self.move_speed
        self.position[2] += (forward_vec[2] * forward + right_vec[2] * right) * self.move_speed 