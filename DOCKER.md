# 🐳 Docker Deployment Guide

This guide explains how to run Tron Worm using Docker for easy deployment and portability.

## Prerequisites

- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 1.29+ (usually included with Docker Desktop)

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The game will be available at:
- **HTTP**: http://localhost:8080
- **WebSocket**: ws://localhost:8765

### Using Docker Directly

```bash
# Build the image
docker build -t tronworm:latest .

# Run the container
docker run -d \
  --name tronworm-game \
  -p 8080:8080 \
  -p 8765:8765 \
  --restart unless-stopped \
  tronworm:latest

# View logs
docker logs -f tronworm-game

# Stop the container
docker stop tronworm-game
docker rm tronworm-game
```

## Configuration

### Custom Ports

Edit `docker-compose.yml` to change ports:

```yaml
ports:
  - "8081:8080"  # Map host port 8081 to container port 8080
  - "8766:8765"  # Map host port 8766 to container port 8765
```

Or with Docker directly:

```bash
docker run -d \
  -p 8081:8080 \
  -p 8766:8765 \
  tronworm:latest
```

### Custom Grid Size

Pass command-line arguments:

```yaml
# docker-compose.yml
services:
  tronworm:
    command: ["python", "web_server.py", "--host", "0.0.0.0", "--width", "100", "--height", "50"]
```

Or with Docker:

```bash
docker run -d \
  -p 8080:8080 \
  -p 8765:8765 \
  tronworm:latest \
  python web_server.py --host 0.0.0.0 --width 100 --height 50
```

## Management

### View Running Containers

```bash
docker ps
```

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail 100
```

### Restart Container

```bash
docker-compose restart
```

### Update to Latest Code

```bash
# Rebuild and restart
docker-compose up -d --build
```

## Remote Deployment

### Deploy to Cloud

The Docker image can be deployed to any cloud provider:

#### DigitalOcean

```bash
# Create droplet with Docker
# SSH into droplet
git clone https://github.com/ikaganacar1/TronWorm.git
cd TronWorm
docker-compose up -d
```

#### AWS EC2

```bash
# Launch EC2 instance with Docker
# SSH into instance
git clone https://github.com/ikaganacar1/TronWorm.git
cd TronWorm
docker-compose up -d

# Open ports in security group:
# - 8080 (HTTP)
# - 8765 (WebSocket)
```

#### Fly.io

```bash
# Install flyctl
brew install flyctl  # Mac
# or
curl -L https://fly.io/install.sh | sh  # Linux

# Login and launch
fly launch
fly deploy
```

### Using Docker Hub

Push your image to Docker Hub for easy sharing:

```bash
# Tag the image
docker tag tronworm:latest YOUR_USERNAME/tronworm:latest

# Push to Docker Hub
docker login
docker push YOUR_USERNAME/tronworm:latest

# Others can pull and run
docker pull YOUR_USERNAME/tronworm:latest
docker run -d -p 8080:8080 -p 8765:8765 YOUR_USERNAME/tronworm:latest
```

## Remote Play with Docker

### Option 1: ngrok with Docker

```bash
# Terminal 1: Start game server
docker-compose up

# Terminal 2: HTTP tunnel
ngrok http 8080

# Terminal 3: WebSocket tunnel
ngrok http 8765

# Share the ngrok URLs with friends
```

### Option 2: Expose Public IP

If running on a cloud server:

```bash
# Get public IP
curl ifconfig.me

# Players connect to:
# HTTP: http://YOUR_PUBLIC_IP:8080
# WebSocket: ws://YOUR_PUBLIC_IP:8765
```

## Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
sudo lsof -i :8080
sudo lsof -i :8765

# Kill the process or use different ports
docker-compose down
# Edit docker-compose.yml to use different ports
docker-compose up -d
```

### Container Won't Start

```bash
# Check logs
docker-compose logs

# Check container status
docker-compose ps

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Permission Denied

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker-compose up -d
```

### Container Keeps Restarting

```bash
# Check logs for errors
docker-compose logs -f

# Check health status
docker inspect tronworm-game | grep -A 10 Health
```

## Security

### Production Recommendations

1. **Use HTTPS/WSS**: Put behind reverse proxy (nginx, Caddy)
2. **Firewall**: Restrict access to necessary ports only
3. **Updates**: Keep Docker and base images updated
4. **Secrets**: Use Docker secrets for sensitive data
5. **Resources**: Set memory/CPU limits

### Example nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name tronworm.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Resource Limits

Add resource limits to docker-compose.yml:

```yaml
services:
  tronworm:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

## Monitoring

### Check Container Stats

```bash
# Real-time stats
docker stats tronworm-game

# With docker-compose
docker-compose stats
```

### Health Check

```bash
# Check health status
docker inspect tronworm-game | grep -A 5 Health
```

## Development

### Live Development with Docker

Mount source code for live updates:

```yaml
# docker-compose.dev.yml
services:
  tronworm:
    volumes:
      - ./:/app
    command: ["python", "-u", "web_server.py", "--host", "0.0.0.0"]
```

```bash
docker-compose -f docker-compose.dev.yml up
```

---

## Summary

**Quick Start:**
```bash
docker-compose up -d
# Open http://localhost:8080
```

**Update:**
```bash
docker-compose up -d --build
```

**Stop:**
```bash
docker-compose down
```

**Logs:**
```bash
docker-compose logs -f
```

That's it! Your Tron Worm game is now running in Docker! 🎮🐳
