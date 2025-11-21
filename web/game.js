// Tron Worm - Web Game Client

// Game states
const STATE_LOBBY = 'lobby';
const STATE_COUNTDOWN = 'countdown';
const STATE_PLAYING = 'playing';
const STATE_ROUND_END = 'round_end';

// Player colors (matching server config)
const COLORS = [
    '#ff0000', // Red
    '#00ff00', // Green
    '#ffff00', // Yellow
    '#0000ff', // Blue
    '#ff00ff', // Magenta
    '#00ffff', // Cyan
];

class TronWormClient {
    constructor() {
        this.ws = null;
        this.playerId = null;
        this.gameState = null;
        this.canvas = null;
        this.ctx = null;
        this.isReady = false;
        this.previousState = null;

        this.initElements();
        this.initEventListeners();
    }

    initElements() {
        // Screens
        this.screens = {
            connection: document.getElementById('connection-screen'),
            lobby: document.getElementById('lobby-screen'),
            countdown: document.getElementById('countdown-screen'),
            game: document.getElementById('game-screen'),
            roundEnd: document.getElementById('round-end-screen')
        };

        // Connection screen
        this.playerNameInput = document.getElementById('player-name');
        this.serverUrlInput = document.getElementById('server-url');
        this.connectBtn = document.getElementById('connect-btn');
        this.connectionStatus = document.getElementById('connection-status');

        // Lobby screen
        this.playerCount = document.getElementById('player-count');
        this.playerList = document.getElementById('player-list');
        this.readyBtn = document.getElementById('ready-btn');
        this.soloBtn = document.getElementById('solo-btn');
        this.disconnectBtn = document.getElementById('disconnect-btn');

        // Countdown screen
        this.countdownNumber = document.getElementById('countdown-number');

        // Game screen
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.roundNumber = document.getElementById('round-number');
        this.gameSpeed = document.getElementById('game-speed');
        this.scoresDisplay = document.getElementById('scores-display');

        // Round end screen
        this.winnerText = document.getElementById('winner-text');
        this.finalScores = document.getElementById('final-scores');
        this.nextRoundBtn = document.getElementById('next-round-btn');
        this.soloRestartBtn = document.getElementById('solo-restart-btn');
        this.quitBtn = document.getElementById('quit-btn');

        // Load player name from localStorage
        const savedName = localStorage.getItem('playerName');
        if (savedName) {
            this.playerNameInput.value = savedName;
        }
    }

    initEventListeners() {
        // Connection
        this.connectBtn.addEventListener('click', () => this.connect());
        this.playerNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.connect();
        });

        // Lobby
        this.readyBtn.addEventListener('click', () => this.toggleReady());
        this.soloBtn.addEventListener('click', () => this.startSolo());
        this.disconnectBtn.addEventListener('click', () => this.disconnect());

        // Round end
        this.nextRoundBtn.addEventListener('click', () => this.toggleReady());
        this.soloRestartBtn.addEventListener('click', () => this.startSolo());
        this.quitBtn.addEventListener('click', () => this.disconnect());

        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));

        // Window resize
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    connect() {
        const playerName = this.playerNameInput.value.trim() || `Player${Math.floor(Math.random() * 1000)}`;
        const serverUrl = this.serverUrlInput.value.trim();

        if (!serverUrl) {
            this.showStatus('Please enter server URL', 'error');
            return;
        }

        // Save player name
        localStorage.setItem('playerName', playerName);

        this.showStatus('Connecting...', 'info');
        this.connectBtn.disabled = true;

        try {
            this.ws = new WebSocket(serverUrl);

            this.ws.onopen = () => {
                console.log('Connected to server');
                // Send join message
                this.send({
                    type: 'join',
                    data: { name: playerName }
                });
            };

            this.ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showStatus('Connection error', 'error');
                this.connectBtn.disabled = false;
            };

            this.ws.onclose = () => {
                console.log('Disconnected from server');
                this.showStatus('Disconnected from server', 'error');
                this.showScreen('connection');
                this.connectBtn.disabled = false;
            };

        } catch (error) {
            console.error('Connection error:', error);
            this.showStatus('Failed to connect', 'error');
            this.connectBtn.disabled = false;
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.showScreen('connection');
        this.isReady = false;
    }

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    handleMessage(message) {
        switch (message.type) {
            case 'join_ack':
                this.playerId = message.data.player_id;
                this.gameState = message.data.game_state;
                this.showStatus('Connected!', 'success');
                this.showScreen('lobby');
                this.updateLobby();
                break;

            case 'state':
                this.gameState = message.data.game_state;
                this.updateGame();
                break;

            case 'error':
                this.showStatus(message.data.error, 'error');
                break;
        }
    }

    updateGame() {
        if (!this.gameState) return;

        const state = this.gameState.state;

        if (state === STATE_LOBBY) {
            this.showScreen('lobby');
            this.updateLobby();
            this.previousState = state;
        } else if (state === STATE_COUNTDOWN) {
            this.showScreen('countdown');
            this.updateCountdown();
            this.previousState = state;
        } else if (state === STATE_PLAYING) {
            this.showScreen('game');
            this.updatePlaying();
            this.render();
            this.previousState = state;
        } else if (state === STATE_ROUND_END) {
            this.showScreen('roundEnd');
            this.updateRoundEnd();
            // Only reset isReady when first entering round end state
            if (this.previousState !== STATE_ROUND_END) {
                this.isReady = false;
            }
            this.previousState = state;
        }
    }

    updateLobby() {
        const worms = Object.values(this.gameState.worms);
        this.playerCount.textContent = worms.length;

        this.playerList.innerHTML = '';
        worms.forEach(worm => {
            const item = document.createElement('div');
            item.className = 'player-item';
            item.style.background = `${COLORS[worm.color_id]}33`;

            const readyMark = document.createElement('span');
            readyMark.className = 'ready-mark';
            readyMark.textContent = this.gameState.ready_players.includes(worm.player_id) ? '✓' : ' ';

            const name = document.createElement('span');
            name.textContent = worm.name;
            name.style.color = COLORS[worm.color_id];

            item.appendChild(readyMark);
            item.appendChild(name);

            if (worm.player_id === this.playerId) {
                const badge = document.createElement('span');
                badge.className = 'you-badge';
                badge.textContent = 'YOU';
                item.appendChild(badge);
            }

            this.playerList.appendChild(item);
        });

        // Update ready button
        if (this.isReady) {
            this.readyBtn.textContent = 'Not Ready';
            this.readyBtn.classList.remove('btn-success');
            this.readyBtn.classList.add('btn-danger');
        } else {
            this.readyBtn.textContent = 'Ready Up';
            this.readyBtn.classList.remove('btn-danger');
            this.readyBtn.classList.add('btn-success');
        }

        // Show/hide solo button based on player count
        if (worms.length === 1) {
            this.soloBtn.style.display = 'block';
            this.readyBtn.style.display = 'none';
        } else {
            this.soloBtn.style.display = 'none';
            this.readyBtn.style.display = 'block';
        }
    }

    updateCountdown() {
        if (this.gameState.countdown_start) {
            const elapsed = (Date.now() / 1000) - this.gameState.countdown_start;
            const remaining = Math.max(0, 3 - Math.floor(elapsed));

            if (remaining > 0) {
                this.countdownNumber.textContent = remaining;
            } else {
                this.countdownNumber.textContent = 'GO!';
            }
        }
    }

    updatePlaying() {
        this.roundNumber.textContent = this.gameState.round_number;
        this.gameSpeed.textContent = this.gameState.current_speed.toFixed(1);

        // Update scores
        this.scoresDisplay.innerHTML = '';
        Object.values(this.gameState.worms).forEach(worm => {
            const scoreItem = document.createElement('span');
            scoreItem.className = 'score-item';
            scoreItem.style.background = `${COLORS[worm.color_id]}33`;

            const score = this.gameState.scores[worm.player_id] || 0;
            const status = worm.alive ? '' : ' 💀';

            scoreItem.innerHTML = `<span style="color: ${COLORS[worm.color_id]}">${worm.name}</span>: ${score}${status}`;

            this.scoresDisplay.appendChild(scoreItem);
        });
    }

    updateRoundEnd() {
        if (this.gameState.last_winner) {
            this.winnerText.textContent = `🏆 ${this.gameState.last_winner} wins! 🏆`;
        }

        // Sort players by score
        const worms = Object.values(this.gameState.worms);
        worms.sort((a, b) => {
            const scoreA = this.gameState.scores[a.player_id] || 0;
            const scoreB = this.gameState.scores[b.player_id] || 0;
            return scoreB - scoreA;
        });

        this.finalScores.innerHTML = '';
        worms.forEach(worm => {
            const row = document.createElement('div');
            row.className = 'score-row';
            row.style.background = `${COLORS[worm.color_id]}22`;

            // Add ready indicator for multiplayer
            if (worms.length > 1) {
                const readyMark = document.createElement('span');
                readyMark.style.marginRight = '8px';
                readyMark.textContent = this.gameState.ready_players.includes(worm.player_id) ? '✓' : ' ';
                row.appendChild(readyMark);
            }

            const name = document.createElement('span');
            name.className = 'player-name';
            name.style.color = COLORS[worm.color_id];
            name.textContent = worm.name;

            const score = document.createElement('span');
            score.className = 'player-score';
            score.textContent = this.gameState.scores[worm.player_id] || 0;

            row.appendChild(name);
            row.appendChild(score);
            this.finalScores.appendChild(row);
        });

        // Update button
        if (this.isReady) {
            this.nextRoundBtn.textContent = 'Cancel Ready';
            this.nextRoundBtn.classList.remove('btn-success');
            this.nextRoundBtn.classList.add('btn-danger');
        } else {
            this.nextRoundBtn.textContent = 'Ready for Next Round';
            this.nextRoundBtn.classList.remove('btn-danger');
            this.nextRoundBtn.classList.add('btn-success');
        }

        // Show/hide solo restart button based on player count
        if (worms.length === 1) {
            this.soloRestartBtn.style.display = 'block';
            this.nextRoundBtn.style.display = 'none';
        } else {
            this.soloRestartBtn.style.display = 'none';
            this.nextRoundBtn.style.display = 'block';
        }
    }

    toggleReady() {
        this.isReady = !this.isReady;
        this.send({
            type: 'ready',
            data: { ready: this.isReady }
        });
    }

    startSolo() {
        this.send({
            type: 'force_start',
            data: {}
        });
    }

    handleKeyPress(e) {
        if (!this.gameState || this.gameState.state !== STATE_PLAYING) {
            return;
        }

        let direction = null;

        // Arrow keys
        if (e.key === 'ArrowUp') {
            direction = 'UP';
            e.preventDefault();
        } else if (e.key === 'ArrowDown') {
            direction = 'DOWN';
            e.preventDefault();
        } else if (e.key === 'ArrowLeft') {
            direction = 'LEFT';
            e.preventDefault();
        } else if (e.key === 'ArrowRight') {
            direction = 'RIGHT';
            e.preventDefault();
        }
        // WASD
        else if (e.key.toLowerCase() === 'w') {
            direction = 'UP';
        } else if (e.key.toLowerCase() === 's') {
            direction = 'DOWN';
        } else if (e.key.toLowerCase() === 'a') {
            direction = 'LEFT';
        } else if (e.key.toLowerCase() === 'd') {
            direction = 'RIGHT';
        }
        // Escape to disconnect
        else if (e.key === 'Escape') {
            this.disconnect();
            return;
        }

        if (direction) {
            this.send({
                type: 'input',
                data: { direction: direction }
            });
        }
    }

    resizeCanvas() {
        if (!this.gameState) return;

        const container = this.canvas.parentElement;
        const cellSize = Math.min(
            Math.floor((container.clientWidth - 40) / this.gameState.width),
            Math.floor((container.clientHeight - 200) / this.gameState.height)
        );

        this.canvas.width = this.gameState.width * cellSize;
        this.canvas.height = this.gameState.height * cellSize;

        if (this.gameState.state === STATE_PLAYING) {
            this.render();
        }
    }

    render() {
        if (!this.gameState || !this.ctx) return;

        const cellSize = this.canvas.width / this.gameState.width;

        // Clear canvas
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid (subtle)
        this.ctx.strokeStyle = '#111';
        this.ctx.lineWidth = 0.5;
        for (let x = 0; x <= this.gameState.width; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * cellSize, 0);
            this.ctx.lineTo(x * cellSize, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y <= this.gameState.height; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * cellSize);
            this.ctx.lineTo(this.canvas.width, y * cellSize);
            this.ctx.stroke();
        }

        // Draw bonuses
        if (this.gameState.bonuses) {
            this.gameState.bonuses.forEach(bonus => {
                const centerX = bonus.x * cellSize + cellSize / 2;
                const centerY = bonus.y * cellSize + cellSize / 2;
                const radius = cellSize / 3;

                // Draw glowing circle for bonus
                this.ctx.fillStyle = '#FFD700'; // Gold color
                this.ctx.shadowBlur = 15;
                this.ctx.shadowColor = '#FFD700';
                this.ctx.beginPath();
                this.ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.shadowBlur = 0;

                // Draw inner highlight
                this.ctx.fillStyle = '#FFFF00';
                this.ctx.beginPath();
                this.ctx.arc(centerX - radius/3, centerY - radius/3, radius/3, 0, Math.PI * 2);
                this.ctx.fill();
            });
        }

        // Draw worms
        Object.values(this.gameState.worms).forEach(worm => {
            const color = COLORS[worm.color_id];

            // Draw trail
            this.ctx.fillStyle = color + '88'; // Semi-transparent
            worm.trail.forEach(([x, y]) => {
                this.ctx.fillRect(
                    x * cellSize + 1,
                    y * cellSize + 1,
                    cellSize - 2,
                    cellSize - 2
                );
            });

            // Draw head (brighter)
            if (worm.body.length > 0 && worm.alive) {
                const [headX, headY] = worm.body[0];
                this.ctx.fillStyle = color;
                this.ctx.fillRect(
                    headX * cellSize + 1,
                    headY * cellSize + 1,
                    cellSize - 2,
                    cellSize - 2
                );

                // Add glow effect to head
                this.ctx.shadowBlur = 10;
                this.ctx.shadowColor = color;
                this.ctx.fillRect(
                    headX * cellSize + 1,
                    headY * cellSize + 1,
                    cellSize - 2,
                    cellSize - 2
                );
                this.ctx.shadowBlur = 0;
            }
        });

        // Draw border
        this.ctx.strokeStyle = '#00ff00';
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(0, 0, this.canvas.width, this.canvas.height);
    }

    showScreen(screenName) {
        Object.values(this.screens).forEach(screen => {
            screen.classList.remove('active');
        });

        if (this.screens[screenName]) {
            this.screens[screenName].classList.add('active');

            if (screenName === 'game') {
                setTimeout(() => this.resizeCanvas(), 100);
            }
        }
    }

    showStatus(message, type) {
        this.connectionStatus.textContent = message;
        this.connectionStatus.className = `status-message ${type}`;
    }
}

// Initialize game when page loads
let game;
window.addEventListener('DOMContentLoaded', () => {
    game = new TronWormClient();
});
