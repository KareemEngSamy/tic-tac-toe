"""
utils.py - Helper Functions and Constants

This module contains utility functions and constants used across
the Tic Tac Toe game. It centralizes common values and helper
functions to maintain consistency and reduce code duplication.
"""

from enum import Enum
from typing import Dict


class GameMode(Enum):
    """
    Enumeration of available game modes.
    """
    NORMAL = "normal"
    NO_DRAW = "no_draw"


# Display names for game modes
GAME_MODE_NAMES: Dict[GameMode, str] = {
    GameMode.NORMAL: "Normal 🎲",
    GameMode.NO_DRAW: "No Draw ♾️"
}

# Descriptions for game modes
GAME_MODE_DESCRIPTIONS: Dict[GameMode, str] = {
    GameMode.NORMAL: "Classic Tic Tac Toe rules.",
    GameMode.NO_DRAW: "Oldest marks removed after 3. No draws possible!"
}


class Difficulty(Enum):
    """
    Enumeration of available difficulty levels.
    
    Using an enum ensures type safety and prevents invalid
    difficulty values from being used.
    """
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# Display names for difficulty levels
DIFFICULTY_NAMES: Dict[Difficulty, str] = {
    Difficulty.EASY: "Easy 🌱",
    Difficulty.MEDIUM: "Medium 🎯",
    Difficulty.HARD: "Hard 🔥"
}

# Descriptions for difficulty levels
DIFFICULTY_DESCRIPTIONS: Dict[Difficulty, str] = {
    Difficulty.EASY: "Computer plays randomly.",
    Difficulty.MEDIUM: "Computer blocks and tries to win.",
    Difficulty.HARD: "Unbeatable AI (Minimax)."
}

# ── Professional color palette ──────────────────────────────────────
# Light-friendly theme: high contrast, readable text, modern look
COLORS = {
    # Layout
    'background': '#0f172a',       # Deep navy
    'surface': '#1e293b',          # Slate card background
    'surface_alt': '#334155',      # Lighter slate for hover
    # Accent
    'primary': '#818cf8',          # Bright indigo
    'secondary': '#475569',        # Muted slate for secondary buttons
    # Text  – high contrast on dark bg
    'text_primary': '#f1f5f9',     # Near-white
    'text_secondary': '#cbd5e1',   # Light slate 
    # Players
    'player_x': '#38bdf8',         # Sky blue 
    'player_o': '#fb923c',         # Warm orange 
    # States
    'win': '#4ade80',              # Bright green
    'draw': '#fbbf24',             # Amber
    'danger': '#f87171',           # Soft red
    # Board
    'board_bg': '#0f172a',         # Grid line color
    'cell_bg': '#1e293b',          # Normal cell
    'cell_hover': '#334155',       # Hovered empty cell
    'oldest_mark': '#3b2f1e',      # Subtle warm tint for oldest mark
    # Buttons
    'btn_primary': '#6366f1',      # Indigo button
    'btn_primary_hover': '#818cf8',
    'btn_secondary': '#334155',
    'btn_secondary_hover': '#475569',
}

FONTS = {
    'title': ('Segoe UI', 28, 'bold'),
    'subtitle': ('Segoe UI', 14),
    'button': ('Segoe UI', 13, 'bold'),
    'cell': ('Segoe UI', 42, 'bold'),
    'status': ('Segoe UI', 16, 'bold'),
    'small': ('Segoe UI', 11),
    'badge': ('Segoe UI', 10, 'bold'),
    'score_num': ('Segoe UI', 22, 'bold'),
    'score_label': ('Segoe UI', 9, 'bold'),
}


def format_player_symbol(player: str) -> str:
    """Return formatted player name."""
    return 'X (You)' if player == 'X' else 'O (Computer)'


def get_cell_color(value: str) -> str:
    """Return color for cell value (X, O, or empty)."""
    if value == 'X':
        return COLORS['player_x']
    elif value == 'O':
        return COLORS['player_o']
    return COLORS['text_primary']
