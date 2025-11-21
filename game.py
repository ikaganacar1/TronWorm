"""
Core game logic for Tron Worm
"""

import time
from collections import deque
from config import *


class Worm:
    """Represents a player's worm"""

    def __init__(self, player_id, name, start_x, start_y, direction, color_id):
        self.player_id = player_id
        self.name = name
        self.direction = direction
        self.alive = True
        self.color_id = color_id
        self.char = WORM_CHARS[color_id % len(WORM_CHARS)]

        # Worm body is a list of (x, y) coordinates
        # Head is at index 0
        self.body = deque([(start_x, start_y)])
        self.trail = set()  # Set of all positions ever occupied
        self.trail.add((start_x, start_y))

    def get_head(self):
        """Get the head position"""
        return self.body[0]

    def set_direction(self, new_direction):
        """Change direction (prevent reversing)"""
        if new_direction in DIRECTIONS:
            # Don't allow reversing direction
            if OPPOSITE_DIRS.get(self.direction) != new_direction:
                self.direction = new_direction

    def move(self):
        """Move the worm one step in current direction"""
        if not self.alive:
            return

        head_x, head_y = self.get_head()
        dx, dy = DIRECTIONS[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # Add new head position
        self.body.appendleft(new_head)
        self.trail.add(new_head)

    def get_next_position(self):
        """Get the next position without moving"""
        head_x, head_y = self.get_head()
        dx, dy = DIRECTIONS[self.direction]
        return (head_x + dx, head_y + dy)

    def die(self):
        """Mark worm as dead"""
        self.alive = False

    def to_dict(self):
        """Convert worm to dictionary for network transmission"""
        return {
            'player_id': self.player_id,
            'name': self.name,
            'direction': self.direction,
            'alive': self.alive,
            'color_id': self.color_id,
            'char': self.char,
            'body': list(self.body),
            'trail': list(self.trail)
        }

    @staticmethod
    def from_dict(data):
        """Create worm from dictionary"""
        worm = Worm(
            data['player_id'],
            data['name'],
            0, 0,  # Will be overwritten
            data['direction'],
            data['color_id']
        )
        worm.alive = data['alive']
        worm.char = data['char']
        worm.body = deque(data['body'])
        worm.trail = set(tuple(pos) for pos in data['trail'])
        return worm


class GameState:
    """Manages the game state"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.worms = {}  # player_id -> Worm
        self.state = STATE_LOBBY
        self.ready_players = set()
        self.scores = {}  # player_id -> score
        self.round_number = 0
        self.game_start_time = None
        self.current_speed = INITIAL_SPEED
        self.countdown_start = None
        self.last_winner = None
        self.move_count = 0  # Track moves in current round

    def add_player(self, player_id, name):
        """Add a new player to the game"""
        if len(self.worms) >= MAX_PLAYERS:
            return False

        # Assign starting position and direction
        color_id = len(self.worms)
        start_positions = [
            (10, 10, 'RIGHT'),
            (self.width - 10, 10, 'LEFT'),
            (10, self.height - 10, 'UP'),
            (self.width - 10, self.height - 10, 'UP'),
            (self.width // 2, self.height // 2, 'RIGHT'),
        ]

        if color_id < len(start_positions):
            x, y, direction = start_positions[color_id]
        else:
            x, y, direction = self.width // 2, self.height // 2, 'RIGHT'

        worm = Worm(player_id, name, x, y, direction, color_id)
        self.worms[player_id] = worm
        self.scores[player_id] = 0
        return True

    def remove_player(self, player_id):
        """Remove a player from the game"""
        if player_id in self.worms:
            del self.worms[player_id]
        if player_id in self.ready_players:
            self.ready_players.remove(player_id)
        if player_id in self.scores:
            del self.scores[player_id]

    def set_player_ready(self, player_id, ready=True):
        """Mark a player as ready"""
        if ready:
            self.ready_players.add(player_id)
        else:
            self.ready_players.discard(player_id)

    def all_players_ready(self):
        """Check if all players are ready"""
        if len(self.worms) < MIN_PLAYERS:
            return False
        return len(self.ready_players) == len(self.worms)

    def start_countdown(self):
        """Start the countdown before game begins"""
        self.state = STATE_COUNTDOWN
        self.countdown_start = time.time()

    def start_round(self):
        """Start a new round"""
        self.state = STATE_PLAYING
        self.round_number += 1
        self.game_start_time = time.time()
        self.current_speed = INITIAL_SPEED
        self.ready_players.clear()
        self.move_count = 0  # Reset move counter

        # Reset all worms
        color_id = 0
        start_positions = [
            (10, 10, 'RIGHT'),
            (self.width - 10, 10, 'LEFT'),
            (10, self.height - 10, 'UP'),
            (self.width - 10, self.height - 10, 'UP'),
            (self.width // 2, self.height // 2, 'RIGHT'),
        ]

        for player_id, worm in self.worms.items():
            if color_id < len(start_positions):
                x, y, direction = start_positions[color_id]
            else:
                x, y, direction = self.width // 2, self.height // 2, 'RIGHT'

            # Completely reset worm state
            worm.body = deque([(x, y)])
            worm.trail = set()  # Clear trail first
            worm.trail.add((x, y))  # Then add starting position
            worm.direction = direction
            worm.alive = True
            color_id += 1

    def update(self):
        """Update game state (move worms, check collisions)"""
        if self.state != STATE_PLAYING:
            return

        # Update speed based on time
        if self.game_start_time:
            elapsed = time.time() - self.game_start_time
            self.current_speed = min(
                INITIAL_SPEED + (elapsed / 10) * SPEED_INCREMENT,
                MAX_SPEED
            )

        # Check collisions BEFORE moving (check where worms will move to)
        self._check_collisions()

        # Move all living worms (only if they survived collision check)
        for worm in self.worms.values():
            if worm.alive:
                worm.move()

        self.move_count += 1

        # Check win condition (but not on first few moves to avoid instant end)
        # Wait at least 3 moves to let worms separate from start positions
        if self.move_count >= 3:
            alive_worms = [w for w in self.worms.values() if w.alive]
            if len(alive_worms) <= 1:
                self._end_round()

    def _check_collisions(self):
        """Check for collisions with walls and trails"""
        for worm in self.worms.values():
            if not worm.alive:
                continue

            # Get where the worm WILL move to
            next_x, next_y = worm.get_next_position()

            # Check wall collision
            if (next_x < 0 or next_x >= self.width or
                    next_y < 0 or next_y >= self.height):
                worm.die()
                continue

            # Check collision with own trail (before moving there)
            if (next_x, next_y) in worm.trail:
                worm.die()
                continue

            # Check collision with other worms' trails
            for other_worm in self.worms.values():
                if other_worm.player_id == worm.player_id:
                    continue
                # Check if next position collides with other worm's trail
                if (next_x, next_y) in other_worm.trail:
                    worm.die()
                    break

    def _end_round(self):
        """End the current round"""
        self.state = STATE_ROUND_END

        # Award point to winner
        alive_worms = [w for w in self.worms.values() if w.alive]
        if len(alive_worms) == 1:
            winner = alive_worms[0]
            self.scores[winner.player_id] += 1
            self.last_winner = winner.name
        else:
            self.last_winner = "Draw"

    def handle_input(self, player_id, direction):
        """Handle player input"""
        if player_id in self.worms and self.state == STATE_PLAYING:
            self.worms[player_id].set_direction(direction)

    def to_dict(self):
        """Convert game state to dictionary for network transmission"""
        return {
            'width': self.width,
            'height': self.height,
            'worms': {pid: worm.to_dict() for pid, worm in self.worms.items()},
            'state': self.state,
            'ready_players': list(self.ready_players),
            'scores': self.scores,
            'round_number': self.round_number,
            'current_speed': self.current_speed,
            'countdown_start': self.countdown_start,
            'last_winner': self.last_winner,
            'move_count': self.move_count
        }

    @staticmethod
    def from_dict(data):
        """Create game state from dictionary"""
        game = GameState(data['width'], data['height'])
        game.worms = {
            pid: Worm.from_dict(worm_data)
            for pid, worm_data in data['worms'].items()
        }
        game.state = data['state']
        game.ready_players = set(data['ready_players'])
        game.scores = data['scores']
        game.round_number = data['round_number']
        game.current_speed = data['current_speed']
        game.countdown_start = data['countdown_start']
        game.last_winner = data.get('last_winner')
        game.move_count = data.get('move_count', 0)
        return game
