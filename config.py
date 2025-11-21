"""
Configuration and constants for Tron Worm game
"""

# Network settings
DEFAULT_PORT = 9999
DEFAULT_HOST = '0.0.0.0'
BUFFER_SIZE = 4096
MAX_PLAYERS = 5
MIN_PLAYERS = 2

# Game settings
DEFAULT_GRID_WIDTH = 160  # Wider field for better gameplay
DEFAULT_GRID_HEIGHT = 45  # Less tall, more wide
DEFAULT_FPS = 30
TICK_RATE = 1.0 / DEFAULT_FPS

# Worm settings
INITIAL_SPEED = 10  # Moves per second
SPEED_INCREMENT = 0.5  # Speed increase per 10 seconds
MAX_SPEED = 20
TRAIL_LENGTH = 30  # Smaller trail that fades quickly
TRAIL_BONUS_INCREASE = 50  # How much trail length increases when collecting bonus

# Bonus settings
MAX_BONUSES = 8  # Maximum number of bonuses on field at once
BONUS_RESPAWN_TIME = 5  # Seconds before new bonus spawns

# Countdown settings
COUNTDOWN_SECONDS = 3

# Player colors (for terminal rendering)
COLORS = [
    ('RED', 1),
    ('GREEN', 2),
    ('YELLOW', 3),
    ('BLUE', 4),
    ('MAGENTA', 5),
    ('CYAN', 6),
]

# Worm characters for different players (all solid blocks for clean UI)
WORM_CHARS = ['█', '█', '█', '█', '█']

# Direction vectors
DIRECTIONS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0)
}

# Opposite directions (for preventing reverse)
OPPOSITE_DIRS = {
    'UP': 'DOWN',
    'DOWN': 'UP',
    'LEFT': 'RIGHT',
    'RIGHT': 'LEFT'
}

# Game states
STATE_LOBBY = 'lobby'
STATE_COUNTDOWN = 'countdown'
STATE_PLAYING = 'playing'
STATE_ROUND_END = 'round_end'
STATE_GAME_OVER = 'game_over'

# Message types for network protocol
MSG_JOIN = 'join'
MSG_JOIN_ACK = 'join_ack'
MSG_READY = 'ready'
MSG_INPUT = 'input'
MSG_STATE = 'state'
MSG_DISCONNECT = 'disconnect'
MSG_ERROR = 'error'
MSG_CHAT = 'chat'
MSG_START_COUNTDOWN = 'start_countdown'
MSG_FORCE_START = 'force_start'  # Force start for solo/practice mode
