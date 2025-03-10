"""
Texture loading and management for 3D rendering.
"""
import os
import pygame
from OpenGL.GL import *
import numpy as np


class TextureManager:
    """Class to manage texture loading and binding."""
    
    def __init__(self):
        """Initialize the texture manager."""
        # Dictionary to store loaded textures
        self.textures = {}
        
        # Ensure pygame is initialized for image loading
        if not pygame.get_init():
            pygame.init()
    
    def load_texture(self, name, file_path):
        """
        Load a texture from a file and store it with the given name.
        
        Args:
            name: Name to identify the texture
            file_path: Path to the texture file
        
        Returns:
            The OpenGL texture ID
        """
        if name in self.textures:
            return self.textures[name]
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Warning: Texture file not found: {file_path}")
            # Create a default texture (checkerboard)
            texture_data = self._create_default_texture()
            texture_surface = pygame.Surface((64, 64))
            pygame.surfarray.blit_array(texture_surface, texture_data)
        else:
            # Load the image using pygame
            try:
                texture_surface = pygame.image.load(file_path)
            except Exception as e:
                print(f"Error loading texture {file_path}: {e}")
                # Create a default texture (checkerboard)
                texture_data = self._create_default_texture()
                texture_surface = pygame.Surface((64, 64))
                pygame.surfarray.blit_array(texture_surface, texture_data)
        
        # Get the texture data as a string buffer
        texture_data = pygame.image.tostring(texture_surface, 'RGBA', 1)
        width = texture_surface.get_width()
        height = texture_surface.get_height()
        
        # Generate an OpenGL texture ID
        texture_id = glGenTextures(1)
        
        # Bind the texture
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        
        # Upload the texture data
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        # Generate mipmaps
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, width, height, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        # Store the texture ID
        self.textures[name] = texture_id
        
        return texture_id
    
    def bind_texture(self, name):
        """
        Bind the texture with the given name.
        
        Args:
            name: Name of the texture to bind
        
        Returns:
            True if the texture was bound, False otherwise
        """
        if name not in self.textures:
            print(f"Warning: Texture '{name}' not loaded")
            return False
        
        glBindTexture(GL_TEXTURE_2D, self.textures[name])
        return True
    
    def _create_default_texture(self, size=64):
        """
        Create a default checkerboard texture.
        
        Args:
            size: Size of the texture (size x size)
        
        Returns:
            NumPy array with texture data
        """
        # Create a checkerboard pattern
        texture = np.zeros((size, size, 3), dtype=np.uint8)
        
        # Fill with checkerboard pattern
        for i in range(size):
            for j in range(size):
                if (i // 8 + j // 8) % 2 == 0:
                    texture[i, j] = [255, 0, 255]  # Magenta
                else:
                    texture[i, j] = [0, 0, 0]      # Black
        
        return texture
    
    def delete_texture(self, name):
        """
        Delete a texture from OpenGL and remove it from the manager.
        
        Args:
            name: Name of the texture to delete
        """
        if name in self.textures:
            glDeleteTextures(1, [self.textures[name]])
            del self.textures[name]
    
    def cleanup(self):
        """Delete all textures and clean up resources."""
        for texture_id in self.textures.values():
            glDeleteTextures(1, [texture_id])
        self.textures.clear()


def enable_texturing():
    """Enable texture mapping."""
    glEnable(GL_TEXTURE_2D)


def disable_texturing():
    """Disable texture mapping."""
    glDisable(GL_TEXTURE_2D) 