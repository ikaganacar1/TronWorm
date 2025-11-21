# 🐍 Tron Worm - Multiplayer Snake Battle

A fast-paced multiplayer Tron-style worm game where players compete to be the last one alive. Leave trails, dodge opponents, collect bonuses, and dominate the arena!

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.6+-green)
![Platform](https://img.shields.io/badge/platform-web%20%7C%20terminal-orange)

---

## 🎮 Game Overview

Control a constantly moving worm that leaves a trail behind it. Avoid crashing into walls, your own trail, or other players' trails. Collect golden bonuses to increase your trail length and gain an advantage. Last worm alive wins the round!

**Play locally or over the internet!**

---

## ✨ Features

### 🎯 Gameplay
- **Multiplayer or Solo** - 2-5 players online or practice alone
- **Real-time Action** - Smooth 30 FPS gameplay
- **Collectible Bonuses** - Golden orbs increase your trail length (+50)
- **Dynamic Difficulty** - Speed increases as the round progresses
- **Fading Trails** - Limited trail length keeps gameplay fast-paced
- **Large Arena** - 120x60 grid sized for modern displays

### 🌐 Connectivity
- **LAN Multiplayer** - Play with friends on local network
- **Remote Play** - Play over internet using ngrok or port forwarding
- **Browser-Based** - No installation needed for players
- **Cross-Platform** - Works on Windows, Mac, Linux

### 🎨 Technical
- **Web Version** - HTML5 Canvas with WebSockets (Recommended)
- **Terminal Version** - Classic CLI with curses (For terminal enthusiasts)
- **Server-Authoritative** - Fair gameplay, no cheating
- **Lobby System** - Ready-up mechanism with countdown
- **Score Tracking** - Multiple rounds with persistent scores

---

## 🚀 Quick Start

### Requirements

- **Python 3.6+**
- **pip** (Python package manager)

### Installation

1. **Clone or download this repository:**
   ```bash
   cd expert-broccoli
   ```

2. **Install dependencies:**
   ```bash
   pip install websockets
   ```

### Running the Game

#### 🌐 Web Version (Recommended)

**Start the server:**
```bash
python3 web_server.py
```

**Play the game:**
- Open your browser to: **http://localhost:8080**
- Enter your name and connect to: **ws://localhost:8765**
- Wait for friends to join or click "Start Solo Practice"

**Server options:**
```bash
python3 web_server.py --http-port 8080 --ws-port 8765 --width 120 --height 60
```

#### 💻 Terminal Version

**Start the server:**
```bash
python3 server.py
```

**Connect clients:**
```bash
python3 client.py localhost --name YourName
```

---

## 🌍 Playing Remotely (Internet)

Want to play with friends across the internet? Here are your options:

### Option 1: Using ngrok (Easiest)

**ngrok** creates a secure tunnel to your local server with a public URL.

1. **Install ngrok:**
   - Download from [ngrok.com/download](https://ngrok.com/download)
   - Or use: `brew install ngrok` (Mac) / `sudo snap install ngrok` (Linux)

2. **Start your game server:**
   ```bash
   python3 web_server.py
   ```

3. **Create tunnels (in separate terminals):**
   ```bash
   # Terminal 2: HTTP tunnel
   ngrok http 8080

   # Terminal 3: WebSocket tunnel
   ngrok http 8765
   ```

4. **Share the URLs with friends:**
   - ngrok shows URLs like: `https://abc123.ngrok.io`
   - HTTP tunnel URL → For accessing the game page
   - WebSocket tunnel URL → For game connection (use `wss://` instead of `https://`)

**Example:**
- Game page: `https://xyz789.ngrok.io`
- WebSocket: `wss://abc123.ngrok.io`

### Option 2: Port Forwarding (Permanent)

1. **Forward ports 8080 and 8765** in your router settings
2. **Find your public IP:** `curl ifconfig.me`
3. **Share with friends:**
   - Game page: `http://YOUR_PUBLIC_IP:8080`
   - WebSocket: `ws://YOUR_PUBLIC_IP:8765`

⚠️ **Security:** Port forwarding exposes your server directly. Consider firewall rules.

### Option 3: Cloud Deployment

Deploy to a cloud service for permanent hosting:
- **DigitalOcean** - $5/month droplet
- **AWS EC2** - Free tier available
- **Heroku** - Free tier for hobby projects
- **Fly.io** - Free tier with custom domains

---

## 🎯 How to Play

### Controls

**Web Version:**
- **Arrow Keys** or **WASD** - Control worm direction
- **Mouse** - Click buttons in menus

**Terminal Version:**
- **Arrow Keys** or **WASD** - Control worm direction
- **Space** - Ready up / Ready for next round
- **Q** - Quit game

### Game Flow

1. **Lobby** - Wait for players to join
2. **Ready Up** - Click "Ready" or press Space
3. **Countdown** - 3... 2... 1... GO!
4. **Play** - Avoid walls and trails, collect bonuses
5. **Round End** - Winner announced with scores
6. **Next Round** - Ready up for another round

### Game Mechanics

- **Movement** - Your worm moves continuously in the current direction
- **No Reverse** - Can't reverse direction (prevents instant death)
- **Collision = Death** - Hit walls, trails, or yourself → you die
- **Trail Fading** - Trails are limited to 30 cells (increases with bonuses)
- **Bonuses** - Collect golden orbs to increase trail length by 50 cells
- **Speed Increase** - Game gradually speeds up as the round progresses
- **Scoring** - Last worm alive wins the round and earns a point

---

## 🏆 Gameplay Tips

1. **Early Game** - Stay in open space, avoid congestion
2. **Collect Bonuses** - Longer trail = more flexibility
3. **Corner Traps** - Use corners to box in opponents
4. **Wall Riding** - Advanced: stay near walls for better control
5. **Prediction** - Anticipate where opponents will move
6. **Strategic Death** - Sometimes sacrifice to trap an opponent

---

## 🔧 Configuration

Edit `config.py` to customize game settings:

```python
# Game settings
DEFAULT_GRID_WIDTH = 120    # Arena width
DEFAULT_GRID_HEIGHT = 60    # Arena height
DEFAULT_FPS = 30            # Target frames per second

# Worm settings
TRAIL_LENGTH = 30           # Initial trail length
TRAIL_BONUS_INCREASE = 50   # Bonus trail length from collectibles
INITIAL_SPEED = 10          # Starting moves per second
MAX_SPEED = 20              # Maximum speed cap

# Bonus settings
MAX_BONUSES = 8             # Number of bonuses on field
BONUS_RESPAWN_TIME = 5      # Seconds between bonus spawns

# Network settings
DEFAULT_PORT = 9999         # Terminal server port
```

---

## 📁 Project Structure

```
expert-broccoli/
├── web/
│   ├── index.html      # Web game UI
│   ├── style.css       # Tron-themed styling
│   └── game.js         # Client-side game logic
├── web_server.py       # WebSocket game server (Web version)
├── server.py           # TCP game server (Terminal version)
├── client.py           # Terminal game client
├── game.py             # Core game logic (Worm, GameState, Bonuses)
├── renderer.py         # Terminal rendering with curses
├── protocol.py         # Network message protocol
├── config.py           # Game configuration
└── README.md           # This file
```

---

## 🐛 Troubleshooting

### Web Version

**Connection Issues:**
- Check server is running: `python3 web_server.py`
- Verify WebSocket URL is correct (ws:// or wss://)
- Check firewall isn't blocking ports 8080/8765
- For ngrok: Make sure both tunnels are running

**Port Already in Use:**
```bash
# Use different ports
python3 web_server.py --http-port 8081 --ws-port 8766
```

**Game Lagging:**
- Close other applications using network/CPU
- Reduce browser tab count
- Check internet connection (for remote play)

### Terminal Version

**"setupterm: could not find terminfo database"**
```bash
# Set TERM variable
export TERM=xterm-256color

# Install ncurses (Ubuntu/Debian)
sudo apt-get install ncurses-base ncurses-bin
```

**Connection Refused:**
- Verify server is running
- Check IP address is correct
- Ensure firewall allows port 9999
- Confirm both machines on same network

**Terminal Too Small:**
- Resize terminal to at least 80x40
- Or use smaller grid: `--width 60 --height 30`

---

## 🏗️ Architecture

### Server-Authoritative Model
- **Server** controls all game logic and state
- **Clients** send input, receive game state updates
- **Broadcast** state to all clients at 30 FPS
- **Benefits**: Fair gameplay, no cheating, consistency

### Networking
- **Web**: WebSocket protocol with asyncio
- **Terminal**: TCP with length-prefixed JSON messages
- **Low Latency**: Optimized for real-time gameplay
- **Reliable**: Automatic disconnect handling

### Game Loop
1. Server receives player inputs
2. Updates game state (movement, collisions, bonuses)
3. Broadcasts state to all connected clients
4. Clients render the current state
5. Repeat at 30 FPS

---

## 🚀 Future Ideas

Potential enhancements:
- **Power-ups**: Speed boost, invincibility, ghost mode
- **Game Modes**: Teams, elimination, time attack
- **Custom Maps**: Obstacles and barriers
- **Spectator Mode**: Watch after dying
- **Replays**: Review and share best rounds
- **Leaderboard**: Track stats across sessions
- **AI Opponents**: Practice against bots
- **Mobile Support**: Touch controls for phones

---

## 📝 License

This is a learning project - feel free to modify and share!

---

## 🙏 Credits

Inspired by:
- **Tron** (1982) - Light cycle battles
- **Snake** - Classic arcade game
- **Achtung, die Kurve!** - Multiplayer worm game

---

## 🎮 Ready to Play?

```bash
# Start the server
python3 web_server.py

# Open http://localhost:8080 in your browser
# Invite friends or play solo!
```

**Have fun and may the best worm win! 🏆🐍**
