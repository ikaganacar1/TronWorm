#!/bin/bash
# Test script to run server and multiple clients in tmux

echo "🎮 Starting Tron Worm test environment..."

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux not found. Please install it:"
    echo "   Ubuntu/Debian: sudo apt-get install tmux"
    echo "   Fedora/RHEL:   sudo dnf install tmux"
    exit 1
fi

# Create new tmux session with server
tmux new-session -d -s tron_game "python3 server.py"

# Wait a moment for server to start
sleep 1

# Split window and run first client
tmux split-window -h "python3 client.py localhost --name Player1"

# Split again for second client
tmux split-window -v "python3 client.py localhost --name Player2"

# Select first pane (server)
tmux select-pane -t 0

# Attach to session
echo "✅ Starting game in tmux session..."
echo ""
echo "Controls:"
echo "  - Arrow Keys/WASD to move"
echo "  - Space to ready up"
echo "  - Q to quit"
echo "  - Ctrl+b then arrow keys to switch panes"
echo "  - Ctrl+b then d to detach"
echo "  - 'tmux kill-session -t tron_game' to stop all"
echo ""
sleep 2

tmux attach-session -t tron_game
