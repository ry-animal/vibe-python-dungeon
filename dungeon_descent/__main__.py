"""
Main entry point for Dungeon Descent game when run as a package.
"""
import sys


def main():
    """
    Main entry point that decides which mode to run based on arguments.
    
    Usage:
        python -m dungeon_descent [2d|3d]
    
    Args:
        2d: Run in 2D console mode (default)
        3d: Run in 3D OpenGL mode
    """
    # Parse command line arguments
    mode = "2d"  # Default to 2D mode
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ("3d", "3", "opengl"):
            mode = "3d"
        elif sys.argv[1].lower() in ("2d", "2", "console", "terminal"):
            mode = "2d"
        else:
            print(f"Unknown mode: {sys.argv[1]}")
            print("Available modes: 2d, 3d")
            return 1
    
    # Run the appropriate mode
    if mode == "2d":
        from dungeon_descent.scripts.run_2d import main as run_2d
        return run_2d()
    else:
        from dungeon_descent.scripts.run_3d import main as run_3d
        return run_3d()


if __name__ == "__main__":
    sys.exit(main()) 