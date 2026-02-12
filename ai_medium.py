"""ai_medium.py - Reactive AI (blocks player, takes wins, else random)."""

import random
from collections import deque
from typing import List, Optional, Tuple

WINNING_COMBINATIONS: List[Tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]


def find_winning_move(board: List[Optional[str]], player: str) -> Optional[int]:
    """Find position that completes a winning line for player."""
    for combo in WINNING_COMBINATIONS:
        values = [board[i] for i in combo]
        if values.count(player) == 2 and values.count(None) == 1:
            return combo[values.index(None)]
    return None


def get_medium_move(board: List[Optional[str]]) -> Optional[int]:
    """
    Priority: 1) Win if possible, 2) Block player win, 3) Random move.
    """
    empty = [i for i in range(9) if board[i] is None]
    if not empty:
        return None
    
    # Try to win
    win_move = find_winning_move(board, 'O')
    if win_move is not None:
        return win_move
    
    # Block player
    block_move = find_winning_move(board, 'X')
    if block_move is not None:
        return block_move
    
    return random.choice(empty)


def _simulate_no_draw_board(board: List[Optional[str]], player: str,
                             position: int, player_moves: list) -> List[Optional[str]]:
    """
    Simulate placing a mark in No Draw mode: remove oldest if at 3,
    then place new mark. Returns a new board copy.
    """
    sim_board = board.copy()
    sim_moves = list(player_moves)
    
    if len(sim_moves) >= 3:
        oldest = sim_moves[0]
        sim_board[oldest] = None
    
    sim_board[position] = player
    return sim_board


def find_winning_move_no_draw(board: List[Optional[str]], player: str,
                               player_moves: list) -> Optional[int]:
    """
    Find a position that creates a winning line for player in No Draw mode.
    Must simulate the removal of the oldest mark before checking.
    """
    # Determine available positions
    available = [i for i in range(9) if board[i] is None]
    if len(player_moves) >= 3:
        oldest = player_moves[0]
        if oldest not in available:
            available.append(oldest)
    
    for pos in available:
        sim_board = _simulate_no_draw_board(board, player, pos, player_moves)
        # Check if this creates a win
        if any(all(sim_board[i] == player for i in combo) for combo in WINNING_COMBINATIONS):
            return pos
    return None


def get_medium_move_no_draw(board: List[Optional[str]], x_moves: list, o_moves: list) -> Optional[int]:
    """
    No Draw medium AI.
    Priority: 1) Win if possible, 2) Block player win, 3) Random move.
    Uses simulation to account for mark removal.
    """
    # Available cells for O
    available = [i for i in range(9) if board[i] is None]
    if len(o_moves) >= 3:
        oldest = o_moves[0]
        if oldest not in available:
            available.append(oldest)
    
    if not available:
        return None
    
    # Try to win
    win_move = find_winning_move_no_draw(board, 'O', o_moves)
    if win_move is not None:
        return win_move
    
    # Block player win (simulate X's next move with removal)
    block_move = find_winning_move_no_draw(board, 'X', x_moves)
    if block_move is not None and block_move in available:
        return block_move
    
    return random.choice(available)
