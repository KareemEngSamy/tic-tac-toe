"""
ai_hard.py - Minimax AI (unbeatable).

Minimax explores all possible game states recursively:
- Maximizer (O/computer): picks move with highest score
- Minimizer (X/player): picks move with lowest score
- Scores: +10 win, -10 loss, 0 draw (adjusted by depth for faster wins)

No-Draw variant uses alpha-beta pruning, dynamic depth limiting,
move ordering, and state hashing to avoid freezes.
"""

from collections import deque
from typing import List, Optional, Tuple

WINNING_COMBINATIONS: List[Tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

# Preferred move ordering: center → corners → edges (improves pruning)
_MOVE_PRIORITY = [4, 0, 2, 6, 8, 1, 3, 5, 7]


def check_winner(board: List[Optional[str]], player: str) -> bool:
    """Check if player has won."""
    return any(all(board[i] == player for i in combo) for combo in WINNING_COMBINATIONS)


def is_board_full(board: List[Optional[str]]) -> bool:
    """Check if board is full."""
    return all(cell is not None for cell in board)


def minimax(board: List[Optional[str]], depth: int, is_maximizing: bool) -> int:
    """
    Minimax algorithm: returns optimal score for current board state.
    Depth adjustment makes AI prefer faster wins / slower losses.
    """
    if check_winner(board, 'O'):
        return 10 - depth
    if check_winner(board, 'X'):
        return depth - 10
    if is_board_full(board):
        return 0

    empty = [i for i in range(9) if board[i] is None]

    if is_maximizing:
        best = float('-inf')
        for pos in empty:
            board[pos] = 'O'
            best = max(best, minimax(board, depth + 1, False))
            board[pos] = None
        return best
    else:
        best = float('inf')
        for pos in empty:
            board[pos] = 'X'
            best = min(best, minimax(board, depth + 1, True))
            board[pos] = None
        return best


def get_hard_move(board: List[Optional[str]]) -> Optional[int]:
    """Return optimal move using Minimax algorithm."""
    empty = [i for i in range(9) if board[i] is None]
    if not empty:
        return None

    best_score = float('-inf')
    best_move = empty[0]

    for pos in empty:
        board[pos] = 'O'
        score = minimax(board, 0, False)
        board[pos] = None
        if score > best_score:
            best_score = score
            best_move = pos

    return best_move


# ==================== No Draw Mode AI ====================

MAX_MARKS = 3

# Transposition table cleared each top-level call
_tp_table: dict = {}


def _get_dynamic_depth(board: List[Optional[str]]) -> int:
    """Choose search depth based on how many cells are empty.
    
    Fewer empty cells → deeper search (smaller tree).
    More empty cells → shallower to avoid lag.
    """
    empty = sum(1 for c in board if c is None)
    if empty >= 7:
        return 4
    if empty >= 5:
        return 5
    return 6


def _order_moves(moves: List[int]) -> List[int]:
    """Sort moves by strategic priority for better alpha-beta pruning."""
    return sorted(moves, key=lambda m: _MOVE_PRIORITY.index(m)
                  if m in _MOVE_PRIORITY else 9)


def _board_key(board: List[Optional[str]], x_moves: list,
               o_moves: list, is_maximizing: bool) -> tuple:
    """Create a hashable key for the transposition table."""
    return (tuple(board), tuple(x_moves), tuple(o_moves), is_maximizing)


def _get_available_moves_no_draw(board: List[Optional[str]], player: str,
                                  player_moves: list) -> List[int]:
    """
    Get available moves for a player in No Draw mode.
    If the player has 3 marks, the oldest will be removed,
    so that cell also becomes available.
    """
    available = [i for i in range(9) if board[i] is None]
    if len(player_moves) >= MAX_MARKS:
        oldest = player_moves[0]
        if oldest not in available:
            available.append(oldest)
    return _order_moves(available)


def _heuristic_score(board: List[Optional[str]]) -> int:
    """Quick heuristic when depth limit reached.
    
    Counts how many winning lines each player threatens.
    """
    o_score = 0
    x_score = 0
    for combo in WINNING_COMBINATIONS:
        vals = [board[i] for i in combo]
        o_count = vals.count('O')
        x_count = vals.count('X')
        if x_count == 0 and o_count > 0:
            o_score += o_count
        if o_count == 0 and x_count > 0:
            x_score += x_count
    return o_score - x_score


def minimax_no_draw(board: List[Optional[str]], depth: int, is_maximizing: bool,
                     x_moves: list, o_moves: list, max_depth: int,
                     alpha: float = float('-inf'),
                     beta: float = float('inf')) -> int:
    """
    Minimax with alpha-beta pruning for No Draw mode.
    Simulates mark removal (FIFO) when a player already has 3 marks.
    Uses transposition table and heuristic evaluation at depth limit.
    """
    if check_winner(board, 'O'):
        return 10 - depth
    if check_winner(board, 'X'):
        return depth - 10
    if depth >= max_depth:
        return _heuristic_score(board)

    # Transposition table lookup
    key = _board_key(board, x_moves, o_moves, is_maximizing)
    if key in _tp_table:
        return _tp_table[key]

    if is_maximizing:
        player = 'O'
        player_moves = o_moves
    else:
        player = 'X'
        player_moves = x_moves

    available = _get_available_moves_no_draw(board, player, player_moves)

    if not available:
        return _heuristic_score(board)

    if is_maximizing:
        best = float('-inf')
        for pos in available:
            removed = None
            new_moves = list(player_moves)
            if len(new_moves) >= MAX_MARKS:
                removed = new_moves.pop(0)
                board[removed] = None

            board[pos] = player
            new_moves.append(pos)

            if check_winner(board, player):
                score = 10 - depth
            else:
                score = minimax_no_draw(board, depth + 1, False,
                                         x_moves, new_moves, max_depth,
                                         alpha, beta)

            board[pos] = None
            if removed is not None:
                board[removed] = player

            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        _tp_table[key] = best
        return best
    else:
        best = float('inf')
        for pos in available:
            removed = None
            new_moves = list(player_moves)
            if len(new_moves) >= MAX_MARKS:
                removed = new_moves.pop(0)
                board[removed] = None

            board[pos] = player
            new_moves.append(pos)

            if check_winner(board, player):
                score = depth - 10
            else:
                score = minimax_no_draw(board, depth + 1, True,
                                         new_moves, o_moves, max_depth,
                                         alpha, beta)

            board[pos] = None
            if removed is not None:
                board[removed] = player

            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        _tp_table[key] = best
        return best


def get_hard_move_no_draw(board: List[Optional[str]], x_moves: list,
                           o_moves: list) -> Optional[int]:
    """Return optimal move for O in No Draw mode.
    
    Uses Minimax with alpha-beta pruning, dynamic depth,
    move ordering, and transposition table.
    """
    global _tp_table
    _tp_table = {}  # Clear cache each top-level call

    available = _get_available_moves_no_draw(board, 'O', o_moves)

    if not available:
        return None

    # Fast path: take an immediate win before running expensive minimax
    for pos in available:
        removed = None
        sim_moves = list(o_moves)
        if len(sim_moves) >= MAX_MARKS:
            removed = sim_moves.pop(0)
            board[removed] = None
        board[pos] = 'O'
        won = check_winner(board, 'O')
        board[pos] = None
        if removed is not None:
            board[removed] = 'O'
        if won:
            return pos

    max_depth = _get_dynamic_depth(board)
    best_score = float('-inf')
    best_move = available[0]
    alpha = float('-inf')
    beta = float('inf')

    for pos in available:
        removed = None
        new_o_moves = list(o_moves)
        if len(new_o_moves) >= MAX_MARKS:
            removed = new_o_moves.pop(0)
            board[removed] = None

        board[pos] = 'O'
        new_o_moves.append(pos)

        if check_winner(board, 'O'):
            score = 10
        else:
            score = minimax_no_draw(board, 0, False, x_moves, new_o_moves,
                                     max_depth, alpha, beta)

        alpha = max(alpha, best_score)
    
    return best_move
