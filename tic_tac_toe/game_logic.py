"""
game_logic.py - Core game rules and board state management.

Board layout (indices 0-8):
    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8
"""

from collections import deque
from typing import List, Optional, Tuple

WINNING_COMBINATIONS: List[Tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
    (0, 4, 8), (2, 4, 6)              # Diagonals
]


class TicTacToeGame:
    """Manages game state: board, current player, winner detection."""
    
    def __init__(self):
        self.reset()
    
    def reset(self) -> None:
        """Reset to initial state."""
        self.board: List[Optional[str]] = [None] * 9
        self.current_player: str = 'X'
        self.game_over: bool = False
        self.winner: Optional[str] = None
    
    def make_move(self, position: int) -> bool:
        """Make move at position. Returns True if valid."""
        if not self.is_valid_move(position):
            return False
        
        self.board[position] = self.current_player
        
        if self.check_winner(self.current_player):
            self.game_over = True
            self.winner = self.current_player
        elif self.is_board_full():
            self.game_over = True
            self.winner = None
        else:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
        
        return True
    
    def is_valid_move(self, position: int) -> bool:
        """Check if move is valid (in bounds, empty cell, game not over)."""
        return (not self.game_over and 
                0 <= position <= 8 and 
                self.board[position] is None)
    
    def get_valid_moves(self) -> List[int]:
        """Return list of empty positions."""
        return [i for i in range(9) if self.board[i] is None]
    
    def check_winner(self, player: str) -> bool:
        """Check if player has won."""
        return any(all(self.board[i] == player for i in combo) 
                   for combo in WINNING_COMBINATIONS)
    
    def get_winning_combination(self) -> Optional[Tuple[int, int, int]]:
        """Return winning combination indices or None."""
        if self.winner is None:
            return None
        for combo in WINNING_COMBINATIONS:
            if all(self.board[i] == self.winner for i in combo):
                return combo
        return None
    
    def is_board_full(self) -> bool:
        """Check if board has no empty cells."""
        return all(cell is not None for cell in self.board)
    
    def get_board_copy(self) -> List[Optional[str]]:
        """Return copy of board state."""
        return self.board.copy()
    
    def get_game_status(self) -> str:
        """Return human-readable game status."""
        if not self.game_over:
            return "Your turn (X)" if self.current_player == 'X' else "Computer's turn (O)"
        elif self.winner == 'X':
            return "You win! 🎉"
        elif self.winner == 'O':
            return "Computer wins! 🤖"
        return "It's a draw! 🤝"


class NoDrawGame(TicTacToeGame):
    """
    No Draw variant of Tic Tac Toe.
    
    Once a player has 3 marks on the board, each new move removes
    that player's oldest mark (FIFO). Draws are impossible.
    """
    
    MAX_MARKS = 3
    
    def __init__(self):
        super().__init__()
        self.x_moves: deque = deque()
        self.o_moves: deque = deque()
    
    def reset(self) -> None:
        """Reset to initial state including move histories."""
        super().reset()
        self.x_moves = deque()
        self.o_moves = deque()
    
    def _get_player_moves(self, player: str) -> deque:
        """Return the move history deque for the given player."""
        return self.x_moves if player == 'X' else self.o_moves
    
    def get_oldest_mark(self, player: str) -> Optional[int]:
        """Return the position of the player's oldest mark, or None."""
        moves = self._get_player_moves(player)
        return moves[0] if len(moves) >= self.MAX_MARKS else None
    
    def is_valid_move(self, position: int) -> bool:
        """
        Check if move is valid. In No Draw mode, can place on oldest mark
        because it will be removed before new mark is placed.
        """
        if self.game_over or not (0 <= position <= 8):
            return False
        
        cell = self.board[position]
        
        # If cell is empty, always valid
        if cell is None:
            return True
        
        # If cell has opponent's mark, invalid
        if cell != self.current_player:
            return False
        
        # If cell has our mark, valid only if it's our oldest mark
        moves = self._get_player_moves(self.current_player)
        if len(moves) >= self.MAX_MARKS and moves[0] == position:
            return True
        
        return False
    
    def make_move(self, position: int) -> bool:
        """
        Make move at position. If the player already has 3 marks,
        removes the oldest mark first (FIFO), then places new mark,
        then checks for winner.
        Returns True if valid.
        """
        if not self.is_valid_move(position):
            return False
        
        player = self.current_player
        moves = self._get_player_moves(player)
        
        # Remove oldest mark if player already has MAX_MARKS
        removed_pos = None
        if len(moves) >= self.MAX_MARKS:
            removed_pos = moves.popleft()
            self.board[removed_pos] = None
        
        # Place new mark
        self.board[position] = player
        moves.append(position)
        
        # Check for winner after placement (and removal)
        if self.check_winner(player):
            self.game_over = True
            self.winner = player
        else:
            self.current_player = 'O' if player == 'X' else 'X'
        
        return True
    
    def is_board_full(self) -> bool:
        """In No Draw mode, the board is never considered full (no draws)."""
        return False
    
    def get_game_status(self) -> str:
        """Return human-readable game status."""
        if not self.game_over:
            return "Your turn (X)" if self.current_player == 'X' else "Computer's turn (O)"
        elif self.winner == 'X':
            return "You win! 🎉"
        elif self.winner == 'O':
            return "Computer wins! 🤖"
        return "Game in progress..."
