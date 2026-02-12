"""Unit tests for AI modules."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_easy import get_easy_move
from ai_medium import get_medium_move, find_winning_move
from ai_hard import get_hard_move, minimax, check_winner, is_board_full


class TestAIEasy(unittest.TestCase):
    """Tests for Easy AI (random moves)."""
    
    def test_returns_valid_move(self):
        """Should return an empty position."""
        board = ['X', None, None, 'O', None, None, None, None, None]
        move = get_easy_move(board)
        self.assertIsNotNone(move)
        self.assertIsNone(board[move])
    
    def test_returns_none_when_full(self):
        """Should return None when board is full."""
        board = ['X', 'O', 'X', 'O', 'X', 'O', 'O', 'X', 'O']
        self.assertIsNone(get_easy_move(board))
    
    def test_only_returns_empty_positions(self):
        """All returned moves should be valid."""
        board = ['X', 'O', 'X', None, None, None, 'O', 'X', 'O']
        for _ in range(50):  # Run multiple times due to randomness
            move = get_easy_move(board)
            self.assertIn(move, [3, 4, 5])


class TestAIMedium(unittest.TestCase):
    """Tests for Medium AI (win/block strategy)."""
    
    def test_takes_winning_move(self):
        """Should complete winning line when possible."""
        board = ['X', 'X', None, 'O', 'O', None, None, None, None]
        move = get_medium_move(board)
        self.assertEqual(move, 5)  # O should complete row 2
    
    def test_blocks_player_win(self):
        """Should block player's winning line."""
        board = ['X', 'X', None, 'O', None, None, None, None, None]
        move = get_medium_move(board)
        self.assertEqual(move, 2)  # Block X's top row win
    
    def test_win_priority_over_block(self):
        """Should prefer winning over blocking."""
        board = ['X', 'X', None, 'O', 'O', None, None, None, None]
        move = get_medium_move(board)
        self.assertEqual(move, 5)  # Win instead of block
    
    def test_find_winning_move_horizontal(self):
        """Detect winning move in row."""
        board = ['O', 'O', None, None, None, None, None, None, None]
        self.assertEqual(find_winning_move(board, 'O'), 2)
    
    def test_find_winning_move_vertical(self):
        """Detect winning move in column."""
        board = ['O', None, None, 'O', None, None, None, None, None]
        self.assertEqual(find_winning_move(board, 'O'), 6)
    
    def test_find_winning_move_diagonal(self):
        """Detect winning move in diagonal."""
        board = ['O', None, None, None, 'O', None, None, None, None]
        self.assertEqual(find_winning_move(board, 'O'), 8)
    
    def test_returns_none_when_full(self):
        """Should return None when board is full."""
        board = ['X', 'O', 'X', 'O', 'X', 'O', 'O', 'X', 'O']
        self.assertIsNone(get_medium_move(board))


class TestAIHard(unittest.TestCase):
    """Tests for Hard AI (minimax - unbeatable)."""
    
    def test_takes_winning_move(self):
        """Should take immediate win."""
        board = ['X', 'X', None, 'O', 'O', None, None, None, None]
        move = get_hard_move(board)
        self.assertEqual(move, 5)
    
    def test_blocks_player_win(self):
        """Should block player's winning move."""
        board = ['X', 'X', None, 'O', None, None, None, None, None]
        move = get_hard_move(board)
        self.assertEqual(move, 2)
    
    def test_takes_center_first(self):
        """Should prefer center on empty board or after corner."""
        board = ['X', None, None, None, None, None, None, None, None]
        move = get_hard_move(board)
        self.assertEqual(move, 4)  # Center is optimal response to corner
    
    def test_prevents_fork(self):
        """Should prevent player's fork setup."""
        board = ['X', None, None, None, 'O', None, None, None, 'X']
        move = get_hard_move(board)
        # Optimal moves are edges to prevent fork
        self.assertIn(move, [1, 3, 5, 7])
    
    def test_never_loses(self):
        """Hard AI should never lose (draw or win)."""
        # Simulate game where AI plays optimally
        board = [None] * 9
        board[0] = 'X'  # Player takes corner
        
        # AI responds
        move = get_hard_move(board)
        board[move] = 'O'
        
        # Continue a few moves
        for player_move in [8, 2, 6]:
            if board[player_move] is None:
                board[player_move] = 'X'
                if not check_winner(board, 'X') and not is_board_full(board):
                    ai_move = get_hard_move(board)
                    if ai_move is not None:
                        board[ai_move] = 'O'
        
        # AI should not have lost
        self.assertFalse(check_winner(board, 'X'))
    
    def test_minimax_win_score(self):
        """Minimax should return positive score for winning position."""
        board = ['O', 'O', None, 'X', 'X', None, None, None, None]
        board[2] = 'O'  # O wins
        score = minimax(board, 0, False)
        self.assertGreater(score, 0)
    
    def test_minimax_loss_score(self):
        """Minimax should return negative score for losing position."""
        board = ['X', 'X', None, 'O', 'O', None, None, None, None]
        board[2] = 'X'  # X wins
        score = minimax(board, 0, True)
        self.assertLess(score, 0)
    
    def test_minimax_draw_score(self):
        """Minimax should return 0 for draw."""
        board = ['X', 'O', 'X', 'X', 'O', 'O', 'O', 'X', 'X']
        score = minimax(board, 0, True)
        self.assertEqual(score, 0)
    
    def test_check_winner(self):
        """Helper function should detect wins."""
        board = ['X', 'X', 'X', None, None, None, None, None, None]
        self.assertTrue(check_winner(board, 'X'))
        self.assertFalse(check_winner(board, 'O'))
    
    def test_is_board_full(self):
        """Helper function should detect full board."""
        self.assertFalse(is_board_full([None] * 9))
        self.assertTrue(is_board_full(['X', 'O', 'X', 'O', 'X', 'O', 'O', 'X', 'O']))
    
    def test_returns_none_when_full(self):
        """Should return None when no moves available."""
        board = ['X', 'O', 'X', 'O', 'X', 'O', 'O', 'X', 'O']
        self.assertIsNone(get_hard_move(board))


if __name__ == '__main__':
    unittest.main()
