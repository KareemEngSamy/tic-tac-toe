"""Unit tests for utils.py"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    Difficulty, 
    DIFFICULTY_NAMES, 
    DIFFICULTY_DESCRIPTIONS,
    COLORS,
    FONTS,
    format_player_symbol,
    get_cell_color
)


class TestDifficulty(unittest.TestCase):
    """Tests for Difficulty enum."""
    
    def test_difficulty_values(self):
        """Enum should have correct values."""
        self.assertEqual(Difficulty.EASY.value, "easy")
        self.assertEqual(Difficulty.MEDIUM.value, "medium")
        self.assertEqual(Difficulty.HARD.value, "hard")
    
    def test_difficulty_count(self):
        """Should have exactly 3 difficulty levels."""
        self.assertEqual(len(Difficulty), 3)
    
    def test_difficulty_names_mapping(self):
        """All difficulties should have display names."""
        for diff in Difficulty:
            self.assertIn(diff, DIFFICULTY_NAMES)
            self.assertIsInstance(DIFFICULTY_NAMES[diff], str)
    
    def test_difficulty_descriptions_mapping(self):
        """All difficulties should have descriptions."""
        for diff in Difficulty:
            self.assertIn(diff, DIFFICULTY_DESCRIPTIONS)
            self.assertIsInstance(DIFFICULTY_DESCRIPTIONS[diff], str)


class TestColors(unittest.TestCase):
    """Tests for color constants."""
    
    def test_required_colors_exist(self):
        """Essential colors should be defined."""
        required = ['background', 'surface', 'primary', 'text_primary', 
                    'player_x', 'player_o', 'win', 'draw']
        for color in required:
            self.assertIn(color, COLORS)
    
    def test_colors_are_valid_hex(self):
        """All colors should be valid hex codes."""
        for name, color in COLORS.items():
            self.assertTrue(
                color.startswith('#') and len(color) == 7,
                f"{name} is not a valid hex color: {color}"
            )


class TestFonts(unittest.TestCase):
    """Tests for font constants."""
    
    def test_required_fonts_exist(self):
        """Essential fonts should be defined."""
        required = ['title', 'button', 'cell', 'status']
        for font in required:
            self.assertIn(font, FONTS)
    
    def test_fonts_are_tuples(self):
        """All fonts should be tuples."""
        for name, font in FONTS.items():
            self.assertIsInstance(font, tuple, f"{name} should be a tuple")
            self.assertGreaterEqual(len(font), 2, f"{name} should have at least 2 elements")


class TestHelperFunctions(unittest.TestCase):
    """Tests for utility functions."""
    
    def test_format_player_symbol_x(self):
        """Should format X as player."""
        result = format_player_symbol('X')
        self.assertIn('X', result)
        self.assertIn('You', result)
    
    def test_format_player_symbol_o(self):
        """Should format O as computer."""
        result = format_player_symbol('O')
        self.assertIn('O', result)
        self.assertIn('Computer', result)
    
    def test_get_cell_color_x(self):
        """Should return player X color."""
        self.assertEqual(get_cell_color('X'), COLORS['player_x'])
    
    def test_get_cell_color_o(self):
        """Should return player O color."""
        self.assertEqual(get_cell_color('O'), COLORS['player_o'])
    
    def test_get_cell_color_empty(self):
        """Should return default color for empty/other."""
        self.assertEqual(get_cell_color(''), COLORS['text_primary'])
        self.assertEqual(get_cell_color(None), COLORS['text_primary'])


if __name__ == '__main__':
    unittest.main()
