"""
Terminal rendering using curses
"""

import curses
import time
from config import *


class Renderer:
    """Handles terminal rendering with curses"""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.setup_curses()

    def setup_curses(self):
        """Initialize curses settings"""
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(1)  # Non-blocking input
        self.stdscr.keypad(1)  # Enable keypad
        self.stdscr.timeout(0)  # Non-blocking getch

        # Initialize colors
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            for i, (name, color_num) in enumerate(COLORS):
                curses.init_pair(i + 1, color_num, -1)

    def clear(self):
        """Clear the screen"""
        self.stdscr.clear()

    def refresh(self):
        """Refresh the screen"""
        self.stdscr.refresh()

    def get_size(self):
        """Get terminal size"""
        height, width = self.stdscr.getmaxyx()
        return width, height

    def draw_border(self, width, height):
        """Draw game border"""
        try:
            # Top and bottom borders
            for x in range(width):
                self.stdscr.addch(0, x, '═')
                self.stdscr.addch(height - 1, x, '═')

            # Left and right borders
            for y in range(height):
                self.stdscr.addch(y, 0, '║')
                self.stdscr.addch(y, width - 1, '║')

            # Corners
            self.stdscr.addch(0, 0, '╔')
            self.stdscr.addch(0, width - 1, '╗')
            self.stdscr.addch(height - 1, 0, '╚')
            self.stdscr.addch(height - 1, width - 1, '╝')
        except curses.error:
            pass  # Ignore errors at screen edges

    def draw_text(self, y, x, text, color_pair=0, attr=curses.A_NORMAL):
        """Draw text at position"""
        try:
            if color_pair > 0:
                self.stdscr.addstr(y, x, text, curses.color_pair(color_pair) | attr)
            else:
                self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass  # Ignore errors at screen edges

    def draw_text_centered(self, y, text, color_pair=0, attr=curses.A_NORMAL):
        """Draw centered text"""
        width, _ = self.get_size()
        x = max(0, (width - len(text)) // 2)
        self.draw_text(y, x, text, color_pair, attr)

    def draw_worm(self, worm, offset_x=1, offset_y=1):
        """Draw a worm on the screen"""
        if not worm.alive:
            return

        color_pair = worm.color_id + 1

        # Draw trail
        for x, y in worm.trail:
            try:
                self.stdscr.addch(
                    y + offset_y,
                    x + offset_x,
                    worm.char,
                    curses.color_pair(color_pair)
                )
            except curses.error:
                pass

        # Draw head with brightness
        if worm.body:
            head_x, head_y = worm.body[0]
            try:
                self.stdscr.addch(
                    head_y + offset_y,
                    head_x + offset_x,
                    '●',
                    curses.color_pair(color_pair) | curses.A_BOLD
                )
            except curses.error:
                pass

    def render_lobby(self, game_state, player_id):
        """Render lobby screen"""
        self.clear()
        width, height = self.get_size()

        # Title
        self.draw_text_centered(2, "═══ TRON WORM ═══", attr=curses.A_BOLD)
        self.draw_text_centered(3, "Multiplayer Snake Battle", attr=curses.A_DIM)

        # Players list
        y = 6
        self.draw_text_centered(y, "PLAYERS:", attr=curses.A_BOLD)
        y += 2

        for worm in game_state.worms.values():
            ready_mark = "✓" if worm.player_id in game_state.ready_players else " "
            is_you = " (You)" if worm.player_id == player_id else ""
            player_text = f"[{ready_mark}] {worm.name}{is_you}"

            self.draw_text_centered(
                y,
                player_text,
                color_pair=worm.color_id + 1,
                attr=curses.A_BOLD
            )
            y += 1

        # Instructions
        y = height - 10
        self.draw_text_centered(y, f"Players: {len(game_state.worms)}/{MAX_PLAYERS}", attr=curses.A_DIM)
        y += 2
        self.draw_text_centered(y, "Press SPACE to ready up", attr=curses.A_BOLD)
        y += 1
        self.draw_text_centered(y, "Press Q to quit", attr=curses.A_DIM)

        if len(game_state.worms) >= MIN_PLAYERS:
            y += 2
            self.draw_text_centered(
                y,
                f"Waiting for {len(game_state.worms) - len(game_state.ready_players)} players...",
                attr=curses.A_BLINK
            )

        self.refresh()

    def render_countdown(self, game_state):
        """Render countdown screen"""
        if game_state.countdown_start is None:
            return

        self.clear()
        width, height = self.get_size()

        elapsed = time.time() - game_state.countdown_start
        remaining = max(0, COUNTDOWN_SECONDS - int(elapsed))

        if remaining > 0:
            countdown_text = str(remaining)
        else:
            countdown_text = "GO!"

        # Draw large countdown
        y = height // 2
        self.draw_text_centered(y, countdown_text, attr=curses.A_BOLD)

        # Draw player info
        y = height - 6
        for worm in game_state.worms.values():
            player_text = f"{worm.name}"
            self.draw_text_centered(y, player_text, color_pair=worm.color_id + 1)
            y += 1

        self.refresh()

    def render_game(self, game_state, player_id):
        """Render active game"""
        self.clear()

        # Draw border
        self.draw_border(game_state.width + 2, game_state.height + 2)

        # Draw all worms
        for worm in game_state.worms.values():
            self.draw_worm(worm, offset_x=1, offset_y=1)

        # Draw HUD
        y = game_state.height + 3
        self.draw_text(y, 2, f"Round: {game_state.round_number}", attr=curses.A_BOLD)
        self.draw_text(y, 20, f"Speed: {game_state.current_speed:.1f}", attr=curses.A_BOLD)

        # Draw scores
        y += 1
        score_text = "Scores: "
        for worm in game_state.worms.values():
            score = game_state.scores.get(worm.player_id, 0)
            status = "💀" if not worm.alive else ""
            score_text += f"{worm.name}:{score}{status}  "
        self.draw_text(y, 2, score_text[:game_state.width])

        self.refresh()

    def render_round_end(self, game_state, player_id):
        """Render round end screen"""
        self.clear()
        width, height = self.get_size()

        # Winner announcement
        if game_state.last_winner:
            self.draw_text_centered(
                height // 2 - 2,
                f"🏆 {game_state.last_winner} wins! 🏆",
                attr=curses.A_BOLD
            )

        # Scores
        y = height // 2 + 1
        self.draw_text_centered(y, "SCORES:", attr=curses.A_BOLD)
        y += 2

        # Sort by score
        sorted_worms = sorted(
            game_state.worms.values(),
            key=lambda w: game_state.scores.get(w.player_id, 0),
            reverse=True
        )

        for worm in sorted_worms:
            score = game_state.scores.get(worm.player_id, 0)
            score_text = f"{worm.name}: {score}"
            self.draw_text_centered(y, score_text, color_pair=worm.color_id + 1)
            y += 1

        # Instructions
        y = height - 5
        self.draw_text_centered(y, "Press SPACE for next round", attr=curses.A_BLINK)
        y += 1
        self.draw_text_centered(y, "Press Q to quit", attr=curses.A_DIM)

        self.refresh()

    def render(self, game_state, player_id):
        """Main render function"""
        if game_state.state == STATE_LOBBY:
            self.render_lobby(game_state, player_id)
        elif game_state.state == STATE_COUNTDOWN:
            self.render_countdown(game_state)
        elif game_state.state == STATE_PLAYING:
            self.render_game(game_state, player_id)
        elif game_state.state == STATE_ROUND_END:
            self.render_round_end(game_state, player_id)

    def show_error(self, message):
        """Show error message"""
        self.clear()
        width, height = self.get_size()
        self.draw_text_centered(height // 2, f"ERROR: {message}", attr=curses.A_BOLD)
        self.draw_text_centered(height // 2 + 2, "Press any key to exit...")
        self.refresh()
        self.stdscr.nodelay(0)
        self.stdscr.getch()

    def show_connecting(self, host, port):
        """Show connecting message"""
        self.clear()
        width, height = self.get_size()
        self.draw_text_centered(height // 2, f"Connecting to {host}:{port}...", attr=curses.A_BOLD)
        self.refresh()
