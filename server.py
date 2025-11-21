#!/usr/bin/env python3
"""
Tron Worm Game Server
Handles multiplayer game hosting
"""

import socket
import threading
import time
import sys
from config import *
from protocol import *
from game import GameState


class GameServer:
    """Multiplayer game server"""

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, width=DEFAULT_GRID_WIDTH, height=DEFAULT_GRID_HEIGHT):
        self.host = host
        self.port = port
        self.game_state = GameState(width, height)
        self.clients = {}  # player_id -> socket
        self.player_names = {}  # player_id -> name
        self.running = False
        self.lock = threading.Lock()
        self.next_player_id = 1
        self.server_socket = None

    def start(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(MAX_PLAYERS)
            self.running = True

            print(f"🎮 Tron Worm Server started on {self.host}:{self.port}")
            print(f"📊 Grid size: {self.game_state.width}x{self.game_state.height}")
            print(f"👥 Max players: {MAX_PLAYERS}")
            print(f"⏱️  Target FPS: {DEFAULT_FPS}")
            print("\nWaiting for players to connect...\n")

            # Start game loop thread
            game_thread = threading.Thread(target=self.game_loop, daemon=True)
            game_thread.start()

            # Accept client connections
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"📥 New connection from {address}")

                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        print(f"❌ Error accepting connection: {e}")

        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.shutdown()

    def handle_client(self, client_socket, address):
        """Handle a client connection"""
        player_id = None

        try:
            # Wait for join message
            msg = receive_message(client_socket)
            if not msg or msg.type != MSG_JOIN:
                send_message(client_socket, Message(MSG_ERROR, {'error': 'Invalid join message'}))
                client_socket.close()
                return

            player_name = msg.data.get('name', f'Player{self.next_player_id}')

            with self.lock:
                # Assign player ID
                player_id = str(self.next_player_id)
                self.next_player_id += 1

                # Add player to game
                if not self.game_state.add_player(player_id, player_name):
                    send_message(client_socket, Message(MSG_ERROR, {'error': 'Server full'}))
                    client_socket.close()
                    return

                self.clients[player_id] = client_socket
                self.player_names[player_id] = player_name

            # Send join acknowledgment
            send_message(client_socket, Message(MSG_JOIN_ACK, {
                'player_id': player_id,
                'game_state': self.game_state.to_dict()
            }))

            print(f"✅ Player '{player_name}' joined (ID: {player_id}) - {len(self.clients)}/{MAX_PLAYERS}")

            # Broadcast updated state to all clients
            self.broadcast_state()

            # Handle client messages
            while self.running:
                msg = receive_message(client_socket)
                if not msg:
                    break  # Client disconnected

                self.handle_message(player_id, msg)

        except Exception as e:
            print(f"❌ Client handler error: {e}")
        finally:
            # Remove player
            if player_id:
                with self.lock:
                    if player_id in self.clients:
                        del self.clients[player_id]
                    if player_id in self.player_names:
                        player_name = self.player_names[player_id]
                        del self.player_names[player_id]
                        print(f"👋 Player '{player_name}' disconnected - {len(self.clients)}/{MAX_PLAYERS}")
                    self.game_state.remove_player(player_id)

                # Broadcast updated state
                self.broadcast_state()

            try:
                client_socket.close()
            except:
                pass

    def handle_message(self, player_id, msg):
        """Handle a message from a client"""
        with self.lock:
            if msg.type == MSG_READY:
                ready = msg.data.get('ready', True)
                self.game_state.set_player_ready(player_id, ready)

                # Check if all players are ready
                if self.game_state.all_players_ready() and self.game_state.state == STATE_LOBBY:
                    self.game_state.start_countdown()

                self.broadcast_state()

            elif msg.type == MSG_INPUT:
                direction = msg.data.get('direction')
                if direction:
                    self.game_state.handle_input(player_id, direction)

            elif msg.type == MSG_DISCONNECT:
                pass  # Will be handled by connection close

    def game_loop(self):
        """Main game loop"""
        last_update = time.time()
        last_broadcast = time.time()

        while self.running:
            current_time = time.time()
            delta_time = current_time - last_update

            with self.lock:
                # Handle countdown
                if self.game_state.state == STATE_COUNTDOWN:
                    if self.game_state.countdown_start:
                        elapsed = current_time - self.game_state.countdown_start
                        if elapsed >= COUNTDOWN_SECONDS:
                            self.game_state.start_round()

                # Update game state
                elif self.game_state.state == STATE_PLAYING:
                    # Update at appropriate speed
                    moves_per_second = self.game_state.current_speed
                    update_interval = 1.0 / moves_per_second

                    if delta_time >= update_interval:
                        self.game_state.update()
                        last_update = current_time

            # Broadcast state to clients at target FPS
            if current_time - last_broadcast >= TICK_RATE:
                self.broadcast_state()
                last_broadcast = current_time

            # Small sleep to prevent CPU spinning
            time.sleep(0.001)

    def broadcast_state(self):
        """Broadcast game state to all clients"""
        with self.lock:
            state_msg = Message(MSG_STATE, {'game_state': self.game_state.to_dict()})

            # Send to all clients
            dead_clients = []
            for player_id, client_socket in self.clients.items():
                if not send_message(client_socket, state_msg):
                    dead_clients.append(player_id)

            # Remove dead clients
            for player_id in dead_clients:
                if player_id in self.clients:
                    del self.clients[player_id]
                if player_id in self.player_names:
                    del self.player_names[player_id]
                self.game_state.remove_player(player_id)

    def shutdown(self):
        """Shutdown the server"""
        print("\n🛑 Shutting down server...")
        self.running = False

        with self.lock:
            # Close all client connections
            for client_socket in self.clients.values():
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()

        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        print("✅ Server shutdown complete")


def main():
    """Main server entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Tron Worm Game Server')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'Server host (default: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Server port (default: {DEFAULT_PORT})')
    parser.add_argument('--width', type=int, default=DEFAULT_GRID_WIDTH, help=f'Grid width (default: {DEFAULT_GRID_WIDTH})')
    parser.add_argument('--height', type=int, default=DEFAULT_GRID_HEIGHT, help=f'Grid height (default: {DEFAULT_GRID_HEIGHT})')

    args = parser.parse_args()

    server = GameServer(args.host, args.port, args.width, args.height)

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        server.shutdown()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        server.shutdown()
        sys.exit(1)


if __name__ == '__main__':
    main()
