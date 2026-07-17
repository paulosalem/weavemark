import {
  COURSE,
  GAME_STATE,
  createInitialGameState,
  formatTime,
  getActiveTarget,
  restartGame,
  setPaused,
  startRace,
  updateGame,
} from "./engine.js";

const BEST_TIME_KEY = "orbital-drift.bestTime";
const CONTROL_KEYS = new Set([
  "arrowup",
  "arrowdown",
  "arrowleft",
  "arrowright",
  "w",
  "a",
  "s",
  "d",
  " ",
  "p",
  "escape",
  "r",
  "enter",
]);

class InputController {
  constructor(canvas, callbacks) {
    this.canvas = canvas;
    this.callbacks = callbacks;
    this.keys = new Set();

    window.addEventListener("keydown", (event) => this.handleKeyDown(event), { passive: false });
    window.addEventListener("keyup", (event) => this.handleKeyUp(event), { passive: false });
    window.addEventListener("blur", () => {
      this.keys.clear();
      this.callbacks.onSuspend();
    });
    canvas.addEventListener("pointerdown", () => {
      canvas.focus();
      this.callbacks.onStart();
    });
  }

  snapshot() {
    return {
      thrust: this.keys.has("w") || this.keys.has("arrowup"),
      left: this.keys.has("a") || this.keys.has("arrowleft"),
      right: this.keys.has("d") || this.keys.has("arrowright"),
      brake: this.keys.has(" ") || this.keys.has("s") || this.keys.has("arrowdown"),
    };
  }

  clearMotionKeys() {
    this.keys.clear();
  }

  handleKeyDown(event) {
    const key = normalizeKey(event.key);

    if (CONTROL_KEYS.has(key)) {
      event.preventDefault();
      this.canvas.focus();
    }

    if (key === "r") {
      this.callbacks.onRestart();
      return;
    }

    if (key === "p" || key === "escape") {
      this.callbacks.onPauseToggle();
      return;
    }

    if (key === "enter") {
      this.callbacks.onStart();
      return;
    }

    if (key === "w" || key === "arrowup") {
      this.callbacks.onStart();
    }

    if (CONTROL_KEYS.has(key)) {
      this.keys.add(key);
    }
  }

  handleKeyUp(event) {
    this.keys.delete(normalizeKey(event.key));
  }
}

class Hud {
  constructor() {
    this.lap = document.getElementById("hudLap");
    this.gate = document.getElementById("hudGate");
    this.time = document.getElementById("hudTime");
    this.best = document.getElementById("hudBest");
    this.state = document.getElementById("hudState");
    this.overlay = document.getElementById("overlay");
    this.feedback = document.getElementById("feedback");
  }

  update(state) {
    const target = getActiveTarget(state);
    this.lap.textContent = `Lap ${state.progress.lap}/${state.progress.requiredLaps}`;
    this.gate.textContent =
      target.type === "finish"
        ? "Finish gate"
        : `Gate ${state.progress.nextCheckpoint + 1}/${COURSE.checkpoints.length}`;
    this.time.textContent = formatTime(state.timer.final ?? state.timer.elapsed);
    this.best.textContent = `Best ${formatTime(state.bestTime)}`;
    this.state.textContent = state.state[0].toUpperCase() + state.state.slice(1);

    this.updateOverlay(state);
    this.updateFeedback(state);
  }

  updateOverlay(state) {
    if (state.state === GAME_STATE.PLAYING) {
      this.overlay.hidden = true;
      return;
    }

    this.overlay.hidden = false;
    const card = this.overlay.querySelector(".overlay-card");

    if (state.state === GAME_STATE.READY) {
      card.innerHTML = readyOverlayMarkup();
    } else if (state.state === GAME_STATE.PAUSED) {
      card.innerHTML = `
        <p class="eyebrow">Race suspended</p>
        <h2>Paused on a safe orbit.</h2>
        <p>The timer and physics are stopped. Press P, Escape, or Enter to resume, or R to restart.</p>
        <p class="start-hint">No surprise jumps after tab switches.</p>
      `;
    } else if (state.state === GAME_STATE.FINISHED) {
      const isBest = state.bestTime !== null && state.timer.final === state.bestTime;
      card.innerHTML = `
        <p class="eyebrow">Race complete</p>
        <h2>${formatTime(state.timer.final)}</h2>
        <p>${isBest ? "New best time locked into local storage." : `Best time: ${formatTime(state.bestTime)}.`}</p>
        <p class="start-hint">Press R to restart without reloading.</p>
      `;
    }
  }

  updateFeedback(state) {
    const shouldShow = state.message.time > 0 && state.state !== GAME_STATE.READY;
    this.feedback.textContent = shouldShow ? state.message.text : "";
    this.feedback.classList.toggle("is-visible", shouldShow);
    this.feedback.dataset.type = state.message.type;
  }
}

class Renderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.stars = createStarfield(190);
    this.asteroidShapes = COURSE.asteroids.map((asteroid, index) =>
      createAsteroidShape(asteroid.radius, index),
    );
  }

  render(state, timeSeconds) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, COURSE.width, COURSE.height);
    this.drawBackground(ctx, timeSeconds);
    this.drawRoute(ctx);
    this.drawGravityWells(ctx, state, timeSeconds);
    this.drawGates(ctx, state, timeSeconds);
    this.drawPlanets(ctx);
    this.drawAsteroids(ctx, timeSeconds);
    this.drawCraft(ctx, state);
    this.drawEffects(ctx, state);
  }

  drawBackground(ctx, timeSeconds) {
    const gradient = ctx.createLinearGradient(0, 0, COURSE.width, COURSE.height);
    gradient.addColorStop(0, "#020715");
    gradient.addColorStop(0.55, "#07162f");
    gradient.addColorStop(1, "#030611");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, COURSE.width, COURSE.height);

    for (const star of this.stars) {
      const twinkle = 0.55 + Math.sin(timeSeconds * star.speed + star.phase) * 0.22;
      ctx.globalAlpha = star.alpha * twinkle;
      ctx.fillStyle = star.color;
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  drawRoute(ctx) {
    const points = [COURSE.startGate, ...COURSE.checkpoints, COURSE.startGate];
    ctx.save();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "rgba(139, 222, 255, 0.18)";
    ctx.setLineDash([9, 15]);
    ctx.beginPath();
    points.forEach((point, index) => {
      if (index === 0) {
        ctx.moveTo(point.x, point.y);
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });
    ctx.stroke();
    ctx.restore();
  }

  drawGravityWells(ctx, state, timeSeconds) {
    for (const well of COURSE.gravityWells) {
      const pulse = 0.5 + Math.sin(timeSeconds * 2.4 + well.x) * 0.5;
      const gradient = ctx.createRadialGradient(well.x, well.y, 10, well.x, well.y, well.radius);
      gradient.addColorStop(0, `${hexToRgba(well.color, 0.26 + pulse * 0.06)}`);
      gradient.addColorStop(0.42, `${hexToRgba(well.color, 0.09)}`);
      gradient.addColorStop(1, "rgba(80, 150, 255, 0)");
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(well.x, well.y, well.radius, 0, Math.PI * 2);
      ctx.fill();

      ctx.lineWidth = 2;
      ctx.strokeStyle = hexToRgba(well.color, 0.42);
      ctx.setLineDash([16, 11]);
      ctx.beginPath();
      ctx.arc(well.x, well.y, well.radius * (0.72 + pulse * 0.03), 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = hexToRgba(well.color, 0.85);
      ctx.font = "700 15px Inter, sans-serif";
      ctx.fillText(well.label, well.x - 36, well.y + 5);
    }

    if (state.effects.gravity > 0.05 && state.effects.gravitySource) {
      const source = state.effects.gravitySource;
      const alpha = Math.min(0.7, state.effects.gravity + 0.2);
      ctx.strokeStyle = hexToRgba(source.color ?? "#6bb7ff", alpha);
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(state.craft.x, state.craft.y);
      ctx.lineTo(source.x, source.y);
      ctx.stroke();
    }
  }

  drawGates(ctx, state, timeSeconds) {
    this.drawGate(ctx, COURSE.startGate, {
      label: "START / FINISH",
      isActive: getActiveTarget(state).type === "finish",
      isStart: true,
      timeSeconds,
    });

    COURSE.checkpoints.forEach((gate, index) => {
      const isActive =
        state.progress.nextCheckpoint === index && getActiveTarget(state).type === "checkpoint";
      const isComplete = index < state.progress.nextCheckpoint;
      this.drawGate(ctx, gate, {
        label: `${index + 1}`,
        isActive,
        isComplete,
        timeSeconds,
      });
    });
  }

  drawGate(ctx, gate, options) {
    const pulse = options.isActive ? 0.5 + Math.sin(options.timeSeconds * 6) * 0.5 : 0;
    const color = options.isActive
      ? options.isStart
        ? "#ffd166"
        : "#61f2ff"
      : options.isComplete
        ? "#76f7b7"
        : "rgba(169, 194, 222, 0.48)";

    ctx.save();
    ctx.translate(gate.x, gate.y);
    ctx.lineWidth = options.isActive ? 7 : 3;
    ctx.strokeStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = options.isActive ? 26 + pulse * 14 : options.isComplete ? 12 : 0;
    ctx.globalAlpha = options.isComplete && !options.isActive ? 0.5 : 1;
    ctx.beginPath();
    ctx.arc(0, 0, gate.radius, 0, Math.PI * 2);
    ctx.stroke();

    if (options.isActive) {
      ctx.globalAlpha = 0.28;
      ctx.beginPath();
      ctx.arc(0, 0, gate.radius + 14 + pulse * 8, 0, Math.PI * 2);
      ctx.stroke();
    }

    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
    ctx.fillStyle = color;
    ctx.font = options.isStart ? "800 16px Inter, sans-serif" : "900 28px Inter, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(options.label, 0, 0);
    ctx.restore();
  }

  drawPlanets(ctx) {
    for (const planet of COURSE.planets) {
      const gradient = ctx.createRadialGradient(
        planet.x - planet.radius * 0.35,
        planet.y - planet.radius * 0.35,
        planet.radius * 0.1,
        planet.x,
        planet.y,
        planet.radius,
      );
      gradient.addColorStop(0, "#ffffff");
      gradient.addColorStop(0.12, planet.colors[0]);
      gradient.addColorStop(1, planet.colors[1]);
      ctx.fillStyle = gradient;
      ctx.shadowColor = planet.colors[0];
      ctx.shadowBlur = 18;
      ctx.beginPath();
      ctx.arc(planet.x, planet.y, planet.radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.strokeStyle = "rgba(255, 255, 255, 0.16)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(planet.x, planet.y, planet.radius + 5, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  drawAsteroids(ctx, timeSeconds) {
    COURSE.asteroids.forEach((asteroid, index) => {
      const shape = this.asteroidShapes[index];
      ctx.save();
      ctx.translate(asteroid.x, asteroid.y);
      ctx.rotate(timeSeconds * asteroid.spin);
      ctx.fillStyle = "#8a7564";
      ctx.strokeStyle = "#d1b79d";
      ctx.lineWidth = 2;
      ctx.shadowColor = "rgba(255, 154, 96, 0.42)";
      ctx.shadowBlur = 10;
      ctx.beginPath();
      shape.forEach((point, pointIndex) => {
        if (pointIndex === 0) {
          ctx.moveTo(point.x, point.y);
        } else {
          ctx.lineTo(point.x, point.y);
        }
      });
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    });
  }

  drawCraft(ctx, state) {
    const craft = state.craft;
    ctx.save();
    ctx.translate(craft.x, craft.y);
    ctx.rotate(craft.angle);

    if (craft.thrusting) {
      const flame = ctx.createLinearGradient(-16, 0, -42, 0);
      flame.addColorStop(0, "rgba(255, 255, 255, 0.95)");
      flame.addColorStop(0.35, "rgba(97, 242, 255, 0.85)");
      flame.addColorStop(1, "rgba(255, 117, 91, 0)");
      ctx.fillStyle = flame;
      ctx.beginPath();
      ctx.moveTo(-15, -7);
      ctx.lineTo(-42, 0);
      ctx.lineTo(-15, 7);
      ctx.closePath();
      ctx.fill();
    }

    if (craft.braking) {
      ctx.strokeStyle = "rgba(255, 209, 102, 0.75)";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(-2, 0, 23, -0.75, 0.75);
      ctx.stroke();
    }

    ctx.fillStyle = "#eaf7ff";
    ctx.strokeStyle = "#61f2ff";
    ctx.lineWidth = 2;
    ctx.shadowColor = "#61f2ff";
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.moveTo(20, 0);
    ctx.lineTo(-13, -12);
    ctx.lineTo(-7, 0);
    ctx.lineTo(-13, 12);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#0c1c35";
    ctx.beginPath();
    ctx.arc(6, 0, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    ctx.strokeStyle = "rgba(97, 242, 255, 0.45)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(craft.x, craft.y);
    ctx.lineTo(craft.x - craft.vx * 0.18, craft.y - craft.vy * 0.18);
    ctx.stroke();
  }

  drawEffects(ctx, state) {
    if (state.effects.checkpoint > 0 || state.effects.lap > 0 || state.effects.finish > 0) {
      const target = getActiveTarget(state);
      const glow = Math.max(state.effects.checkpoint, state.effects.lap, state.effects.finish);
      ctx.strokeStyle = `rgba(118, 247, 183, ${Math.min(0.7, glow)})`;
      ctx.lineWidth = 8;
      ctx.beginPath();
      ctx.arc(target.x, target.y, target.radius + 26 * (1 - glow), 0, Math.PI * 2);
      ctx.stroke();
    }

    if (state.effects.collision > 0) {
      const alpha = Math.min(0.28, state.effects.collision * 0.38);
      ctx.fillStyle = `rgba(255, 70, 105, ${alpha})`;
      ctx.fillRect(0, 0, COURSE.width, COURSE.height);
      ctx.strokeStyle = `rgba(255, 107, 138, ${alpha + 0.22})`;
      ctx.lineWidth = 5;
      ctx.beginPath();
      ctx.arc(state.craft.x, state.craft.y, 35 + state.effects.collision * 25, 0, Math.PI * 2);
      ctx.stroke();
    }
  }
}

class Game {
  constructor() {
    this.canvas = document.getElementById("gameCanvas");
    this.state = createInitialGameState({ bestTime: readBestTime() });
    this.renderer = new Renderer(this.canvas);
    this.hud = new Hud();
    this.lastFrameTime = null;
    this.input = new InputController(this.canvas, {
      onStart: () => this.startOrResume(),
      onRestart: () => this.restart(),
      onPauseToggle: () => this.togglePause(),
      onSuspend: () => this.suspend(),
    });

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        this.suspend();
      } else {
        this.lastFrameTime = null;
      }
    });
  }

  start() {
    this.canvas.focus();
    this.installDebugSurface();
    requestAnimationFrame((time) => this.loop(time));
  }

  startOrResume() {
    if (this.state.state === GAME_STATE.FINISHED) {
      this.state = restartGame(this.state);
    }
    startRace(this.state);
  }

  togglePause() {
    if (this.state.state === GAME_STATE.PLAYING) {
      setPaused(this.state, true);
      this.input.clearMotionKeys();
      this.lastFrameTime = null;
    } else if (this.state.state === GAME_STATE.PAUSED) {
      setPaused(this.state, false);
      this.lastFrameTime = null;
    }
  }

  suspend() {
    if (this.state.state === GAME_STATE.PLAYING) {
      setPaused(this.state, true);
    }
    this.input.clearMotionKeys();
    this.lastFrameTime = null;
  }

  restart() {
    this.state = restartGame(this.state);
    this.input.clearMotionKeys();
    this.lastFrameTime = null;
  }

  loop(now) {
    const dt = this.lastFrameTime === null ? 0 : (now - this.lastFrameTime) / 1000;
    this.lastFrameTime = now;

    updateGame(this.state, this.input.snapshot(), dt);
    this.recordFinishIfNeeded();
    this.renderer.render(this.state, now / 1000);
    this.hud.update(this.state);

    requestAnimationFrame((time) => this.loop(time));
  }

  recordFinishIfNeeded() {
    if (
      this.state.state !== GAME_STATE.FINISHED ||
      this.state.finishRecorded ||
      !Number.isFinite(this.state.timer.final)
    ) {
      return;
    }

    if (this.state.bestTime === null || this.state.timer.final < this.state.bestTime) {
      this.state.bestTime = this.state.timer.final;
      writeBestTime(this.state.bestTime);
    }

    this.state.finishRecorded = true;
  }

  installDebugSurface() {
    window.orbitalDrift = {
      getSnapshot: () => ({
        state: this.state.state,
        lap: this.state.progress.lap,
        requiredLaps: this.state.progress.requiredLaps,
        nextCheckpoint: this.state.progress.nextCheckpoint,
        timer: { ...this.state.timer },
        bestTime: this.state.bestTime,
        craft: { ...this.state.craft },
        target: getActiveTarget(this.state),
        effects: { ...this.state.effects },
        course: {
          startGate: COURSE.startGate,
          checkpoints: COURSE.checkpoints,
          asteroids: COURSE.asteroids,
          planets: COURSE.planets,
          gravityWells: COURSE.gravityWells,
        },
        message: { ...this.state.message },
      }),
      restart: () => this.restart(),
      pause: () => setPaused(this.state, true),
      resume: () => setPaused(this.state, false),
    };
  }
}

function readyOverlayMarkup() {
  return `
    <p class="eyebrow">Ready on the line</p>
    <h2>Thread the gates, bend around gravity, beat your best time.</h2>
    <p>
      Fly through the glowing gates in order for two laps. Avoid asteroids and planets;
      gravity wells tug your racing line but can be recovered from.
    </p>
    <dl class="controls-grid">
      <div><dt>Rotate</dt><dd>A / D or Arrow Left / Right</dd></div>
      <div><dt>Thrust</dt><dd>W or Arrow Up</dd></div>
      <div><dt>Brake</dt><dd>Space</dd></div>
      <div><dt>Pause</dt><dd>P or Escape</dd></div>
      <div><dt>Restart</dt><dd>R</dd></div>
    </dl>
    <p class="start-hint">Press W, Arrow Up, or Enter to start.</p>
  `;
}

function readBestTime() {
  try {
    const value = window.localStorage.getItem(BEST_TIME_KEY);
    if (value === null) {
      return null;
    }

    const parsed = Number.parseFloat(value);
    if (Number.isFinite(parsed) && parsed > 0) {
      return parsed;
    }

    console.warn("Ignoring invalid Orbital Drift best-time value in localStorage.");
    return null;
  } catch (error) {
    console.warn("Orbital Drift could not read localStorage best time.", error);
    return null;
  }
}

function writeBestTime(time) {
  try {
    window.localStorage.setItem(BEST_TIME_KEY, String(time));
  } catch (error) {
    console.warn("Orbital Drift could not persist localStorage best time.", error);
  }
}

function normalizeKey(key) {
  return key.length === 1 ? key.toLowerCase() : key.toLowerCase();
}

function createStarfield(count) {
  return Array.from({ length: count }, (_, index) => ({
    x: seeded(index, 11) * COURSE.width,
    y: seeded(index, 23) * COURSE.height,
    radius: 0.8 + seeded(index, 37) * 1.8,
    alpha: 0.35 + seeded(index, 47) * 0.65,
    phase: seeded(index, 59) * Math.PI * 2,
    speed: 0.6 + seeded(index, 71) * 1.8,
    color: seeded(index, 83) > 0.78 ? "#bcecff" : "#ffffff",
  }));
}

function createAsteroidShape(radius, seedOffset) {
  const points = 10;
  return Array.from({ length: points }, (_, index) => {
    const angle = (index / points) * Math.PI * 2;
    const roughness = 0.72 + seeded(seedOffset * 19 + index, 101) * 0.46;
    return {
      x: Math.cos(angle) * radius * roughness,
      y: Math.sin(angle) * radius * roughness,
    };
  });
}

function seeded(index, salt) {
  const x = Math.sin(index * 999.91 + salt * 77.17) * 10000;
  return x - Math.floor(x);
}

function hexToRgba(hex, alpha) {
  const stripped = hex.replace("#", "");
  const value = Number.parseInt(stripped, 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

new Game().start();
