"""Unit tests for game_logic.py"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_logic import TicTacToeGame, WINNING_COMBINATIONS


class TestTicTacToeGame(unittest.TestCase):
    """Tests for TicTacToeGame class."""
    
    def setUp(self):
        """Create fresh game instance for each test."""
        self.game = TicTacToeGame()
    
    # === Initialization Tests ===
    
    def test_initial_board_empty(self):
        """Board should have 9 empty cells on init."""
        self.assertEqual(len(self.game.board), 9)
        self.assertTrue(all(cell is None for cell in self.game.board))
    
    def test_initial_player_is_x(self):
        """First player should be X."""
        self.assertEqual(self.game.current_player, 'X')
    
    def test_initial_game_not_over(self):
        """Game should not be over at start."""
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.winner)
    
    # === Move Tests ===
    
    def test_valid_move(self):
        """Valid move should return True and update board."""
        result = self.game.make_move(0)
        self.assertTrue(result)
        self.assertEqual(self.game.board[0], 'X')
    
    def test_player_switches_after_move(self):
        """Current player should switch after valid move."""
        self.game.make_move(0)
        self.assertEqual(self.game.current_player, 'O')
        self.game.make_move(1)
        self.assertEqual(self.game.current_player, 'X')
    
    def test_invalid_move_occupied_cell(self):
        """Move to occupied cell should return False."""
        self.game.make_move(0)
        result = self.game.make_move(0)
        self.assertFalse(result)
    
    def test_invalid_move_out_of_bounds(self):
        """Move outside board should return False."""
        self.assertFalse(self.game.make_move(-1))
        self.assertFalse(self.game.make_move(9))
    
    def test_invalid_move_after_game_over(self):
        """Move after game ends should return False."""
        # X wins with top row
        self.game.board = ['X', 'X', None, 'O', 'O', None, None, None, None]
        self.game.make_move(2)  # X wins
        result = self.game.make_move(5)  # Try to move after game over
        self.assertFalse(result)
    
    # === Win Detection Tests ===
    
    def test_horizontal_win(self):
        """Detect horizontal wins."""
        self.game.board = ['X', 'X', None, 'O', 'O', None, None, None, None]
        self.game.make_move(2)  # X at position 2
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'X')
    
    def test_vertical_win(self):
        """Detect vertical wins."""
        self.game.board = ['X', 'O', 'O', 'X', None, None, None, None, None]
        self.game.make_move(6)  # X at position 6
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'X')
    
    def test_diagonal_win(self):
        """Detect diagonal wins."""
        self.game.board = ['X', 'O', None, 'O', 'X', None, None, None, None]
        self.game.make_move(8)  # X at position 8
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'X')
    
    def test_all_winning_combinations(self):
        """Test all 8 winning combinations."""
        for combo in WINNING_COMBINATIONS:
            game = TicTacToeGame()
            for pos in combo:
                game.board[pos] = 'X'
            self.assertTrue(game.check_winner('X'))
    
    def test_get_winning_combination(self):
        """Should return winning line indices."""
        self.game.board = ['X', 'X', 'X', 'O', 'O', None, None, None, None]
        self.game.game_over = True
        self.game.winner = 'X'
        self.assertEqual(self.game.get_winning_combination(), (0, 1, 2))
    
    # === Draw Tests ===
    
    def test_draw_detection(self):
        """Detect draw when board is full with no winner."""
        self.game.board = ['X', 'O', 'X', 'X', 'O', 'O', 'O', 'X', None]
        self.game.current_player = 'X'
        self.game.make_move(8)  # Fill last cell
        self.assertTrue(self.game.game_over)
        self.assertIsNone(self.game.winner)
    
    def test_is_board_full(self):
        """Board full detection."""
        self.assertFalse(self.game.is_board_full())
        self.game.board = ['X', 'O', 'X', 'O', 'X', 'O', 'O', 'X', 'O']
        self.assertTrue(self.game.is_board_full())
    
    # === Utility Tests ===
    
    def test_get_valid_moves(self):
        """Should return list of empty positions."""
        self.assertEqual(self.game.get_valid_moves(), list(range(9)))
        self.game.make_move(0)
        self.game.make_move(4)
        self.assertEqual(self.game.get_valid_moves(), [1, 2, 3, 5, 6, 7, 8])
    
    def test_get_board_copy(self):
        """Board copy should be independent."""
        self.game.make_move(0)
        copy = self.game.get_board_copy()
        copy[0] = 'O'
        self.assertEqual(self.game.board[0], 'X')
    
    def test_reset(self):
        """Reset should restore initial state."""
        self.game.make_move(0)
        self.game.make_move(1)
        self.game.reset()
        self.assertTrue(all(cell is None for cell in self.game.board))
        self.assertEqual(self.game.current_player, 'X')
        self.assertFalse(self.game.game_over)
    
    def test_get_game_status_messages(self):
        """Status messages should be correct."""
        self.assertIn("Your turn", self.game.get_game_status())
        self.game.make_move(0)
        self.assertIn("Computer", self.game.get_game_status())


if __name__ == '__main__':
    unittest.main()
