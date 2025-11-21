# Changelog

All notable changes to Tron Worm will be documented in this file.

## [2.0.0] - 2025-11-21

### 🎮 Added
- **Collectible Bonus System**: Golden orbs spawn randomly on the field
  - Collect bonuses to increase trail length by +50 cells
  - Up to 8 bonuses on field at once
  - Bonuses respawn every 5 seconds
  - Glowing gold visual effects
- **Solo/Practice Mode**: Play alone without needing other players
  - "Start Solo Practice" button when alone in lobby
  - Different win conditions for single vs multiplayer
  - "Play Again" button for quick restarts
- **Larger Playing Field**: Increased from 80x40 to 120x60
  - Optimized for modern 1920x1080 displays
  - More space for strategic gameplay
- **Limited Trail Length**: Trails now fade over time
  - Initial trail length of 30 cells (down from 150)
  - Faster-paced gameplay
  - Dynamic trail growth through bonuses

### 🐛 Fixed
- **Critical**: Fixed random game ending bug
  - Root cause: Trail deque maxlen desynchronization
  - Worm's max_trail_length now reset before creating deque
  - Added defensive trail_set synchronization
- **Critical**: Fixed ready state not persisting in round end screen
  - Ready button now maintains state correctly
  - Added visual ready indicators in multiplayer
  - Fixed button flickering between states
- **Fixed**: Rematch functionality after round ends
  - Server now accepts countdown start from STATE_ROUND_END
  - Both solo and multiplayer rematches work properly
- **Fixed**: Single-player mode win condition
  - Solo ends only when player dies (0 alive)
  - Multiplayer ends when ≤1 alive
- **Fixed**: Collision detection causing immediate deaths
  - Collision checks performed BEFORE moving
  - Proper set-based trail collision detection
  - Added move_count to prevent instant end

### 📚 Documentation
- **Reorganized README**: Complete restructure with modern formatting
  - Web version featured first (recommended)
  - Added remote play guide (ngrok, port forwarding, cloud)
  - Added gameplay mechanics and strategy tips
  - Better organization with visual separators
  - Version badges and modern markdown
- **Added**: Complete remote internet play instructions
  - ngrok tunnel setup guide
  - Port forwarding instructions
  - Cloud deployment options

### 🎨 Improvements
- **Visual**: Glowing effects for bonuses and worm heads
- **UI**: Ready indicators in round end score display
- **Performance**: Efficient deque with maxlen for trail management
- **Network**: Bonus state synchronization across clients

### 🏗️ Technical
- Added `Bonus` class for collectible items
- Dynamic trail length system with adjustable deque
- Bonus spawning with collision avoidance
- Enhanced game state serialization for bonuses
- State tracking to prevent ready state reset

---

## [1.0.0] - Initial Release

### Added
- **Web Version**: Browser-based multiplayer with WebSockets
- **Terminal Version**: Classic CLI with curses
- **Multiplayer**: 2-5 players over LAN
- **Real-time Gameplay**: 30 FPS server-authoritative model
- **Lobby System**: Ready-up mechanism with countdown
- **Score Tracking**: Multiple rounds with persistent scores
- **Controls**: Arrow keys and WASD support
- **Game Mechanics**:
  - Continuous worm movement
  - Trail collision detection
  - Wall collision detection
  - Speed progression over time
- **Networking**:
  - TCP/IP for terminal version
  - WebSocket for web version
  - Length-prefixed JSON protocol

---

**Legend:**
- 🎮 Added - New features
- 🐛 Fixed - Bug fixes
- 📚 Documentation - Documentation changes
- 🎨 Improvements - Enhancements to existing features
- 🏗️ Technical - Under-the-hood changes
