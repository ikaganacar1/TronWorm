# 🚀 Quick Start Guide

Get playing in 60 seconds!

## Single Machine Testing (2+ terminals)

**Terminal 1 - Start Server:**
```bash
python3 server.py
```

**Terminal 2 - Player 1:**
```bash
python3 client.py localhost --name Alice
```

**Terminal 3 - Player 2:**
```bash
python3 client.py localhost --name Bob
```

**Ready and Play:**
1. Both players press **SPACE** to ready up
2. Countdown starts automatically
3. Use **Arrow Keys** or **WASD** to control
4. Press **Q** to quit

## LAN Multiplayer

**Host Machine:**
```bash
# Start server
python3 server.py

# Find your IP
hostname -I
# Example output: 192.168.1.100
```

**Player Machines:**
```bash
# Connect using host's IP
python3 client.py 192.168.1.100 --name YourName
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move worm |
| Space | Ready up / Next round |
| Q | Quit |

## Tips

1. **Terminal Size**: Make sure your terminal is at least 80x40 characters
2. **Network**: All players must be on the same local network
3. **Firewall**: Port 9999 must be open on the server machine
4. **Colors**: Use a modern terminal emulator for best graphics

## Common Issues

**"Connection refused"**
- Server not running or wrong IP address

**"Server full"**
- Already 5 players connected

**Choppy gameplay**
- Try smaller grid: `python3 server.py --width 60 --height 30`

---

That's it! For detailed info, see README.md
