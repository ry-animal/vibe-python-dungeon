"""
Setup script for the Dungeon Descent package.
"""
from setuptools import setup, find_packages

setup(
    name="dungeon_descent",
    version="0.1.0",
    author="Dungeon Descent Team",
    author_email="example@example.com",
    description="A roguelike game with both 2D and 3D rendering capabilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dungeon-descent",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Gamers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment :: Role-Playing",
    ],
    python_requires=">=3.9",
    install_requires=[
        "tcod>=13.8.1",
        "numpy>=1.24.0",
        "pygame>=2.5.0",
        "PyOpenGL>=3.1.6",
        "PyOpenGL-accelerate>=3.1.6",
    ],
    entry_points={
        "console_scripts": [
            "dungeon-descent=dungeon_descent.__main__:main",
            "dungeon-descent-2d=dungeon_descent.scripts.run_2d:main",
            "dungeon-descent-3d=dungeon_descent.scripts.run_3d:main",
        ],
    },
) 