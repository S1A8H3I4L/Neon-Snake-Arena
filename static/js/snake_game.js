/* ===========================================================
   Retro Neon Snake — browser game engine (Canvas 2D)
   Mirrors the mechanics of the Pygame desktop version:
   queued directional input, grid movement, wall/self collision,
   gradually increasing speed, neon glow rendering.
   =========================================================== */

(() => {
  const CELL_SIZE = 20;
  const GRID_WIDTH = 28;
  const GRID_HEIGHT = 22;

  const START_MOVE_INTERVAL = 130; // ms per move, mirrors desktop version
  const MIN_MOVE_INTERVAL = 55;
  const SPEEDUP_EVERY_N_FOODS = 4;
  const SPEEDUP_AMOUNT = 8;

  const COLORS = {
    bg: '#05050d',
    grid: 'rgba(124, 255, 203, 0.05)',
    snakeHead: '#78ffd2',
    snakeBody: '#00ffaa',
    food: '#ff3cb4',
  };

  const DIRECTIONS = {
    ArrowUp: [0, -1],
    ArrowDown: [0, 1],
    ArrowLeft: [-1, 0],
    ArrowRight: [1, 0],
  };

  function opposite([dx, dy]) {
    return [-dx, -dy];
  }

  function sameDir(a, b) {
    return a[0] === b[0] && a[1] === b[1];
  }

  class SnakeGame {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.hudScore = document.getElementById('hudScore');
      this.hudHigh = document.getElementById('hudHigh');
      this.sessionHigh = 0;

      this.reset();
      this.bindInput();
      this.lastTimestamp = null;
      this.timeSinceMove = 0;
      this.gameOverFired = false;

      requestAnimationFrame((t) => this.loop(t));
    }

    reset() {
      const startX = Math.floor(GRID_WIDTH / 2);
      const startY = Math.floor(GRID_HEIGHT / 2);
      this.body = [[startX, startY], [startX - 1, startY], [startX - 2, startY]];
      this.direction = [1, 0];
      this.pendingDirections = [];
      this.growPending = 0;
      this.score = 0;
      this.moveInterval = START_MOVE_INTERVAL;
      this.foodsEatenSinceSpeedup = 0;
      this.paused = false;
      this.gameOver = false;
      this.gameOverFired = false;
      this.food = this.spawnFood();
      this.updateHud();
    }

    spawnFood() {
      const occupied = new Set(this.body.map(([x, y]) => `${x},${y}`));
      const free = [];
      for (let x = 0; x < GRID_WIDTH; x++) {
        for (let y = 0; y < GRID_HEIGHT; y++) {
          if (!occupied.has(`${x},${y}`)) free.push([x, y]);
        }
      }
      if (free.length === 0) return this.food || [0, 0];
      return free[Math.floor(Math.random() * free.length)];
    }

    bindInput() {
      window.addEventListener('keydown', (e) => {
        if (e.key in DIRECTIONS) {
          e.preventDefault();
          this.queueDirection(DIRECTIONS[e.key]);
        } else if (e.key === 'p' || e.key === 'P') {
          if (!this.gameOver) this.paused = !this.paused;
        } else if (e.key === 'Enter' && this.gameOver) {
          this.reset();
          hideGameOverOverlay();
        }
      });

      const playAgainBtn = document.getElementById('playAgainBtn');
      if (playAgainBtn) {
        playAgainBtn.addEventListener('click', () => {
          this.reset();
          hideGameOverOverlay();
        });
      }
    }

    queueDirection(dir) {
      const lastDir = this.pendingDirections.length
        ? this.pendingDirections[this.pendingDirections.length - 1]
        : this.direction;
      if (sameDir(dir, opposite(lastDir))) return;
      if (this.pendingDirections.length < 2) this.pendingDirections.push(dir);
    }

    step() {
      if (this.pendingDirections.length) {
        this.direction = this.pendingDirections.shift();
      }

      const [hx, hy] = this.body[0];
      const [dx, dy] = this.direction;
      const newHead = [hx + dx, hy + dy];
      this.body.unshift(newHead);

      if (this.growPending > 0) {
        this.growPending -= 1;
      } else {
        this.body.pop();
      }

      // Wall collision
      const [nx, ny] = newHead;
      if (nx < 0 || nx >= GRID_WIDTH || ny < 0 || ny >= GRID_HEIGHT) {
        this.triggerGameOver();
        return;
      }

      // Self collision (skip the head itself, index 0)
      for (let i = 1; i < this.body.length; i++) {
        if (this.body[i][0] === nx && this.body[i][1] === ny) {
          this.triggerGameOver();
          return;
        }
      }

      // Food collision
      if (nx === this.food[0] && ny === this.food[1]) {
        this.growPending += 1;
        this.score += 1;
        this.food = this.spawnFood();
        this.foodsEatenSinceSpeedup += 1;
        if (this.foodsEatenSinceSpeedup >= SPEEDUP_EVERY_N_FOODS) {
          this.foodsEatenSinceSpeedup = 0;
          this.moveInterval = Math.max(MIN_MOVE_INTERVAL, this.moveInterval - SPEEDUP_AMOUNT);
        }
        this.updateHud();
      }
    }

    triggerGameOver() {
      this.gameOver = true;
      if (!this.gameOverFired) {
        this.gameOverFired = true;
        if (this.score > this.sessionHigh) {
          this.sessionHigh = this.score;
          this.hudHigh.textContent = this.sessionHigh;
        }
        showGameOverOverlay(this.score);
      }
    }

    updateHud() {
      this.hudScore.textContent = this.score;
    }

    loop(timestamp) {
      if (this.lastTimestamp === null) this.lastTimestamp = timestamp;
      const dt = timestamp - this.lastTimestamp;
      this.lastTimestamp = timestamp;

      if (!this.paused && !this.gameOver) {
        this.timeSinceMove += dt;
        if (this.timeSinceMove >= this.moveInterval) {
          this.timeSinceMove = 0;
          this.step();
        }
      }

      this.draw();
      requestAnimationFrame((t) => this.loop(t));
    }

    draw() {
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;

      ctx.fillStyle = COLORS.bg;
      ctx.fillRect(0, 0, w, h);

      // grid lines
      ctx.strokeStyle = COLORS.grid;
      ctx.lineWidth = 1;
      for (let x = 0; x <= GRID_WIDTH; x++) {
        ctx.beginPath();
        ctx.moveTo(x * CELL_SIZE, 0);
        ctx.lineTo(x * CELL_SIZE, h);
        ctx.stroke();
      }
      for (let y = 0; y <= GRID_HEIGHT; y++) {
        ctx.beginPath();
        ctx.moveTo(0, y * CELL_SIZE);
        ctx.lineTo(w, y * CELL_SIZE);
        ctx.stroke();
      }

      // food with pulsing glow
      const pulse = (Math.sin(performance.now() / 150) + 1) / 2;
      this.drawGlowCell(this.food[0], this.food[1], COLORS.food, 10 + pulse * 10);

      // snake
      this.body.forEach(([x, y], i) => {
        const color = i === 0 ? COLORS.snakeHead : COLORS.snakeBody;
        const glow = i === 0 ? 14 : 6;
        const fade = i === 0 ? 1 : Math.max(0.5, 1 - (i / this.body.length) * 0.5);
        this.drawGlowCell(x, y, color, glow, fade);
      });

      if (this.paused && !this.gameOver) {
        ctx.fillStyle = 'rgba(0,0,0,0.55)';
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = COLORS.snakeHead;
        ctx.font = 'bold 28px monospace';
        ctx.textAlign = 'center';
        ctx.shadowColor = COLORS.snakeHead;
        ctx.shadowBlur = 14;
        ctx.fillText('PAUSED', w / 2, h / 2);
        ctx.shadowBlur = 0;
        ctx.font = '14px monospace';
        ctx.fillStyle = '#d7fff5';
        ctx.fillText('Press P to Resume', w / 2, h / 2 + 30);
      }
    }

    drawGlowCell(gx, gy, color, glowAmount, alpha = 1) {
      const ctx = this.ctx;
      const px = gx * CELL_SIZE;
      const py = gy * CELL_SIZE;
      const pad = 2;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.shadowColor = color;
      ctx.shadowBlur = glowAmount;
      ctx.fillStyle = color;
      ctx.fillRect(px + pad, py + pad, CELL_SIZE - pad * 2, CELL_SIZE - pad * 2);
      ctx.restore();
    }
  }

  // ---- Game over overlay + score submission ----
  function showGameOverOverlay(score) {
    const overlay = document.getElementById('gameOverOverlay');
    const finalScoreEl = document.getElementById('finalScore');
    const statusEl = document.getElementById('saveStatus');

    finalScoreEl.textContent = score;
    statusEl.textContent = 'Saving...';
    statusEl.className = 'save-status pending';
    overlay.classList.add('visible');

    fetch(window.SNAKE_CONFIG.saveScoreUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.SNAKE_CONFIG.csrfToken,
      },
      body: JSON.stringify({ score }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.ok) {
          statusEl.textContent = data.is_personal_best
            ? `Saved Successfully — New Personal Best! (Rank #${data.rank})`
            : `Saved Successfully (Rank #${data.rank})`;
          statusEl.className = 'save-status success';
        } else {
          statusEl.textContent = `Couldn't save score: ${data.error || 'Unknown error'}`;
          statusEl.className = 'save-status error';
        }
      })
      .catch(() => {
        statusEl.textContent = "Couldn't save score — check your connection.";
        statusEl.className = 'save-status error';
      });
  }

  function hideGameOverOverlay() {
    document.getElementById('gameOverOverlay').classList.remove('visible');
  }

  document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('gameCanvas');
    if (canvas) new SnakeGame(canvas);
  });
})();
