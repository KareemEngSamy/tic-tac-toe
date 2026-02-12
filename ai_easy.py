"""ai_easy.py - Random move AI (no strategy)."""

import random
from typing import List, Optional


def get_easy_move(board: List[Optional[str]]) -> Optional[int]:
    """Return a random empty position."""
    empty = [i for i in range(9) if board[i] is None]
    return random.choice(empty) if empty else None


def get_easy_move_no_draw(board: List[Optional[str]], x_moves: list, o_moves: list) -> Optional[int]:
    """
    Return a random valid position for No Draw mode.
    
    Valid moves are:
    - Any currently empty cell
    - The oldest O mark position, if O has >= 3 marks (will be removed before placement)
    """
    empty = [i for i in range(9) if board[i] is None]
    
    # If O has 3 marks, oldest will be removed, so it becomes valid
    if len(o_moves) >= 3:
        oldest = o_moves[0]
        if board[oldest] == 'O':  # Still has O's mark (not overwritten by X yet)
            empty.append(oldest)
    
    return random.choice(empty) if empty else None
