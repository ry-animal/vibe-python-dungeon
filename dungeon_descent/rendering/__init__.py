"""
3D rendering module for Dungeon Descent.

This package contains all the rendering components for the game.
"""
from .camera_3d import Camera
from .renderer_3d import RoguelikeGL
from .primitives import (
    draw_cube, draw_floor_tile, draw_wireframe_cube,
    draw_wireframe_grid, draw_axes, draw_cylinder, draw_sphere
)
from .lighting import (
    setup_lighting, setup_torch_lighting, disable_torch_lighting,
    setup_fog, disable_fog
)
from .textures import TextureManager, enable_texturing, disable_texturing
from .renderer_3d_simplified import RoguelikeGL as RoguelikeGLSimplified
