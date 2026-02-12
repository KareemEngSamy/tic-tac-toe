"""gui.py - Tkinter GUI for Tic Tac Toe.

Fully responsive layout using grid geometry manager with weights.
Scales correctly on maximize, minimize-restore, and manual resize.
"""

import random
import tkinter as tk
from typing import Optional

from game_logic import TicTacToeGame, NoDrawGame
from ai_easy import get_easy_move, get_easy_move_no_draw
from ai_medium import get_medium_move, get_medium_move_no_draw
from ai_hard import get_hard_move, get_hard_move_no_draw
from utils import (Difficulty, GameMode, DIFFICULTY_NAMES, DIFFICULTY_DESCRIPTIONS,
                   GAME_MODE_NAMES, GAME_MODE_DESCRIPTIONS, COLORS, FONTS,
                   get_cell_color)


class TicTacToeGUI:
    """Main GUI class — handles all screens and user interactions."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.geometry("620x720")
        self.root.minsize(420, 520)
        self.root.resizable(True, True)
        self.root.configure(bg=COLORS['background'])

        self.score = {'wins': 0, 'losses': 0, 'draws': 0}
        self.game: Optional[TicTacToeGame] = None
        self.game_mode: Optional[GameMode] = None
        self.difficulty: Optional[Difficulty] = None
        self.cells: list = []
        self.ai_thinking: bool = False
        self.animation_id: Optional[str] = None

        self._center_window()

        # Root grid: one cell that expands
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.main_container = tk.Frame(root, bg=COLORS['background'])
        self.main_container.grid(row=0, column=0, sticky='nsew',
                                 padx=18, pady=18)
        self.main_container.columnconfigure(0, weight=1)

        self._show_mode_screen()

    # ────────────────── Helpers ──────────────────

    def _center_window(self) -> None:
        self.root.update_idletasks()
        w, h = 620, 720
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def _clear_container(self) -> None:
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.cells = []
        # Reset row weights
        for i in range(20):
            self.main_container.rowconfigure(i, weight=0)

    def _make_btn(self, parent, text, command, bg=None, fg=None,
                  font=None, padx=18, pady=8, **kw):
        """Shortcut for creating a styled flat button."""
        bg = bg or COLORS['btn_primary']
        fg = fg or COLORS['text_primary']
        font = font or FONTS['button']
        btn = tk.Button(parent, text=text, command=command, font=font,
                        bg=bg, fg=fg, activebackground=COLORS['btn_primary_hover'],
                        activeforeground=fg, relief='flat', bd=0,
                        padx=padx, pady=pady, cursor='hand2', **kw)
        return btn

    # ──────────────── MODE SELECTION ────────────────

    def _show_mode_screen(self) -> None:
        """Show game mode selection (Normal / No Draw)."""
        self._clear_container()

        # Row 0 — title block
        self.main_container.rowconfigure(0, weight=0)
        title_frame = tk.Frame(self.main_container, bg=COLORS['background'])
        title_frame.grid(row=0, column=0, sticky='ew', pady=(10, 0))

        tk.Label(title_frame, text="TIC TAC TOE",
                 font=FONTS['title'], fg=COLORS['primary'],
                 bg=COLORS['background']).pack(anchor='center')
        tk.Label(title_frame, text="Choose Game Mode",
                 font=FONTS['subtitle'], fg=COLORS['text_secondary'],
                 bg=COLORS['background']).pack(anchor='center', pady=(4, 0))

        # Row 1 — score (only if games played)
        if sum(self.score.values()) > 0:
            self.main_container.rowconfigure(1, weight=0)
            self._create_score_bar(row=1)
        else:
            self.main_container.rowconfigure(1, weight=0)

        # Row 2 — mode cards (expandable)
        self.main_container.rowconfigure(2, weight=1)
        cards = tk.Frame(self.main_container, bg=COLORS['background'])
        cards.grid(row=2, column=0, sticky='nsew', pady=10)
        cards.columnconfigure(0, weight=1)

        mode_cfg = {
            GameMode.NORMAL:  {'icon': 'Classic', 'color': '#4ade80',
                               'subtitle': 'Standard Rules'},
            GameMode.NO_DRAW: {'icon': 'No Draw', 'color': '#a78bfa',
                               'subtitle': 'Marks Cycle — No Draws!'},
        }

        for idx, mode in enumerate(GameMode):
            cards.rowconfigure(idx, weight=1)
            cfg = mode_cfg[mode]
            self._create_mode_card(cards, idx, mode, cfg)

    def _create_mode_card(self, parent, row, mode, cfg):
        """Create a clickable mode card that fills available space."""
        color = cfg['color']

        card = tk.Frame(parent, bg=COLORS['surface'],
                        highlightbackground=color, highlightthickness=2)
        card.grid(row=row, column=0, sticky='nsew', pady=6, padx=4)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(0, weight=1)

        inner = tk.Frame(card, bg=COLORS['surface'])
        inner.grid(row=0, column=0, sticky='nsew', padx=20, pady=14)
        inner.columnconfigure(0, weight=1)

        lbl_name = tk.Label(inner, text=cfg['icon'],
                            font=('Segoe UI', 22, 'bold'), fg=color,
                            bg=COLORS['surface'])
        lbl_name.pack(anchor='center')

        lbl_sub = tk.Label(inner, text=cfg['subtitle'],
                           font=FONTS['small'], fg=COLORS['text_secondary'],
                           bg=COLORS['surface'])
        lbl_sub.pack(anchor='center', pady=(2, 0))

        lbl_desc = tk.Label(inner, text=GAME_MODE_DESCRIPTIONS[mode],
                            font=('Segoe UI', 10), fg=COLORS['text_secondary'],
                            bg=COLORS['surface'])
        lbl_desc.pack(anchor='center', pady=(2, 0))

        # Click + hover bindings
        widgets = [card, inner, lbl_name, lbl_sub, lbl_desc]

        def on_click(e, m=mode):
            self.game_mode = m
            self._show_difficulty_screen()

        def on_enter(e):
            for w in widgets:
                w.configure(bg=COLORS['surface_alt'])

        def on_leave(e):
            for w in widgets:
                w.configure(bg=COLORS['surface'])

        for w in widgets:
            w.bind('<Button-1>', on_click)
            w.bind('<Enter>', on_enter)
            w.bind('<Leave>', on_leave)
            w.configure(cursor='hand2')

    # ──────────────── DIFFICULTY SELECTION ────────────────

    def _show_difficulty_screen(self) -> None:
        self._clear_container()

        # Row 0 — title
        self.main_container.rowconfigure(0, weight=0)
        title_frame = tk.Frame(self.main_container, bg=COLORS['background'])
        title_frame.grid(row=0, column=0, sticky='ew', pady=(10, 0))

        tk.Label(title_frame, text="TIC TAC TOE",
                 font=FONTS['title'], fg=COLORS['primary'],
                 bg=COLORS['background']).pack(anchor='center')

        # Mode badge
        mode_colors = {GameMode.NORMAL: "#4ade80", GameMode.NO_DRAW: "#a78bfa"}
        mc = mode_colors.get(self.game_mode, COLORS['primary'])
        badge = tk.Label(title_frame,
                         text=f"  {GAME_MODE_NAMES[self.game_mode]}  ",
                         font=FONTS['badge'], fg='#0f172a', bg=mc)
        badge.pack(anchor='center', pady=(6, 0))

        tk.Label(title_frame, text="Choose Difficulty",
                 font=FONTS['subtitle'], fg=COLORS['text_secondary'],
                 bg=COLORS['background']).pack(anchor='center', pady=(6, 0))

        # Row 1 — score
        if sum(self.score.values()) > 0:
            self.main_container.rowconfigure(1, weight=0)
            self._create_score_bar(row=1)

        # Row 2 — difficulty cards
        self.main_container.rowconfigure(2, weight=1)
        cards = tk.Frame(self.main_container, bg=COLORS['background'])
        cards.grid(row=2, column=0, sticky='nsew', pady=10)
        cards.columnconfigure(0, weight=1)

        diff_cfg = {
            Difficulty.EASY:   {'color': '#4ade80', 'label': 'Easy'},
            Difficulty.MEDIUM: {'color': '#fbbf24', 'label': 'Medium'},
            Difficulty.HARD:   {'color': '#f87171', 'label': 'Hard'},
        }

        for idx, diff in enumerate(Difficulty):
            cards.rowconfigure(idx, weight=1)
            cfg = diff_cfg[diff]
            self._create_diff_card(cards, idx, diff, cfg)

        # Row 3 — back button
        self.main_container.rowconfigure(3, weight=0)
        back = self._make_btn(self.main_container, "Back to Modes",
                              self._show_mode_screen,
                              bg=COLORS['btn_secondary'],
                              fg=COLORS['text_secondary'])
        back.grid(row=3, column=0, pady=(0, 6))

    def _create_diff_card(self, parent, row, diff, cfg):
        color = cfg['color']
        card = tk.Frame(parent, bg=COLORS['surface'],
                        highlightbackground=color, highlightthickness=2)
        card.grid(row=row, column=0, sticky='nsew', pady=5, padx=4)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(0, weight=1)

        inner = tk.Frame(card, bg=COLORS['surface'])
        inner.grid(row=0, column=0, sticky='nsew', padx=20, pady=12)
        inner.columnconfigure(0, weight=1)

        lbl_name = tk.Label(inner, text=cfg['label'],
                            font=('Segoe UI', 20, 'bold'), fg=color,
                            bg=COLORS['surface'])
        lbl_name.pack(anchor='center')

        lbl_desc = tk.Label(inner, text=DIFFICULTY_DESCRIPTIONS[diff],
                            font=FONTS['small'], fg=COLORS['text_secondary'],
                            bg=COLORS['surface'])
        lbl_desc.pack(anchor='center', pady=(2, 0))

        widgets = [card, inner, lbl_name, lbl_desc]

        def on_click(e, d=diff):
            self._start_game(d)

        def on_enter(e):
            for w in widgets:
                w.configure(bg=COLORS['surface_alt'])

        def on_leave(e):
            for w in widgets:
                w.configure(bg=COLORS['surface'])

        for w in widgets:
            w.bind('<Button-1>', on_click)
            w.bind('<Enter>', on_enter)
            w.bind('<Leave>', on_leave)
            w.configure(cursor='hand2')

    # ──────────────── SCORE BAR ────────────────

    def _create_score_bar(self, row: int) -> None:
        bar = tk.Frame(self.main_container, bg=COLORS['surface'])
        bar.grid(row=row, column=0, sticky='ew', pady=(8, 0), padx=4)
        bar.columnconfigure(0, weight=1)
        bar.columnconfigure(1, weight=0)
        bar.columnconfigure(2, weight=1)

        # Wins
        pf = tk.Frame(bar, bg=COLORS['surface'])
        pf.grid(row=0, column=0, padx=12, pady=8)
        tk.Label(pf, text="WINS", font=FONTS['score_label'],
                 fg=COLORS['win'], bg=COLORS['surface']).pack()
        tk.Label(pf, text=str(self.score['wins']),
                 font=FONTS['score_num'], fg=COLORS['win'],
                 bg=COLORS['surface']).pack()

        # Separator + draws
        sf = tk.Frame(bar, bg=COLORS['surface'])
        sf.grid(row=0, column=1, padx=8, pady=8)
        tk.Label(sf, text="vs", font=FONTS['small'],
                 fg=COLORS['text_secondary'], bg=COLORS['surface']).pack()
        tk.Label(sf, text=f"Draws: {self.score['draws']}",
                 font=('Segoe UI', 9), fg=COLORS['draw'],
                 bg=COLORS['surface']).pack()

        # Losses
        cf = tk.Frame(bar, bg=COLORS['surface'])
        cf.grid(row=0, column=2, padx=12, pady=8)
        tk.Label(cf, text="LOSSES", font=FONTS['score_label'],
                 fg=COLORS['danger'], bg=COLORS['surface']).pack()
        tk.Label(cf, text=str(self.score['losses']),
                 font=FONTS['score_num'], fg=COLORS['danger'],
                 bg=COLORS['surface']).pack()

    # ──────────────── GAME SCREEN ────────────────

    def _start_game(self, difficulty: Difficulty) -> None:
        self.difficulty = difficulty
        self.game = NoDrawGame() if self.game_mode == GameMode.NO_DRAW else TicTacToeGame()
        # Randomly decide who goes first
        self.computer_starts = random.choice([True, False])
        if self.computer_starts:
            self.game.current_player = 'O'
        self._show_game_screen()
        if self.computer_starts:
            self._make_ai_move()

    @property
    def _is_no_draw(self) -> bool:
        return self.game_mode == GameMode.NO_DRAW

    def _show_game_screen(self) -> None:
        self._clear_container()

        diff_colors = {
            Difficulty.EASY: '#4ade80',
            Difficulty.MEDIUM: '#fbbf24',
            Difficulty.HARD: '#f87171',
        }
        mode_colors = {
            GameMode.NORMAL: '#4ade80',
            GameMode.NO_DRAW: '#a78bfa',
        }

        # Row 0 — Badges
        self.main_container.rowconfigure(0, weight=0)
        badge_frame = tk.Frame(self.main_container, bg=COLORS['background'])
        badge_frame.grid(row=0, column=0, sticky='ew', pady=(6, 0))

        mc = mode_colors.get(self.game_mode, COLORS['primary'])
        dc = diff_colors.get(self.difficulty, COLORS['primary'])

        tk.Label(badge_frame,
                 text=f"  {GAME_MODE_NAMES[self.game_mode]}  ",
                 font=FONTS['badge'], fg='#0f172a', bg=mc).pack(side='left', padx=4)
        tk.Label(badge_frame,
                 text=f"  {DIFFICULTY_NAMES[self.difficulty]}  ",
                 font=FONTS['badge'], fg='#0f172a', bg=dc).pack(side='left', padx=4)

        # Row 1 — Score panel
        self.main_container.rowconfigure(1, weight=0)
        score_bar = tk.Frame(self.main_container, bg=COLORS['surface'])
        score_bar.grid(row=1, column=0, sticky='ew', pady=6, padx=4)
        score_bar.columnconfigure(0, weight=1)
        score_bar.columnconfigure(1, weight=0)
        score_bar.columnconfigure(2, weight=1)

        # YOU
        pf = tk.Frame(score_bar, bg=COLORS['surface'])
        pf.grid(row=0, column=0, padx=10, pady=6)
        tk.Label(pf, text="YOU (X)", font=FONTS['score_label'],
                 fg=COLORS['player_x'], bg=COLORS['surface']).pack()
        self.player_score_label = tk.Label(
            pf, text=str(self.score['wins']),
            font=FONTS['score_num'], fg=COLORS['player_x'],
            bg=COLORS['surface'])
        self.player_score_label.pack()

        # VS
        vf = tk.Frame(score_bar, bg=COLORS['surface'])
        vf.grid(row=0, column=1, padx=6, pady=6)
        tk.Label(vf, text="vs", font=FONTS['small'],
                 fg=COLORS['text_secondary'], bg=COLORS['surface']).pack()
        self.draws_label = tk.Label(
            vf, text=f"Draws: {self.score['draws']}",
            font=('Segoe UI', 9), fg=COLORS['draw'],
            bg=COLORS['surface'])
        self.draws_label.pack()

        # Computer
        cf = tk.Frame(score_bar, bg=COLORS['surface'])
        cf.grid(row=0, column=2, padx=10, pady=6)
        tk.Label(cf, text="Computer (O)", font=FONTS['score_label'],
                 fg=COLORS['player_o'], bg=COLORS['surface']).pack()
        self.computer_score_label = tk.Label(
            cf, text=str(self.score['losses']),
            font=FONTS['score_num'], fg=COLORS['player_o'],
            bg=COLORS['surface'])
        self.computer_score_label.pack()

        # Row 2 — Status
        self.main_container.rowconfigure(2, weight=0)
        self.status_label = tk.Label(
            self.main_container, text="Your turn!",
            font=FONTS['status'], fg=COLORS['player_x'],
            bg=COLORS['background'])
        self.status_label.grid(row=2, column=0, sticky='ew', pady=(8, 6))

        # Row 3 — Board (expandable!)
        self.main_container.rowconfigure(3, weight=1)
        self._create_board(row=3)

        # Row 4 — Controls
        self.main_container.rowconfigure(4, weight=0)
        self._create_controls(row=4)

    # ──────────────── BOARD ────────────────

    def _create_board(self, row: int) -> None:
        """Create a 3×3 board using grid — cells expand equally."""
        outer = tk.Frame(self.main_container, bg=COLORS['background'])
        outer.grid(row=row, column=0, sticky='nsew', padx=10, pady=4)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        # Board frame centered inside outer
        board = tk.Frame(outer, bg=COLORS['primary'])
        board.place(relx=0.5, rely=0.5, anchor='center',
                    relwidth=0.95, relheight=0.95)

        for r in range(3):
            board.rowconfigure(r, weight=1)
        for c in range(3):
            board.columnconfigure(c, weight=1)

        self.cells = []
        for i in range(9):
            r, c = divmod(i, 3)
            btn = tk.Button(board, text='', font=FONTS['cell'],
                            bg=COLORS['cell_bg'], fg=COLORS['text_primary'],
                            activebackground=COLORS['cell_hover'],
                            relief='flat', bd=0,
                            command=lambda p=i: self._on_cell_click(p))
            btn.grid(row=r, column=c, sticky='nsew', padx=2, pady=2)
            self.cells.append(btn)

            btn.bind('<Enter>', lambda e, b=btn: self._on_cell_hover(b, True))
            btn.bind('<Leave>', lambda e, b=btn: self._on_cell_hover(b, False))

        # Bind resize to update font sizes
        board.bind('<Configure>', self._on_board_resize)
        self._board_frame = board

    def _on_board_resize(self, event) -> None:
        """Dynamically scale cell font size to match board dimensions."""
        if not self.cells:
            return
        cell_h = event.height // 3
        cell_w = event.width // 3
        size = max(12, min(cell_h, cell_w) // 3)
        font = ('Segoe UI', size, 'bold')
        for btn in self.cells:
            btn.configure(font=font)

    def _on_cell_hover(self, btn: tk.Button, entering: bool) -> None:
        if btn['text'] == '' and not self.ai_thinking:
            if self.game and not self.game.game_over:
                btn.configure(bg=COLORS['cell_hover'] if entering
                              else COLORS['cell_bg'])

    def _on_cell_click(self, position: int) -> None:
        if self.ai_thinking or self.game.game_over or self.game.current_player != 'X':
            return

        # No Draw: allow clicking on own oldest mark (it will be removed)
        if self._is_no_draw and self.game.board[position] is not None:
            oldest = self.game.get_oldest_mark('X')
            if position != oldest:
                return

        if self.game.make_move(position):
            self._update_board()
            self._update_status()
            if self.game.game_over:
                if self.game.winner:
                    self._highlight_winner()
            else:
                self._make_ai_move()

    # ──────────────── AI ────────────────

    def _make_ai_move(self) -> None:
        self.ai_thinking = True
        self._update_status()
        self.root.after(400, self._execute_ai_move)

    def _execute_ai_move(self) -> None:
        board = self.game.get_board_copy()

        if self._is_no_draw:
            xm = list(self.game.x_moves)
            om = list(self.game.o_moves)
            if self.difficulty == Difficulty.EASY:
                move = get_easy_move_no_draw(board, xm, om)
            elif self.difficulty == Difficulty.MEDIUM:
                move = get_medium_move_no_draw(board, xm, om)
            else:
                move = get_hard_move_no_draw(board, xm, om)
        else:
            if self.difficulty == Difficulty.EASY:
                move = get_easy_move(board)
            elif self.difficulty == Difficulty.MEDIUM:
                move = get_medium_move(board)
            else:
                move = get_hard_move(board)

        if move is not None:
            self.game.make_move(move)

        self.ai_thinking = False
        self._update_board()
        self._update_status()

        if self.game.game_over and self.game.winner:
            self._highlight_winner()

    # ──────────────── BOARD UPDATE ────────────────

    def _update_board(self) -> None:
        oldest_x = oldest_o = None
        if self._is_no_draw:
            oldest_x = self.game.get_oldest_mark('X')
            oldest_o = self.game.get_oldest_mark('O')

        for i, btn in enumerate(self.cells):
            value = self.game.board[i]
            if value:
                fg = get_cell_color(value)
                btn.configure(text=value, fg=fg,
                              state='disabled', disabledforeground=fg)
                # Subtle tint for oldest marks in No Draw
                if (self._is_no_draw and not self.game.game_over
                        and ((value == 'X' and i == oldest_x)
                             or (value == 'O' and i == oldest_o))):
                    btn.configure(bg=COLORS['oldest_mark'])
                else:
                    btn.configure(bg=COLORS['cell_bg'])
            else:
                btn.configure(text='', state='normal', bg=COLORS['cell_bg'])

    def _update_status(self) -> None:
        if self.ai_thinking:
            self.status_label.configure(text="Computer thinking...",
                                        fg=COLORS['player_o'])
            self._animate_thinking()
        elif self.game.game_over:
            if self.animation_id:
                self.root.after_cancel(self.animation_id)
                self.animation_id = None

            if self.game.winner == 'X':
                self.score['wins'] += 1
                self.status_label.configure(text="YOU WIN!",
                                            fg=COLORS['win'])
                self._celebrate_win()
            elif self.game.winner == 'O':
                self.score['losses'] += 1
                self.status_label.configure(text="Computer Wins!",
                                            fg=COLORS['danger'])
            else:
                self.score['draws'] += 1
                self.status_label.configure(text="It's a Draw!",
                                            fg=COLORS['draw'])
            self._update_score_display()
        else:
            if self.animation_id:
                self.root.after_cancel(self.animation_id)
                self.animation_id = None
            if self.game.current_player == 'X':
                self.status_label.configure(text="Your turn!",
                                            fg=COLORS['player_x'])
            else:
                self.status_label.configure(text="Computer's turn...",
                                            fg=COLORS['player_o'])

    def _update_score_display(self) -> None:
        if hasattr(self, 'player_score_label'):
            self.player_score_label.configure(text=str(self.score['wins']))
        if hasattr(self, 'computer_score_label'):
            self.computer_score_label.configure(text=str(self.score['losses']))
        if hasattr(self, 'draws_label'):
            self.draws_label.configure(text=f"Draws: {self.score['draws']}")

    def _animate_thinking(self) -> None:
        if not self.ai_thinking:
            return
        current = self.status_label.cget('text')
        if current.endswith('...'):
            new = "Computer thinking"
        else:
            new = current + "."
        self.status_label.configure(text=new)
        self.animation_id = self.root.after(300, self._animate_thinking)

    def _celebrate_win(self) -> None:
        colors = [COLORS['win'], COLORS['player_x'],
                  COLORS['primary'], '#4ade80']

        def flash(count=0):
            if count < 6 and not self.ai_thinking:
                self.status_label.configure(fg=colors[count % len(colors)])
                self.root.after(200, lambda: flash(count + 1))
        flash()

    def _highlight_winner(self) -> None:
        combo = self.game.get_winning_combination()
        if combo:
            for i in combo:
                self.cells[i].configure(bg=COLORS['win'],
                                        disabledforeground='#0f172a')

    # ──────────────── CONTROLS ────────────────

    def _create_controls(self, row: int) -> None:
        controls = tk.Frame(self.main_container, bg=COLORS['background'])
        controls.grid(row=row, column=0, sticky='ew', pady=(10, 6))
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(2, weight=1)

        self._make_btn(controls, "Restart", self._restart_game,
                       bg=COLORS['btn_primary']).grid(
                           row=0, column=0, sticky='ew', padx=4)

        self._make_btn(controls, "Menu", self._show_mode_screen,
                       bg=COLORS['btn_secondary'],
                       fg=COLORS['text_secondary']).grid(
                           row=0, column=1, sticky='ew', padx=4)

        self._make_btn(controls, "Reset Score", self._reset_score,
                       bg=COLORS['secondary'],
                       fg=COLORS['text_secondary']).grid(
                           row=0, column=2, sticky='ew', padx=4)

    def _reset_score(self) -> None:
        self.score = {'wins': 0, 'losses': 0, 'draws': 0}
        self._update_score_display()

    def _restart_game(self) -> None:
        if not self.game:
            return
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.game.reset()
        self.ai_thinking = False
        # Randomly decide who goes first
        self.computer_starts = random.choice([True, False])
        if self.computer_starts:
            self.game.current_player = 'O'
        self._update_board()
        self._update_status()
        for cell in self.cells:
            cell.configure(bg=COLORS['cell_bg'], state='normal')
        if self.computer_starts:
            self._make_ai_move()
