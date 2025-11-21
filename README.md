# 🐍 Tron Worm - Multiplayer Snake Battle

A fast-paced multiplayer Tron-style worm game available in two versions:

- **🌐 Web Version** - Play in your browser! (RECOMMENDED)
- **💻 Terminal Version** - Classic CLI experience

## 🚀 Quick Start

### Web Version (Easiest!)

```bash
pip install websockets
python3 web_server.py
# Open http://localhost:8080 in your browser
```

**📖 See [WEB_README.md](WEB_README.md) for complete web version documentation**

### Terminal Version

```bash
python3 server.py          # Start server
python3 client.py localhost --name YourName  # Connect
```

---

## 🎮 Game Description

Tron Worm is a multiplayer snake game where 2-5 players compete in real-time over a local network. Each player controls a constantly moving "worm" that leaves a trail behind it. The goal is simple: avoid crashing into walls, your own trail, or other players' trails. Last worm alive wins the round!

## ✨ Features

### Core Gameplay
- **2-5 players** simultaneously over LAN
- **Real-time multiplayer** with low latency
- **Continuous movement** - your worm never stops!
- **Death on collision** - walls, own trail, or other players = death
- **Round-based scoring** - multiple rounds with score tracking

### Technical Features
- **Terminal UI** using curses with colorful ASCII graphics
- **TCP/IP networking** - one player hosts, others join
- **30 FPS** smooth rendering
- **Lobby system** with ready-up mechanism
- **Countdown** before each round (3...2...1...GO!)
- **Score tracking** across multiple rounds
- **Graceful disconnect handling**
- **Configurable settings** (grid size, port, etc.)

### Controls
- **Arrow Keys** or **WASD** - Control worm direction
- **Space** - Ready up in lobby / Ready for next round
- **Q** - Quit game

## 📋 Requirements

- **Python 3.6+**
- **Linux** (tested on Ubuntu, should work on most Unix-like systems)
- **Terminal** with color support
- **Local network** for multiplayer

## 🚀 Installation

### 1. Clone or download this repository

```bash
cd expert-broccoli
```

### 2. No additional dependencies needed!

The game uses only Python standard library modules:
- `socket` - networking
- `threading` - concurrent connections
- `curses` - terminal UI
- `json`, `struct`, `time`, `argparse` - utilities

All of these are included with Python by default on Linux.

### 3. Make scripts executable (optional)

```bash
chmod +x server.py client.py
```

## 🎯 How to Play

### Step 1: Start the Server

One player needs to host the game server. On the host machine:

```bash
python3 server.py
```

This will start the server on `0.0.0.0:9999` (accessible from any network interface).

**Server options:**
```bash
python3 server.py --host 0.0.0.0 --port 9999 --width 80 --height 40
```

- `--host` - Server host address (default: 0.0.0.0)
- `--port` - Server port (default: 9999)
- `--width` - Grid width (default: 80)
- `--height` - Grid height (default: 40)

**The server will display:**
```
🎮 Tron Worm Server started on 0.0.0.0:9999
📊 Grid size: 80x40
👥 Max players: 5
⏱️  Target FPS: 30

Waiting for players to connect...
```

### Step 2: Find the Server IP

On the host machine, find the local IP address:

```bash
hostname -I
# or
ip addr show
```

Look for an address like `192.168.1.100` on your local network.

### Step 3: Connect Clients

Each player runs the client and connects to the server:

```bash
python3 client.py 192.168.1.100
```

Replace `192.168.1.100` with the actual server IP address.

**Client options:**
```bash
python3 client.py 192.168.1.100 --port 9999 --name "YourName"
```

- First argument: Server hostname/IP (required)
- `--port` - Server port (default: 9999)
- `--name` - Your player name (will prompt if not provided)

### Step 4: Ready Up and Play!

1. **Lobby**: Players see the lobby screen with all connected players
2. **Ready Up**: Each player presses **SPACE** to ready up (✓ appears next to name)
3. **Countdown**: When all players are ready, a 3-2-1-GO countdown begins
4. **Play**: Control your worm with arrow keys or WASD
5. **Round End**: Winner is announced, scores displayed
6. **Next Round**: Press **SPACE** to ready for another round

## 🎨 Game Screen

```
═══════════════════════════════════════════════════════════════════════
║                                                                       ║
║  ●●●●●                                                               ║
║      ●                                                                ║
║      ●                                                                ║
║      ●                                              ▓▓▓▓●            ║
║                                                         ▓            ║
║                                                         ▓            ║
║                                                         ▓            ║
║                                                                       ║
║                   ░░░                                                ║
║                   ░                                                  ║
║               ●●●●░                                                  ║
║                                                                       ║
═══════════════════════════════════════════════════════════════════════
Round: 3    Speed: 12.5
Scores: Alice:2  Bob:1  Charlie:0
```

Each player gets a unique color and character!

## 🏆 Gameplay Tips

1. **Don't Reverse** - You can't reverse direction (prevents instant death)
2. **Speed Increases** - Game gets faster over time, stay alert!
3. **Corner Strategy** - Use corners to trap opponents
4. **Open Space** - Stay in open areas early game
5. **Wall Riding** - Advanced: ride along walls for control

## 🔧 Configuration

Edit `config.py` to customize game settings:

```python
# Network settings
DEFAULT_PORT = 9999
MAX_PLAYERS = 5
MIN_PLAYERS = 2

# Game settings
DEFAULT_GRID_WIDTH = 80
DEFAULT_GRID_HEIGHT = 40
DEFAULT_FPS = 30

# Worm settings
INITIAL_SPEED = 10  # Moves per second
SPEED_INCREMENT = 0.5
MAX_SPEED = 20
```

## 🐛 Troubleshooting

### "setupterm: could not find terminfo database"
This error occurs when curses can't find terminal information. **Quick fixes:**

1. **Set TERM environment variable:**
   ```bash
   export TERM=xterm-256color
   python3 client.py localhost
   ```

2. **Install ncurses terminfo database:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ncurses-base ncurses-bin

   # Fedora/RHEL
   sudo dnf install ncurses

   # Alpine Linux
   apk add ncurses-terminfo
   ```

3. **Check your TERM variable:**
   ```bash
   echo $TERM
   # Should show: xterm, xterm-256color, screen, etc.
   # If empty, set it: export TERM=xterm
   ```

4. **For Docker/minimal environments:**
   - Make sure `ncurses-base` package is installed in your container
   - Add to Dockerfile: `RUN apt-get install -y ncurses-base` (Debian/Ubuntu)

### "Connection refused"
- Make sure the server is running
- Check the IP address is correct
- Verify firewall isn't blocking port 9999
- Ensure both machines are on the same network

### Terminal too small
- Resize your terminal to at least 80x40
- Or use smaller grid: `python3 server.py --width 60 --height 30`

### Choppy gameplay
- Check network latency
- Reduce grid size for better performance
- Close other network applications

### Colors not showing
- Make sure your terminal supports colors
- Try a different terminal emulator (gnome-terminal, konsole, etc.)

## 🌐 Network Setup

### Playing on Same Machine (Testing)
```bash
# Terminal 1: Server
python3 server.py

# Terminal 2: Client 1
python3 client.py localhost

# Terminal 3: Client 2
python3 client.py localhost
```

### Playing on Local Network
```bash
# Host machine: Start server
python3 server.py

# Find host IP
hostname -I

# Other machines: Connect to host
python3 client.py 192.168.1.100
```

### Firewall Configuration
If connections fail, allow port 9999:

```bash
# Ubuntu/Debian
sudo ufw allow 9999/tcp

# Fedora/RHEL
sudo firewall-cmd --add-port=9999/tcp
```

## 📁 Project Structure

```
expert-broccoli/
├── server.py       # Game server (host runs this)
├── client.py       # Game client (players run this)
├── game.py         # Core game logic (worm movement, collisions)
├── renderer.py     # Terminal rendering with curses
├── protocol.py     # Network message protocol
├── config.py       # Game configuration and constants
└── README.md       # This file
```

## 🔨 Architecture

**Server-Authoritative Model:**
- Server controls all game logic and state
- Clients send input, receive game state
- Server broadcasts state to all clients 30 times/second
- Prevents cheating, ensures consistency

**Networking:**
- Length-prefixed JSON messages over TCP
- Reliable delivery with automatic reconnection handling
- Low latency optimized for real-time gameplay

**Threading:**
- Server: One thread per client + game loop thread
- Client: Receive thread + main rendering/input thread

## 🎓 Code Overview

### Key Classes

**`GameState` (game.py)**
- Manages overall game state
- Tracks all worms, scores, and game phase
- Handles collision detection and win conditions

**`Worm` (game.py)**
- Represents individual player's worm
- Stores position, direction, trail
- Handles movement and direction changes

**`Renderer` (renderer.py)**
- Curses-based terminal rendering
- Different screens for lobby, countdown, gameplay, round end
- Colorful ASCII graphics

**`GameServer` (server.py)**
- TCP server handling multiple clients
- Game loop running at target FPS
- Broadcasts state to all connected clients

**`GameClient` (client.py)**
- Connects to server
- Handles input and rendering
- Receives and applies game state updates

## 🚧 Future Enhancements

Ideas for extending the game:

- **Power-ups**: Speed boost, invincibility, trail erase
- **Game modes**: Team mode, time limit, elimination
- **Spectator mode**: Watch after elimination
- **Replay system**: Review last round
- **Leaderboard**: Persistent stats across games
- **Sound effects**: Terminal beep on events
- **AI players**: Practice against bots
- **Custom maps**: Obstacles and barriers

## 📝 License

This is a learning project - feel free to modify and share!

## 🙏 Credits

Inspired by:
- **Tron** (1982 film) - Light cycle battles
- **Snake** - Classic arcade game
- **Achtung, die Kurve!** - Multiplayer worm game

---

**Have fun and may the best worm win! 🏆🐍**
