# Tron Worm - Multiplayer Snake Battle
# Multi-stage build for minimal image size

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Copy application files
COPY config.py .
COPY protocol.py .
COPY game.py .
COPY web_server.py .
COPY web/ ./web/

# Create non-root user for security
RUN useradd -m -u 1000 tronworm && \
    chown -R tronworm:tronworm /app

USER tronworm

# Expose ports
EXPOSE 8081 8766

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8081)); s.close()" || exit 1

# Run the web server
CMD ["python", "web_server.py", "--host", "0.0.0.0"]
