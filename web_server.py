#!/usr/bin/env python3
"""
Tron Worm Web Server
WebSocket-based multiplayer game server for browser clients
"""

import asyncio
import json
import time
import websockets
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os
import socket
from pathlib import Path
from config import *
from game import GameState


def get_local_ip():
    """Get the local IP address of the server"""
    try:
        # Try multiple methods to get the real LAN IP
        import socket

        # Method 1: Get all network interfaces and find the best one
        hostname = socket.gethostname()
        ip_addresses = socket.getaddrinfo(hostname, None)

        # Filter and prioritize IPs
        lan_ips = []
        for addr_info in ip_addresses:
            ip = addr_info[4][0]
            # Skip localhost, IPv6, and Docker IPs
            if ip.startswith('127.') or ':' in ip:
                continue
            # Skip Docker bridge network (172.17.x.x, 172.18.x.x)
            if ip.startswith('172.17.') or ip.startswith('172.18.'):
                continue
            # Prefer common LAN ranges
            if ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.'):
                lan_ips.append(ip)

        if lan_ips:
            # Return first valid LAN IP (prefer 10.x over 192.168.x)
            lan_ips.sort(key=lambda x: (0 if x.startswith('10.') else 1))
            return lan_ips[0]

        # Method 2: Create a connection to determine route
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()

        # Filter out Docker IPs from method 2 as well
        if not ip.startswith('172.17.') and not ip.startswith('172.18.'):
            return ip

        # Fallback to common server IP
        return '10.67.67.195'
    except Exception:
        return '10.67.67.195'


class WebGameServer:
    """WebSocket game server for browser clients"""

    def __init__(self, host='0.0.0.0', ws_port=8766, http_port=8081, width=DEFAULT_GRID_WIDTH, height=DEFAULT_GRID_HEIGHT, server_ip=None):
        self.host = host
        self.ws_port = ws_port
        self.http_port = http_port
        self.game_state = GameState(width, height)
        self.clients = {}  # player_id -> websocket
        self.player_names = {}  # player_id -> name
        self.running = False
        self.next_player_id = 1
        self.local_ip = server_ip if server_ip else get_local_ip()

    async def handle_client(self, websocket):
        """Handle a WebSocket client connection"""
        player_id = None

        try:
            # Wait for join message
            message = await websocket.recv()
            msg = json.loads(message)

            if msg.get('type') != MSG_JOIN:
                await websocket.send(json.dumps({
                    'type': MSG_ERROR,
                    'data': {'error': 'Invalid join message'}
                }))
                return

            player_name = msg.get('data', {}).get('name', f'Player{self.next_player_id}')

            # Assign player ID
            player_id = str(self.next_player_id)
            self.next_player_id += 1

            # Add player to game
            if not self.game_state.add_player(player_id, player_name):
                await websocket.send(json.dumps({
                    'type': MSG_ERROR,
                    'data': {'error': 'Server full'}
                }))
                return

            self.clients[player_id] = websocket
            self.player_names[player_id] = player_name

            # Send join acknowledgment
            await websocket.send(json.dumps({
                'type': MSG_JOIN_ACK,
                'data': {
                    'player_id': player_id,
                    'game_state': self.game_state.to_dict()
                }
            }))

            print(f"✅ Player '{player_name}' joined (ID: {player_id}) - {len(self.clients)}/{MAX_PLAYERS}")

            # Broadcast updated state
            await self.broadcast_state()

            # Handle messages from this client
            async for message in websocket:
                msg = json.loads(message)
                await self.handle_message(player_id, msg)

        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"❌ Client handler error: {e}")
        finally:
            # Remove player
            if player_id:
                if player_id in self.clients:
                    del self.clients[player_id]
                if player_id in self.player_names:
                    player_name = self.player_names[player_id]
                    del self.player_names[player_id]
                    print(f"👋 Player '{player_name}' disconnected - {len(self.clients)}/{MAX_PLAYERS}")
                self.game_state.remove_player(player_id)

                # Broadcast updated state
                await self.broadcast_state()

    async def handle_message(self, player_id, msg):
        """Handle a message from a client"""
        if msg.get('type') == MSG_READY:
            ready = msg.get('data', {}).get('ready', True)
            self.game_state.set_player_ready(player_id, ready)

            # Check if all players are ready (works in lobby or after round ends)
            if self.game_state.all_players_ready():
                if self.game_state.state == STATE_LOBBY or self.game_state.state == STATE_ROUND_END:
                    self.game_state.start_countdown()

            await self.broadcast_state()

        elif msg.get('type') == MSG_FORCE_START:
            # Force start for solo/practice mode (requires at least 1 player)
            if len(self.game_state.worms) >= 1:
                if self.game_state.state == STATE_LOBBY or self.game_state.state == STATE_ROUND_END:
                    print(f"🎮 Force start initiated by player '{self.player_names.get(player_id)}'")
                    self.game_state.start_countdown()
                    await self.broadcast_state()

        elif msg.get('type') == MSG_INPUT:
            direction = msg.get('data', {}).get('direction')
            if direction:
                self.game_state.handle_input(player_id, direction)

    async def broadcast_state(self):
        """Broadcast game state to all clients"""
        if not self.clients:
            return

        state_msg = json.dumps({
            'type': MSG_STATE,
            'data': {'game_state': self.game_state.to_dict()}
        })

        # Send to all clients
        dead_clients = []
        for player_id, websocket in list(self.clients.items()):
            try:
                await websocket.send(state_msg)
            except:
                dead_clients.append(player_id)

        # Remove dead clients
        for player_id in dead_clients:
            if player_id in self.clients:
                del self.clients[player_id]
            if player_id in self.player_names:
                del self.player_names[player_id]
            self.game_state.remove_player(player_id)

    async def game_loop(self):
        """Main game loop"""
        last_update = time.time()
        last_broadcast = time.time()

        while self.running:
            current_time = time.time()
            delta_time = current_time - last_update

            # Handle countdown
            if self.game_state.state == STATE_COUNTDOWN:
                if self.game_state.countdown_start:
                    elapsed = current_time - self.game_state.countdown_start
                    if elapsed >= COUNTDOWN_SECONDS:
                        self.game_state.start_round()

            # Update game state
            elif self.game_state.state == STATE_PLAYING:
                moves_per_second = self.game_state.current_speed
                update_interval = 1.0 / moves_per_second

                if delta_time >= update_interval:
                    self.game_state.update()
                    last_update = current_time

            # Broadcast state to clients at target FPS
            if current_time - last_broadcast >= TICK_RATE:
                await self.broadcast_state()
                last_broadcast = current_time

            # Small sleep to prevent CPU spinning
            await asyncio.sleep(0.001)

    async def start_websocket_server(self):
        """Start the WebSocket server"""
        try:
            self.running = True
            print(f"🌐 WebSocket server started on ws://{self.host}:{self.ws_port}")

            async with websockets.serve(self.handle_client, self.host, self.ws_port):
                # Start game loop
                await self.game_loop()
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"\n❌ ERROR: WebSocket port {self.ws_port} is already in use!")
                print("\n🔧 Solutions:")
                print(f"1. Use a different port:")
                print(f"   python3 web_server.py --ws-port 8766")
                print(f"\n2. Find what's using port {self.ws_port}:")
                print(f"   sudo lsof -i :{self.ws_port}")
                print(f"\n3. Kill the process using the port")
            else:
                print(f"❌ WebSocket Server error: {e}")
            import sys
            sys.exit(1)

    def start_http_server(self):
        """Start HTTP server for serving static files"""
        try:
            # Change to web directory
            web_dir = Path(__file__).parent / 'web'
            os.chdir(web_dir)

            # Create custom handler with access to server instance
            server_instance = self

            class CustomHandler(SimpleHTTPRequestHandler):
                def log_message(self, format, *args):
                    pass  # Suppress HTTP logs

                def do_GET(self):
                    # If requesting index.html, inject the server URL
                    if self.path == '/' or self.path == '/index.html':
                        try:
                            with open('index.html', 'r', encoding='utf-8') as f:
                                content = f.read()

                            # Replace the placeholder with actual server IP and port
                            server_url = f"ws://{server_instance.local_ip}:{server_instance.ws_port}"
                            content = content.replace('placeholder="ws://localhost:8765"', f'placeholder="{server_url}"')
                            content = content.replace('value="ws://localhost:8765"', f'value="{server_url}"')

                            # Send response
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html; charset=utf-8')
                            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                            self.end_headers()
                            self.wfile.write(content.encode('utf-8'))
                        except Exception as e:
                            self.send_error(500, f'Error: {e}')
                    else:
                        # For other files, use default handler
                        super().do_GET()

            httpd = HTTPServer((self.host, self.http_port), CustomHandler)
            print(f"🌐 HTTP server started on http://{self.host}:{self.http_port}")
            print(f"📊 Grid size: {self.game_state.width}x{self.game_state.height}")
            print(f"👥 Max players: {MAX_PLAYERS}")
            print(f"🔗 Local IP: {self.local_ip}")
            print(f"\n🎮 Open in browser:")
            print(f"   Local:  http://localhost:{self.http_port}")
            print(f"   Network: http://{self.local_ip}:{self.http_port}")
            print(f"\n📡 WebSocket: ws://{self.local_ip}:{self.ws_port}\n")
            print("Waiting for players to connect...\n")

            httpd.serve_forever()
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"\n❌ ERROR: Port {self.http_port} is already in use!")
                print("\n🔧 Solutions:")
                print(f"1. Use a different port:")
                print(f"   python3 web_server.py --http-port 8081")
                print(f"\n2. Find what's using port {self.http_port}:")
                print(f"   sudo lsof -i :{self.http_port}")
                print(f"   # or")
                print(f"   sudo netstat -tulpn | grep :{self.http_port}")
                print(f"\n3. Kill the process using the port")
                print(f"\n4. Try common alternative ports: 8081, 8082, 9000, 3000")
            else:
                print(f"❌ HTTP Server error: {e}")
            import sys
            sys.exit(1)

    def start(self):
        """Start both HTTP and WebSocket servers"""
        # Start HTTP server in separate thread
        http_thread = threading.Thread(target=self.start_http_server, daemon=True)
        http_thread.start()

        # Give HTTP server time to start
        import time
        time.sleep(0.5)

        # Start WebSocket server
        try:
            asyncio.run(self.start_websocket_server())
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            self.running = False
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            import sys
            sys.exit(1)


def main():
    """Main server entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Tron Worm Web Game Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--ws-port', type=int, default=8766, help='WebSocket port (default: 8766)')
    parser.add_argument('--http-port', type=int, default=8081, help='HTTP port (default: 8081)')
    parser.add_argument('--server-ip', type=str, default=None, help='Server IP for clients (auto-detected if not specified)')
    parser.add_argument('--width', type=int, default=DEFAULT_GRID_WIDTH, help=f'Grid width (default: {DEFAULT_GRID_WIDTH})')
    parser.add_argument('--height', type=int, default=DEFAULT_GRID_HEIGHT, help=f'Grid height (default: {DEFAULT_GRID_HEIGHT})')

    args = parser.parse_args()

    # Check if websockets is installed
    try:
        import websockets
    except ImportError:
        print("❌ Error: 'websockets' package not found")
        print("\n📦 Install it with:")
        print("   pip install websockets")
        print("\nOr install all web requirements:")
        print("   pip install -r requirements-web.txt")
        return

    server = WebGameServer(args.host, args.ws_port, args.http_port, args.width, args.height, args.server_ip)
    server.start()


if __name__ == '__main__':
    main()
