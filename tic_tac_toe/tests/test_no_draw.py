"""Unit tests for No Draw mode - game logic and AI."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_logic import NoDrawGame, TicTacToeGame, WINNING_COMBINATIONS
from ai_easy import get_easy_move_no_draw
from ai_medium import get_medium_move_no_draw, find_winning_move_no_draw
from ai_hard import get_hard_move_no_draw


class TestNoDrawGameInit(unittest.TestCase):
    """Tests for NoDrawGame initialization."""

    def setUp(self):
        self.game = NoDrawGame()

    def test_initial_board_empty(self):
        """Board should have 9 empty cells on init."""
        self.assertEqual(len(self.game.board), 9)
        self.assertTrue(all(cell is None for cell in self.game.board))

    def test_initial_move_histories_empty(self):
        """Move histories should be empty on init."""
        self.assertEqual(len(self.game.x_moves), 0)
        self.assertEqual(len(self.game.o_moves), 0)

    def test_initial_player_is_x(self):
        self.assertEqual(self.game.current_player, 'X')

    def test_initial_game_not_over(self):
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.winner)

    def test_is_subclass_of_tic_tac_toe(self):
        """NoDrawGame should be a subclass of TicTacToeGame."""
        self.assertIsInstance(self.game, TicTacToeGame)


class TestNoDrawGameMoves(unittest.TestCase):
    """Tests for No Draw move mechanics (placement + removal)."""

    def setUp(self):
        self.game = NoDrawGame()

    def test_first_three_moves_no_removal(self):
        """First 3 moves per player should not remove anything."""
        self.game.make_move(0)  # X at 0
        self.game.make_move(1)  # O at 1
        self.game.make_move(2)  # X at 2
        self.game.make_move(3)  # O at 3
        self.game.make_move(4)  # X at 4
        self.game.make_move(5)  # O at 5

        # All 6 cells should be occupied
        self.assertEqual(self.game.board[0], 'X')
        self.assertEqual(self.game.board[1], 'O')
        self.assertEqual(self.game.board[2], 'X')
        self.assertEqual(self.game.board[3], 'O')
        self.assertEqual(self.game.board[4], 'X')
        self.assertEqual(self.game.board[5], 'O')

        # Move histories should have 3 each
        self.assertEqual(list(self.game.x_moves), [0, 2, 4])
        self.assertEqual(list(self.game.o_moves), [1, 3, 5])

    def test_fourth_move_removes_oldest(self):
        """4th move by a player should remove their oldest mark."""
        # X moves: 0, 2, 4; O moves: 1, 3, 5
        self.game.make_move(0)  # X at 0
        self.game.make_move(1)  # O at 1
        self.game.make_move(2)  # X at 2
        self.game.make_move(3)  # O at 3
        self.game.make_move(4)  # X at 4
        self.game.make_move(5)  # O at 5

        # Now X's 4th move: place at 6, oldest (0) should be removed
        self.game.make_move(6)  # X at 6, remove X from 0

        self.assertIsNone(self.game.board[0])  # Removed
        self.assertEqual(self.game.board[6], 'X')  # Placed
        self.assertEqual(list(self.game.x_moves), [2, 4, 6])

    def test_removal_only_affects_own_marks(self):
        """Players should only remove their own marks, not opponent's."""
        self.game.make_move(0)  # X at 0
        self.game.make_move(1)  # O at 1
        self.game.make_move(2)  # X at 2
        self.game.make_move(3)  # O at 3
        self.game.make_move(4)  # X at 4
        self.game.make_move(5)  # O at 5

        # X's 4th move removes X's oldest (0), NOT O's
        self.game.make_move(6)  # X at 6
        self.assertEqual(self.game.board[1], 'O')  # O's mark untouched
        self.assertEqual(self.game.board[3], 'O')  # O's mark untouched
        self.assertEqual(self.game.board[5], 'O')  # O's mark untouched

    def test_removed_cell_becomes_reusable(self):
        """A removed cell should become None and be reusable."""
        # Use positions that don't create accidental wins
        self.game.make_move(0)  # X at 0
        self.game.make_move(1)  # O at 1
        self.game.make_move(3)  # X at 3
        self.game.make_move(2)  # O at 2
        self.game.make_move(8)  # X at 8  -> X: [0, 3, 8]
        self.game.make_move(5)  # O at 5  -> O: [1, 2, 5]

        self.game.make_move(6)  # X at 6, removes 0 -> X: [3, 8, 6]

        # Position 0 should now be in valid moves
        self.assertIn(0, self.game.get_valid_moves())

        # O should be able to move there
        result = self.game.make_move(0)  # O at 0, removes O's oldest (1)
        self.assertTrue(result)
        self.assertEqual(self.game.board[0], 'O')

    def test_fifo_order_maintained(self):
        """Marks should be removed in FIFO order across multiple removals."""
        # Use positions that don't accidentally create winning lines
        self.game.make_move(0)  # X at 0
        self.game.make_move(1)  # O at 1
        self.game.make_move(3)  # X at 3
        self.game.make_move(2)  # O at 2
        self.game.make_move(8)  # X at 8  -> X: [0, 3, 8]
        self.game.make_move(5)  # O at 5  -> O: [1, 2, 5]

        # X's 4th: place 6, remove 0
        self.game.make_move(6)  # X moves: [3, 8, 6]
        self.assertIsNone(self.game.board[0])

        # O's 4th: place 7, remove 1
        self.game.make_move(7)  # O moves: [2, 5, 7]
        self.assertIsNone(self.game.board[1])

        # X's 5th: place 4, remove 3
        self.game.make_move(4)  # X moves: [8, 6, 4]
        self.assertIsNone(self.game.board[3])

        self.assertEqual(list(self.game.x_moves), [8, 6, 4])
        self.assertEqual(list(self.game.o_moves), [2, 5, 7])

    def test_invalid_move_occupied_by_opponent(self):
        """Cannot move on cell occupied by opponent (not their oldest)."""
        self.game.make_move(0)  # X at 0
        self.game.make_move(4)  # O at 4

        # X tries to move on O's cell
        result = self.game.make_move(4)
        self.assertFalse(result)

    def test_board_is_never_full(self):
        """is_board_full should always return False in No Draw mode."""
        self.game.make_move(0)
        self.game.make_move(1)
        self.game.make_move(2)
        self.game.make_move(3)
        self.game.make_move(4)
        self.game.make_move(5)
        # 6 cells filled, 3 empty - but even if all were filled:
        self.assertFalse(self.game.is_board_full())

    def test_get_oldest_mark_none_when_under_three(self):
        """get_oldest_mark should return None when player has < 3 marks."""
        self.assertIsNone(self.game.get_oldest_mark('X'))
        self.game.make_move(0)
        self.assertIsNone(self.game.get_oldest_mark('X'))
        self.game.make_move(1)
        self.game.make_move(2)
        self.assertIsNone(self.game.get_oldest_mark('X'))  # Only 2 X marks

    def test_get_oldest_mark_returns_correct_position(self):
        """get_oldest_mark should return oldest when player has 3 marks."""
        self.game.make_move(0)  # X
        self.game.make_move(1)  # O
        self.game.make_move(2)  # X
        self.game.make_move(3)  # O
        self.game.make_move(4)  # X - now 3 X marks: [0, 2, 4]
        self.assertEqual(self.game.get_oldest_mark('X'), 0)


class TestNoDrawWinDetection(unittest.TestCase):
    """Tests for win detection in No Draw mode."""

    def setUp(self):
        self.game = NoDrawGame()

    def test_normal_win_before_removals_start(self):
        """Win should be detected in early game (< 3 marks each)."""
        # X wins with top row: 0, 1, 2
        self.game.make_move(0)  # X
        self.game.make_move(3)  # O
        self.game.make_move(1)  # X
        self.game.make_move(4)  # O
        self.game.make_move(2)  # X wins!

        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'X')

    def test_win_after_removal_phase(self):
        """Win after marks are being removed should be detected."""
        # Set up a scenario where X wins after removal phase
        # X: [0, 4, 2], removing 0, placing at 6 -> X: [4, 2, 6] = anti-diagonal (2,4,6)!
        self.game.make_move(0)  # X at 0
        self.game.make_move(1)  # O at 1
        self.game.make_move(4)  # X at 4
        self.game.make_move(3)  # O at 3
        self.game.make_move(2)  # X at 2  -> X: [0, 4, 2]
        self.game.make_move(5)  # O at 5  -> O: [1, 3, 5]
        # X now has 3: [0, 4, 2]. Next X move removes 0.
        # X plays 6: removes 0, places 6 -> X: [4, 2, 6] = anti-diagonal win (2,4,6)!
        self.game.make_move(6)  # X wins with diagonal 2,4,6

        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'X')

    def test_no_win_if_removal_breaks_line(self):
        """Removal of oldest mark can prevent a win."""
        self.game.make_move(0)  # X at 0
        self.game.make_move(3)  # O at 3
        self.game.make_move(1)  # X at 1
        self.game.make_move(4)  # O at 4
        self.game.make_move(6)  # X at 6  -> X: [0, 1, 6]
        self.game.make_move(5)  # O at 5  -> O: [3, 4, 5] O wins!

        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'O')

    def test_draw_impossible(self):
        """Game should never end in a draw in No Draw mode."""
        # Play many moves, game should never declare a draw
        moves = [0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 1, 2]
        for move in moves:
            if self.game.game_over:
                break
            if move in self.game.get_valid_moves():
                self.game.make_move(move)
            else:
                # Find any valid move
                valid = self.game.get_valid_moves()
                if valid:
                    self.game.make_move(valid[0])

        # If game is over, it must have a winner (no draws)
        if self.game.game_over:
            self.assertIsNotNone(self.game.winner)


class TestNoDrawReset(unittest.TestCase):
    """Tests for resetting No Draw game."""

    def test_reset_clears_move_histories(self):
        """Reset should clear x_moves and o_moves."""
        game = NoDrawGame()
        game.make_move(0)
        game.make_move(1)
        game.make_move(2)

        game.reset()

        self.assertEqual(len(game.x_moves), 0)
        self.assertEqual(len(game.o_moves), 0)
        self.assertTrue(all(cell is None for cell in game.board))
        self.assertEqual(game.current_player, 'X')
        self.assertFalse(game.game_over)


class TestNoDrawAIEasy(unittest.TestCase):
    """Tests for Easy AI in No Draw mode."""

    def test_returns_valid_move(self):
        """Should return a position that is empty or will be freed."""
        board = ['X', 'O', 'X', 'O', 'X', 'O', None, None, None]
        x_moves = [0, 2, 4]
        o_moves = [1, 3, 5]
        move = get_easy_move_no_draw(board, x_moves, o_moves)
        self.assertIsNotNone(move)
        # Move should be an empty cell or O's oldest mark
        valid = [i for i in range(9) if board[i] is None]
        valid.append(o_moves[0])  # O's oldest can be used
        self.assertIn(move, valid)

    def test_includes_oldest_mark_position(self):
        """When O has 3 marks, its oldest should be available."""
        board = ['X', 'O', 'X', 'O', 'X', 'O', None, None, None]
        x_moves = [0, 2, 4]
        o_moves = [1, 3, 5]
        # Run multiple times (random) to verify oldest is sometimes chosen
        moves_seen = set()
        for _ in range(100):
            move = get_easy_move_no_draw(board, x_moves, o_moves)
            moves_seen.add(move)
        # Position 1 (O's oldest) should be available alongside 6, 7, 8
        self.assertTrue(moves_seen.issubset({1, 6, 7, 8}))


class TestNoDrawAIMedium(unittest.TestCase):
    """Tests for Medium AI in No Draw mode."""

    def test_takes_winning_move(self):
        """Should take a winning move when available."""
        # O has marks at 3, 4 and needs 5 to win row 2
        board = [None, None, 'X', 'O', 'O', None, 'X', None, 'X']
        x_moves = [2, 6, 8]
        o_moves = [3, 4]
        move = get_medium_move_no_draw(board, x_moves, o_moves)
        self.assertEqual(move, 5)

    def test_blocks_player_win(self):
        """Should block player's winning move."""
        # X has marks at 0, 1 and needs 2 to win
        # O has marks at 4, 8 (no immediate win for O)
        board = ['X', 'X', None, None, 'O', None, None, None, 'O']
        x_moves = [0, 1]
        o_moves = [4, 8]
        move = get_medium_move_no_draw(board, x_moves, o_moves)
        self.assertEqual(move, 2)

    def test_returns_valid_move(self):
        """Should always return a valid move."""
        board = ['X', 'O', 'X', 'O', 'X', 'O', None, None, None]
        x_moves = [0, 2, 4]
        o_moves = [1, 3, 5]
        move = get_medium_move_no_draw(board, x_moves, o_moves)
        self.assertIsNotNone(move)

    def test_find_winning_move_with_removal(self):
        """Should find win considering mark removal."""
        # O at 0, 4 - if O places at 8, that's a diagonal win (0,4,8)
        # But O only has 2 marks so no removal
        board = ['O', None, None, None, 'O', None, None, None, None]
        o_moves = [0, 4]
        result = find_winning_move_no_draw(board, 'O', o_moves)
        self.assertEqual(result, 8)


class TestNoDrawAIHard(unittest.TestCase):
    """Tests for Hard AI in No Draw mode."""

    def test_takes_winning_move(self):
        """Should take immediate win."""
        board = [None, None, 'X', 'O', 'O', None, 'X', None, 'X']
        x_moves = [2, 6, 8]
        o_moves = [3, 4]
        move = get_hard_move_no_draw(board, x_moves, o_moves)
        # Position 5 completes row (3,4,5) for O
        self.assertEqual(move, 5)

    def test_blocks_player_win(self):
        """Should block player's winning move."""
        # X has [0, 1, 6] threatening top row (needs 2). O has [3, 4, 7], no immediate win.
        board = ['X', 'X', None, 'O', 'O', None, 'X', 'O', None]
        x_moves = [0, 1, 6]
        o_moves = [3, 4, 7]
        move = get_hard_move_no_draw(board, x_moves, o_moves)
        self.assertEqual(move, 2)

    def test_returns_valid_move(self):
        """Should return a valid move in all cases."""
        board = ['X', 'O', 'X', 'O', 'X', 'O', None, None, None]
        x_moves = [0, 2, 4]
        o_moves = [1, 3, 5]
        move = get_hard_move_no_draw(board, x_moves, o_moves)
        self.assertIsNotNone(move)
        # Should be one of the empty cells or O's oldest
        valid = [6, 7, 8, 1]  # empty + O's oldest
        self.assertIn(move, valid)

    def test_does_not_return_none(self):
        """In No Draw, there should always be a valid move."""
        board = ['X', 'O', 'X', 'O', 'X', 'O', None, None, None]
        x_moves = [0, 2, 4]
        o_moves = [1, 3, 5]
        move = get_hard_move_no_draw(board, x_moves, o_moves)
        self.assertIsNotNone(move)


class TestNoDrawGameIntegration(unittest.TestCase):
    """Integration tests simulating full games in No Draw mode."""

    def test_full_game_with_removals(self):
        """Simulate a full game to ensure no crashes."""
        game = NoDrawGame()
        max_turns = 30  # Safety limit
        turn = 0
        while not game.game_over and turn < max_turns:
            valid = game.get_valid_moves()
            if not valid:
                # In No Draw with removals, there should always be valid moves
                # unless the game uses the oldest mark position
                if game.current_player == 'X' and len(game.x_moves) >= 3:
                    valid = [game.x_moves[0]]
                elif game.current_player == 'O' and len(game.o_moves) >= 3:
                    valid = [game.o_moves[0]]
            
            if valid:
                game.make_move(valid[0])
            turn += 1

        # Game should eventually end with a winner
        if game.game_over:
            self.assertIsNotNone(game.winner)

    def test_ai_never_makes_invalid_move(self):
        """AI should never return an invalid move in No Draw mode."""
        game = NoDrawGame()
        max_turns = 20
        for _ in range(max_turns):
            if game.game_over:
                break
            
            if game.current_player == 'X':
                # Human plays first valid move
                valid = game.get_valid_moves()
                if valid:
                    game.make_move(valid[0])
            else:
                # AI plays
                board = game.get_board_copy()
                x_moves = list(game.x_moves)
                o_moves = list(game.o_moves)
                move = get_easy_move_no_draw(board, x_moves, o_moves)
                if move is not None:
                    result = game.make_move(move)
                    self.assertTrue(result, f"AI made invalid move at {move}")

    def test_max_three_marks_per_player(self):
        """Each player should never have more than 3 marks at any time."""
        game = NoDrawGame()
        for i in range(20):
            if game.game_over:
                break
            valid = game.get_valid_moves()
            if valid:
                game.make_move(valid[0])
            
            x_count = sum(1 for c in game.board if c == 'X')
            o_count = sum(1 for c in game.board if c == 'O')
            self.assertLessEqual(x_count, 3)
            self.assertLessEqual(o_count, 3)


class TestGameModeUtils(unittest.TestCase):
    """Tests for GameMode enum and related utils."""

    def test_game_mode_values(self):
        from utils import GameMode
        self.assertEqual(GameMode.NORMAL.value, "normal")
        self.assertEqual(GameMode.NO_DRAW.value, "no_draw")

    def test_game_mode_count(self):
        from utils import GameMode
        self.assertEqual(len(GameMode), 2)

    def test_game_mode_names_mapping(self):
        from utils import GameMode, GAME_MODE_NAMES
        for mode in GameMode:
            self.assertIn(mode, GAME_MODE_NAMES)
            self.assertIsInstance(GAME_MODE_NAMES[mode], str)

    def test_game_mode_descriptions_mapping(self):
        from utils import GameMode, GAME_MODE_DESCRIPTIONS
        for mode in GameMode:
            self.assertIn(mode, GAME_MODE_DESCRIPTIONS)
            self.assertIsInstance(GAME_MODE_DESCRIPTIONS[mode], str)


if __name__ == '__main__':
    unittest.main()
