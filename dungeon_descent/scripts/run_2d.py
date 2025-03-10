"""
Script to run the 2D version of Dungeon Descent.
"""
import tcod
from dungeon_descent.core.engine import Engine


def main():
    """
    Run the 2D version of Dungeon Descent.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    # Initialize game engine
    engine = Engine()
    
    # Create window with tcod.context.new_terminal as required by the rules
    with tcod.context.new_terminal(
        engine.width,
        engine.height,
        title="Dungeon Descent",
        vsync=True,
    ) as context:
        
        print("Dungeon Descent 2D started. Use arrow keys to move, ESC to quit.")
        
        # Main game loop
        while True:
            engine.render(context)
            
            for event in tcod.event.wait():
                if event.type == "QUIT":
                    return 0
                elif event.type == "KEYDOWN":
                    # Movement keys
                    if event.sym == tcod.event.KeySym.UP:
                        engine.move_player(0, -1)
                    elif event.sym == tcod.event.KeySym.DOWN:
                        engine.move_player(0, 1)
                    elif event.sym == tcod.event.KeySym.LEFT:
                        engine.move_player(-1, 0)
                    elif event.sym == tcod.event.KeySym.RIGHT:
                        engine.move_player(1, 0)
                    elif event.sym == tcod.event.KeySym.ESCAPE:
                        return 0
                    
                    engine.update()


if __name__ == "__main__":
    exit(main()) 