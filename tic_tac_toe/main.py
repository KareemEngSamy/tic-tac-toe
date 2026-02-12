"""main.py - Entry point for Tic Tac Toe game."""

import tkinter as tk
from gui import TicTacToeGUI


def main():
    """Initialize and run the game."""
    root = tk.Tk()
    TicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
