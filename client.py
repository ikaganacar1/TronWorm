#!/usr/bin/env python3
"""
Tron Worm Game Client
Connects to game server and handles rendering/input
"""

import socket
import threading
import time
import sys
import curses
from config import *
from protocol import *
from game import GameState
from renderer import Renderer


class GameClient:
    """Multiplayer game client"""

    def __init__(self, host, port, player_name):
        self.host = host
        self.port = port
        self.player_name = player_name
        self.player_id = None
        self.game_state = None
        self.socket = None
        self.running = False
        self.connected = False
        self.lock = threading.Lock()
        self.renderer = None

    def connect(self):
        """Connect to the game server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            # Send join message
            join_msg = Message(MSG_JOIN, {'name': self.player_name})
            if not send_message(self.socket, join_msg):
                return False

            # Wait for join acknowledgment
            response = receive_message(self.socket)
            if not response:
                return False

            if response.type == MSG_ERROR:
                print(f"Server error: {response.data.get('error', 'Unknown error')}")
                return False

            if response.type == MSG_JOIN_ACK:
                self.player_id = response.data['player_id']
                self.game_state = GameState.from_dict(response.data['game_state'])
                self.connected = True
                return True

            return False

        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def receive_loop(self):
        """Receive messages from server"""
        while self.running:
            try:
                msg = receive_message(self.socket)
                if not msg:
                    print("\n❌ Disconnected from server")
                    self.running = False
                    break

                self.handle_message(msg)

            except Exception as e:
                if self.running:
                    print(f"\n❌ Receive error: {e}")
                    self.running = False
                break

    def handle_message(self, msg):
        """Handle a message from server"""
        with self.lock:
            if msg.type == MSG_STATE:
                self.game_state = GameState.from_dict(msg.data['game_state'])

            elif msg.type == MSG_ERROR:
                print(f"\nServer error: {msg.data.get('error', 'Unknown error')}")

    def send_ready(self, ready=True):
        """Send ready status to server"""
        msg = Message(MSG_READY, {'ready': ready})
        send_message(self.socket, msg)

    def send_input(self, direction):
        """Send input to server"""
        msg = Message(MSG_INPUT, {'direction': direction})
        send_message(self.socket, msg)

    def handle_input(self, key):
        """Handle keyboard input"""
        with self.lock:
            if not self.game_state:
                return True

            state = self.game_state.state

            # Quit
            if key in [ord('q'), ord('Q')]:
                return False

            # Lobby state
            if state == STATE_LOBBY:
                if key == ord(' '):  # Space to ready up
                    if self.player_id in self.game_state.ready_players:
                        self.send_ready(False)
                    else:
                        self.send_ready(True)

            # Playing state
            elif state == STATE_PLAYING:
                direction = None

                # Arrow keys
                if key == curses.KEY_UP:
                    direction = 'UP'
                elif key == curses.KEY_DOWN:
                    direction = 'DOWN'
                elif key == curses.KEY_LEFT:
                    direction = 'LEFT'
                elif key == curses.KEY_RIGHT:
                    direction = 'RIGHT'

                # WASD keys
                elif key in [ord('w'), ord('W')]:
                    direction = 'UP'
                elif key in [ord('s'), ord('S')]:
                    direction = 'DOWN'
                elif key in [ord('a'), ord('A')]:
                    direction = 'LEFT'
                elif key in [ord('d'), ord('D')]:
                    direction = 'RIGHT'

                if direction:
                    self.send_input(direction)

            # Round end state
            elif state == STATE_ROUND_END:
                if key == ord(' '):  # Space to ready for next round
                    self.send_ready(True)

        return True

    def run_curses(self, stdscr):
        """Main game loop with curses"""
        self.renderer = Renderer(stdscr)
        self.running = True

        # Start receive thread
        receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
        receive_thread.start()

        last_render = time.time()

        # Main loop
        while self.running:
            current_time = time.time()

            # Handle input
            try:
                key = stdscr.getch()
                if key != -1:
                    if not self.handle_input(key):
                        break
            except:
                pass

            # Render at target FPS
            if current_time - last_render >= TICK_RATE:
                with self.lock:
                    if self.game_state:
                        self.renderer.render(self.game_state, self.player_id)
                last_render = current_time

            # Small sleep to prevent CPU spinning
            time.sleep(0.001)

    def run(self):
        """Run the client"""
        try:
            # Connect to server
            if not self.connect():
                print("❌ Failed to connect to server")
                return False

            print(f"✅ Connected to server as '{self.player_name}'")
            print(f"🎮 Starting game client...\n")

            time.sleep(1)  # Brief pause before starting curses

            # Run curses interface
            curses.wrapper(self.run_curses)

            return True

        except Exception as e:
            print(f"❌ Client error: {e}")
            return False
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown the client"""
        self.running = False

        if self.socket:
            try:
                send_message(self.socket, Message(MSG_DISCONNECT))
                self.socket.close()
            except:
                pass


def main():
    """Main client entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Tron Worm Game Client')
    parser.add_argument('host', help='Server hostname or IP address')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Server port (default: {DEFAULT_PORT})')
    parser.add_argument('--name', default=None, help='Player name')

    args = parser.parse_args()

    # Get player name
    if args.name:
        player_name = args.name
    else:
        try:
            player_name = input("Enter your name: ").strip()
            if not player_name:
                player_name = f"Player{int(time.time()) % 1000}"
        except:
            player_name = f"Player{int(time.time()) % 1000}"

    # Create and run client
    client = GameClient(args.host, args.port, player_name)

    try:
        client.run()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
