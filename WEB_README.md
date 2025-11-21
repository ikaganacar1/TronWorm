# 🌐 Tron Worm - Web Version

A fast-paced multiplayer Tron-style worm game that runs in your web browser!

## 🎮 Play in Your Browser

No terminal required! Just open your browser and play with friends on your local network.

## ✨ Features

- **Browser-based** - Play from any modern web browser
- **Real-time multiplayer** - 2-5 players simultaneously
- **Beautiful graphics** - HTML5 Canvas with glowing effects
- **Responsive design** - Works on desktop and tablet
- **Easy to play** - Just enter your name and connect!

## 🚀 Quick Start

### Step 1: Install Requirements

```bash
# Install websockets library
pip install websockets

# Or install from requirements file
pip install -r requirements-web.txt
```

### Step 2: Start the Server

```bash
python3 web_server.py
```

You'll see:
```
🌐 HTTP server started on http://0.0.0.0:8080
🌐 WebSocket server started on ws://0.0.0.0:8765
📊 Grid size: 80x40
👥 Max players: 5

🎮 Open in browser: http://localhost:8080
   Or: http://<your-ip>:8080

Waiting for players to connect...
```

### Step 3: Open in Browser

**On the same machine:**
- Open your browser to http://localhost:8080

**On other devices (same network):**
1. Find your server's IP address:
   ```bash
   hostname -I
   # Example: 192.168.1.100
   ```
2. Open browser to http://192.168.1.100:8080

### Step 4: Play!

1. Enter your name
2. Click "Connect" (or press Enter)
3. Wait for other players to join
4. Click "Ready Up" when ready
5. Use **Arrow Keys** or **WASD** to control your worm
6. Last player alive wins!

## 🎯 How to Play

### Controls

| Key | Action |
|-----|--------|
| Arrow Keys | Move worm |
| W/A/S/D | Move worm (alternative) |
| ESC | Disconnect from game |

### Game Rules

1. **Constant Movement** - Your worm never stops moving
2. **Turn Only** - You can't reverse direction
3. **Avoid Trails** - Don't hit walls or any worm trails
4. **Last Alive Wins** - Survive longer than opponents
5. **Speed Increases** - Game gets faster over time

## 📱 Supported Browsers

- ✅ Chrome / Chromium (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Opera

**Minimum Requirements:**
- WebSocket support
- HTML5 Canvas support
- ES6 JavaScript support

## 🔧 Server Options

```bash
# Custom ports
python3 web_server.py --ws-port 9000 --http-port 9001

# Custom grid size
python3 web_server.py --width 100 --height 50

# All options
python3 web_server.py \
  --host 0.0.0.0 \
  --ws-port 8765 \
  --http-port 8080 \
  --width 80 \
  --height 40
```

### Command-Line Arguments

- `--host` - Server host address (default: 0.0.0.0)
- `--ws-port` - WebSocket port (default: 8765)
- `--http-port` - HTTP port (default: 8080)
- `--width` - Grid width (default: 80)
- `--height` - Grid height (default: 40)

## 🌐 Network Setup

### Playing on Same Machine

Just open multiple browser tabs/windows and connect to http://localhost:8080

### Playing on Local Network (LAN)

**Server machine:**
```bash
python3 web_server.py
```

**Find server IP:**
```bash
hostname -I
# Example output: 192.168.1.100
```

**Client machines:**
- Open browser to http://192.168.1.100:8080
- Enter name and click Connect

### Port Forwarding (Internet Play)

To play over the internet:

1. **Forward ports on your router:**
   - HTTP: 8080 → your-server-ip:8080
   - WebSocket: 8765 → your-server-ip:8765

2. **Find your public IP:**
   - Visit https://whatismyip.com

3. **Share with friends:**
   - Give them: http://your-public-ip:8080

**⚠️ Security Note:** Only do this temporarily and close ports when done!

## 🐛 Troubleshooting

### "Failed to connect"

**Check server is running:**
```bash
# Should show web_server.py
ps aux | grep web_server
```

**Check WebSocket URL:**
- Should be `ws://` (not `wss://` unless you have SSL)
- Default: `ws://localhost:8765`

**Check firewall:**
```bash
# Allow ports through firewall
sudo ufw allow 8080/tcp
sudo ufw allow 8765/tcp
```

### "Connection refused"

- Server not started
- Wrong IP address
- Firewall blocking ports
- Ports already in use

### "websockets module not found"

```bash
pip install websockets
```

### Connection drops during game

- Check network stability
- Ensure server machine isn't going to sleep
- Check for firewall issues

### Canvas not rendering

- Use a modern browser (Chrome, Firefox, Safari, Edge)
- Enable JavaScript
- Check browser console for errors (F12)

### Laggy gameplay

- Reduce grid size on server: `--width 60 --height 30`
- Use wired connection instead of WiFi
- Close other network applications
- Ensure server machine has sufficient resources

## 📁 Project Structure

```
TronWorm/
├── web_server.py          # WebSocket game server
├── web/
│   ├── index.html         # Game UI
│   ├── style.css          # Styling
│   └── game.js            # Client logic & rendering
├── game.py                # Core game logic (shared)
├── config.py              # Game configuration (shared)
├── Dockerfile             # Docker image
├── docker-compose.yml     # Docker orchestration
└── requirements-web.txt   # Web dependencies
```

## 🎨 Customization

### Change Colors

Edit `web/game.js`:
```javascript
const COLORS = [
    '#ff0000',  // Red - Change to any hex color
    '#00ff00',  // Green
    '#ffff00',  // Yellow
    '#0000ff',  // Blue
    '#ff00ff',  // Magenta
    '#00ffff',  // Cyan
];
```

### Change Speed

Edit `config.py`:
```python
INITIAL_SPEED = 10      # Starting speed (moves/second)
SPEED_INCREMENT = 0.5   # Speed increase rate
MAX_SPEED = 20          # Maximum speed
```

### Change Grid Size

```bash
python3 web_server.py --width 100 --height 50
```

Or edit `config.py`:
```python
DEFAULT_GRID_WIDTH = 100
DEFAULT_GRID_HEIGHT = 50
```

## 🔒 Security Considerations

**For Local Network Play:**
- ✅ Safe to use on trusted local networks
- ✅ No sensitive data transmitted

**For Internet Play:**
- ⚠️ No authentication built-in
- ⚠️ No encryption (plain WebSocket)
- ⚠️ Suitable for casual gaming only
- ⚠️ Close ports after playing

**For Production:**
- Use WSS (WebSocket Secure) with SSL certificates
- Add authentication system
- Implement rate limiting
- Add input validation

## 🆚 Web vs Terminal Version

| Feature | Web Version | Terminal Version |
|---------|-------------|------------------|
| **Platform** | Any browser | Linux terminal |
| **Setup** | Easier | Requires curses |
| **Graphics** | Smooth, colorful | ASCII art |
| **Controls** | Keyboard in browser | Direct terminal input |
| **Network** | WebSockets | Raw TCP sockets |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 💡 Tips for Best Experience

1. **Use Chrome** - Best WebSocket performance
2. **Wired Connection** - Lower latency than WiFi
3. **Close Background Apps** - Free up network bandwidth
4. **Fullscreen Mode** - Press F11 for immersive experience
5. **Practice First** - Try solo in lobby to get used to controls

## 🚧 Known Limitations

- Maximum 5 players (configurable in code)
- Requires modern browser with WebSocket support
- Game state not persisted (restarting server resets scores)
- No spectator mode (yet)
- No replay system (yet)

## 🎓 Technical Details

**Backend:**
- Python 3.6+
- asyncio for async operations
- websockets library for WebSocket protocol
- Simple HTTP server for serving static files

**Frontend:**
- Vanilla JavaScript (no frameworks)
- HTML5 Canvas for rendering
- CSS3 for styling
- WebSocket API for real-time communication

**Architecture:**
- Server-authoritative game logic
- Client sends input, receives full game state
- 30 FPS state updates
- Event-driven networking

## 📝 License

This is a learning project - feel free to modify and share!

## 🙏 Credits

- Original terminal version by Claude
- Inspired by Tron (1982) and classic Snake games

---

**Have fun and may the best worm win! 🏆🐍**

Open http://localhost:8080 and start playing!
