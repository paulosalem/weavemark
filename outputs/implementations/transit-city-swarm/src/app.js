import {
  WORLD_HEIGHT,
  WORLD_WIDTH,
  attemptPlaceStation,
  beginRound,
  createGameState,
  endRound,
  eraseLastStation,
  fieldIndexToWorld,
  findStationAt,
  getLineStations,
  getSnapshot,
  pauseGame,
  readField,
  restartRound,
  resumeGame,
  setMode,
  setSpeed,
  togglePause,
  updateGame,
  upgradeStation
} from "./simulation.js";

const HIGH_SCORE_KEY = "transit-city-swarm.highScore";

const canvas = document.querySelector("#gameCanvas");
const ctx = canvas.getContext("2d", { alpha: false });
const menuScreen = document.querySelector("#menuScreen");
const resultsScreen = document.querySelector("#resultsScreen");
const pauseButton = document.querySelector("#pauseButton");
const restartButton = document.querySelector("#restartButton");
const finishButton = document.querySelector("#finishButton");
const speedButton = document.querySelector("#speedButton");
const startButton = document.querySelector("#startButton");
const playAgainButton = document.querySelector("#playAgainButton");
const messageEl = document.querySelector("#message");
const statusEl = document.querySelector("#gameStatus");
const resultTitle = document.querySelector("#resultTitle");
const resultBody = document.querySelector("#resultBody");
const highScoreEl = document.querySelector("#highScore");
const toolButtons = [...document.querySelectorAll("[data-mode]")];
const statEls = Object.fromEntries(
  [...document.querySelectorAll("[data-stat]")].map((element) => [element.dataset.stat, element])
);
const scoreFill = document.querySelector("#scoreFill");
const canvasWrap = document.querySelector(".canvas-wrap");

let state = createGameState();
let viewport = { scale: 1, offsetX: 0, offsetY: 0, width: WORLD_WIDTH, height: WORLD_HEIGHT, dpr: 1 };
let lastFrame = performance.now();
let resultSavedForScore = null;

function frame(now) {
  const dt = Math.min(0.05, (now - lastFrame) / 1000);
  lastFrame = now;
  updateGame(state, dt);
  render();
  syncUi();
  requestAnimationFrame(frame);
}

function render() {
  prepareCanvas();
  paintSkylineBackdrop();
  paintDistricts();
  paintRoads();
  paintTrails();
  paintBuildings();
  paintTransitLine();
  paintAgents();
  paintHoverPreview();
  paintMapChrome();
}

function prepareCanvas() {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const nextWidth = Math.max(1, Math.round(rect.width * dpr));
  const nextHeight = Math.max(1, Math.round(rect.height * dpr));
  if (canvas.width !== nextWidth || canvas.height !== nextHeight) {
    canvas.width = nextWidth;
    canvas.height = nextHeight;
  }

  const cssWidth = rect.width;
  const cssHeight = rect.height;
  const scale = Math.min(cssWidth / WORLD_WIDTH, cssHeight / WORLD_HEIGHT);
  const offsetX = (cssWidth - WORLD_WIDTH * scale) / 2;
  const offsetY = (cssHeight - WORLD_HEIGHT * scale) / 2;
  viewport = { scale, offsetX, offsetY, width: cssWidth, height: cssHeight, dpr };

  ctx.setTransform(1, 0, 0, 1, 0, 0);
  const backdrop = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  backdrop.addColorStop(0, "#08111f");
  backdrop.addColorStop(0.55, "#0c1426");
  backdrop.addColorStop(1, "#111827");
  ctx.fillStyle = backdrop;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.setTransform(dpr * scale, 0, 0, dpr * scale, dpr * offsetX, dpr * offsetY);
}

function paintSkylineBackdrop() {
  const base = ctx.createLinearGradient(0, 0, WORLD_WIDTH, WORLD_HEIGHT);
  base.addColorStop(0, "#0a1728");
  base.addColorStop(0.55, "#0d1c2e");
  base.addColorStop(1, "#101720");
  ctx.fillStyle = base;
  roundedRect(ctx, 0, 0, WORLD_WIDTH, WORLD_HEIGHT, 26);
  ctx.fill();

  ctx.save();
  ctx.globalAlpha = 0.22;
  ctx.strokeStyle = "#9bd7ff";
  ctx.lineWidth = 1;
  for (let x = 32; x < WORLD_WIDTH; x += 32) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, WORLD_HEIGHT);
    ctx.stroke();
  }
  for (let y = 32; y < WORLD_HEIGHT; y += 32) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(WORLD_WIDTH, y);
    ctx.stroke();
  }
  ctx.restore();
}

function paintDistricts() {
  for (const district of state.districts) {
    const glow = ctx.createRadialGradient(district.x, district.y, 8, district.x, district.y, 154);
    glow.addColorStop(0, hexToRgba(district.tint, 0.25));
    glow.addColorStop(0.62, hexToRgba(district.tint, 0.08));
    glow.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(district.x, district.y, 154, 0, Math.PI * 2);
    ctx.fill();

    ctx.font = "600 13px system-ui, sans-serif";
    ctx.fillStyle = hexToRgba(district.tint, 0.9);
    ctx.fillText(district.name, district.x - 48, district.y - 118);
  }
}

function paintRoads() {
  ctx.save();
  ctx.lineCap = "round";
  for (const road of state.roads) {
    ctx.strokeStyle = road.kind === "greenway" ? "rgba(136, 255, 190, 0.2)" : "rgba(198, 222, 244, 0.18)";
    ctx.lineWidth = road.kind === "avenue" ? 5 : 3;
    ctx.beginPath();
    ctx.moveTo(road.x1, road.y1);
    ctx.lineTo(road.x2, road.y2);
    ctx.stroke();
  }
  ctx.restore();
}

function paintTrails() {
  ctx.save();
  ctx.globalCompositeOperation = "lighter";
  for (let i = 0; i < state.trail.length; i += 1) {
    const value = state.trail[i];
    if (value < 0.08) {
      continue;
    }
    const cell = fieldIndexToWorld(i);
    const alpha = Math.min(0.38, value / 46);
    ctx.fillStyle = `rgba(255, 183, 82, ${alpha})`;
    roundedRect(ctx, cell.x + 1, cell.y + 1, cell.width + 2, cell.height + 2, 6);
    ctx.fill();
  }
  ctx.restore();

  for (let i = 0; i < state.congestion.length; i += 1) {
    const value = state.congestion[i];
    if (value < 0.35) {
      continue;
    }
    const cell = fieldIndexToWorld(i);
    const alpha = Math.min(0.32, value / 15);
    ctx.fillStyle = `rgba(248, 88, 74, ${alpha})`;
    roundedRect(ctx, cell.x + 2, cell.y + 2, cell.width - 2, cell.height - 2, 5);
    ctx.fill();
  }
}

function paintBuildings() {
  for (const building of state.buildings) {
    const centerX = building.x + building.width / 2;
    const centerY = building.y + building.height / 2;
    const access = readField(state.trail, centerX, centerY);
    const popRatio = building.population / building.maxPopulation;
    const lift = Math.max(0, building.growth) * 26;

    ctx.save();
    ctx.shadowColor = building.growth > 0.02 ? "rgba(102, 255, 196, 0.5)" : "rgba(0,0,0,0)";
    ctx.shadowBlur = building.growth > 0.02 ? 16 : 0;
    ctx.fillStyle = mixColor(building.color, "#ffffff", Math.min(0.22, access / 80));
    ctx.globalAlpha = 0.78 + popRatio * 0.18;
    roundedRect(
      ctx,
      building.x,
      building.y - lift,
      building.width,
      building.height + lift,
      5
    );
    ctx.fill();
    ctx.restore();

    ctx.fillStyle = `rgba(7, 13, 24, ${0.24 + popRatio * 0.25})`;
    roundedRect(ctx, building.x + 3, building.y + building.height - 5, building.width - 6, 3, 2);
    ctx.fill();
  }
}

function paintTransitLine() {
  const stations = getLineStations(state);
  if (stations.length >= 2) {
    ctx.save();
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    ctx.shadowColor = "rgba(54, 215, 255, 0.58)";
    ctx.shadowBlur = 18;
    ctx.strokeStyle = "rgba(54, 215, 255, 0.42)";
    ctx.lineWidth = 18;
    drawStationPath(stations);
    ctx.stroke();

    ctx.shadowBlur = 0;
    ctx.strokeStyle = "#36d7ff";
    ctx.lineWidth = 7;
    drawStationPath(stations);
    ctx.stroke();
    ctx.restore();

    paintVehicles(stations);
  }

  for (const station of stations) {
    const selected = station.id === state.selectedStationId;
    const overload = Math.max(0, station.load - station.capacity);
    ctx.save();
    ctx.shadowColor = selected ? "rgba(255,255,255,0.8)" : "rgba(54,215,255,0.55)";
    ctx.shadowBlur = selected ? 20 : 12;
    ctx.fillStyle = "#061925";
    ctx.beginPath();
    ctx.arc(station.x, station.y, 15 + station.level * 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.lineWidth = 4;
    ctx.strokeStyle = overload > 0 ? "#fb7185" : "#a7f3d0";
    ctx.stroke();
    ctx.fillStyle = selected ? "#ffffff" : "#bff8ff";
    ctx.beginPath();
    ctx.arc(station.x, station.y, 5 + station.level, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    if (station.load > 0) {
      const loadRatio = Math.min(1, station.load / station.capacity);
      ctx.strokeStyle = overload > 0 ? "#fb7185" : "#facc15";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(station.x, station.y, 24, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * loadRatio);
      ctx.stroke();
    }
  }
}

function drawStationPath(stations) {
  ctx.beginPath();
  ctx.moveTo(stations[0].x, stations[0].y);
  for (let i = 1; i < stations.length; i += 1) {
    const previous = stations[i - 1];
    const current = stations[i];
    const midX = (previous.x + current.x) / 2;
    const midY = (previous.y + current.y) / 2;
    ctx.quadraticCurveTo(midX, midY, current.x, current.y);
  }
}

function paintVehicles(stations) {
  if (stations.length < 2) {
    return;
  }
  const vehicleCount = Math.min(5, stations.length);
  for (let i = 0; i < vehicleCount; i += 1) {
    const travel = (state.time * 0.12 + i / vehicleCount) % 1;
    const segmentFloat = travel * (stations.length - 1);
    const segmentIndex = Math.min(stations.length - 2, Math.floor(segmentFloat));
    const t = segmentFloat - segmentIndex;
    const from = stations[segmentIndex];
    const to = stations[segmentIndex + 1];
    const x = from.x + (to.x - from.x) * t;
    const y = from.y + (to.y - from.y) * t;
    const angle = Math.atan2(to.y - from.y, to.x - from.x);

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.shadowColor = "rgba(180, 255, 245, 0.8)";
    ctx.shadowBlur = 10;
    ctx.fillStyle = "#e0fffb";
    roundedRect(ctx, -12, -5, 24, 10, 6);
    ctx.fill();
    ctx.restore();
  }
}

function paintAgents() {
  ctx.save();
  ctx.globalCompositeOperation = "lighter";
  for (const agent of state.agents) {
    ctx.fillStyle = agent.usedTransit
      ? `hsla(${agent.hue}, 92%, 67%, 0.88)`
      : `hsla(${agent.hue}, 90%, 60%, 0.58)`;
    ctx.beginPath();
    ctx.arc(agent.x, agent.y, agent.usedTransit ? 3.2 : 2.7, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

function paintHoverPreview() {
  if (!state.hover || state.status !== "playing") {
    return;
  }

  const hoverStation = findStationAt(state, state.hover.x, state.hover.y, 32);
  ctx.save();
  if (state.mode === "build") {
    const stations = getLineStations(state);
    const last = stations[stations.length - 1];
    if (last) {
      ctx.setLineDash([10, 8]);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.52)";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(last.x, last.y);
      ctx.lineTo(state.hover.x, state.hover.y);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.strokeStyle = "rgba(255,255,255,0.65)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(state.hover.x, state.hover.y, 16, 0, Math.PI * 2);
    ctx.stroke();
  } else if (hoverStation) {
    ctx.strokeStyle = state.mode === "upgrade" ? "#facc15" : "#ffffff";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(hoverStation.x, hoverStation.y, 28, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.restore();
}

function paintMapChrome() {
  ctx.save();
  ctx.strokeStyle = "rgba(255,255,255,0.12)";
  ctx.lineWidth = 2;
  roundedRect(ctx, 1, 1, WORLD_WIDTH - 2, WORLD_HEIGHT - 2, 26);
  ctx.stroke();

  ctx.font = "600 12px system-ui, sans-serif";
  ctx.fillStyle = "rgba(220, 248, 255, 0.68)";
  ctx.fillText("Original procedural city seed 1427", 24, WORLD_HEIGHT - 22);
  ctx.restore();
}

function syncUi() {
  const snapshot = getSnapshot(state);
  statEls.budget.textContent = `${snapshot.budget}`;
  statEls.score.textContent = `${snapshot.score}`;
  statEls.reliability.textContent = `${snapshot.reliability}%`;
  statEls.population.textContent = `${snapshot.population}`;
  statEls.served.textContent = `${snapshot.served}`;
  statEls.stops.textContent = `${snapshot.stops}`;
  statEls.agents.textContent = `${snapshot.agents}`;
  statEls.time.textContent = formatTime(snapshot.timeRemaining);
  highScoreEl.textContent = String(loadHighScore());
  scoreFill.style.width = `${Math.min(100, snapshot.score / 9)}%`;

  const statusLabels = {
    menu: "Menu",
    playing: "Playing",
    paused: "Paused",
    results: "Results"
  };
  statusEl.textContent = statusLabels[state.status];
  statusEl.dataset.status = state.status;
  pauseButton.textContent = state.status === "paused" ? "Resume" : "Pause";
  pauseButton.disabled = state.status === "menu" || state.status === "results";
  finishButton.disabled = state.status === "menu" || state.status === "results";
  speedButton.textContent = `${state.speed}x speed`;

  messageEl.textContent = state.message;
  messageEl.dataset.tone = state.messageTone;
  messageEl.classList.toggle("is-dimmed", state.messageTimer <= 0);

  for (const button of toolButtons) {
    const active = button.dataset.mode === state.mode;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  }

  canvasWrap.classList.toggle("is-paused", state.status === "paused");
  menuScreen.hidden = state.status !== "menu";
  resultsScreen.hidden = state.status !== "results";
  resultsScreen.setAttribute("aria-hidden", String(state.status !== "results"));

  if (state.status === "results" && state.result) {
    if (resultSavedForScore !== state.result.score) {
      saveHighScore(state.result.score);
      resultSavedForScore = state.result.score;
    }
    resultTitle.textContent = state.result.outcome === "win" ? "City synchronized" : "Shift report";
    resultBody.textContent =
      `Score ${state.result.score}, ${state.result.served} trips served, ` +
      `${state.result.reliability}% reliability, budget ${state.result.budget}.`;
  }
}

function handleCanvasPointer(event) {
  const point = eventToWorld(event);
  state.hover = point;
  if (!isInsideWorld(point)) {
    return;
  }

  if (state.status === "menu") {
    state = beginRound(state);
    resultSavedForScore = null;
  }

  if (state.status !== "playing") {
    return;
  }

  const station = findStationAt(state, point.x, point.y, 30);
  if (state.mode === "build") {
    attemptPlaceStation(state, point.x, point.y);
  } else if (state.mode === "select") {
    if (station) {
      state.selectedStationId = station.id;
      state.message = `${station.name}: level ${station.level}, load ${Math.round(station.load)}/${station.capacity}, boardings ${station.lifetimeBoardings}.`;
      state.messageTone = "hint";
      state.messageTimer = 4;
    }
  } else if (state.mode === "upgrade") {
    if (station) {
      upgradeStation(state, station.id);
    }
  } else if (state.mode === "erase") {
    const lastId = state.lines[0].stationIds[state.lines[0].stationIds.length - 1];
    if (station?.id === lastId) {
      eraseLastStation(state);
    } else {
      state.message = "Pruning is constrained to the newest stop so the line remains readable.";
      state.messageTone = "warning";
      state.messageTimer = 3.5;
    }
  }
}

function eventToWorld(event) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (event.clientX - rect.left - viewport.offsetX) / viewport.scale,
    y: (event.clientY - rect.top - viewport.offsetY) / viewport.scale
  };
}

function isInsideWorld(point) {
  return point.x >= 0 && point.x <= WORLD_WIDTH && point.y >= 0 && point.y <= WORLD_HEIGHT;
}

function cycleSpeed() {
  const next = state.speed === 1 ? 2 : state.speed === 2 ? 4 : 1;
  setSpeed(state, next);
}

function loadHighScore() {
  return Number(localStorage.getItem(HIGH_SCORE_KEY) || 0);
}

function saveHighScore(score) {
  const highScore = loadHighScore();
  if (score > highScore) {
    localStorage.setItem(HIGH_SCORE_KEY, String(score));
  }
}

function formatTime(seconds) {
  const safe = Math.max(0, Math.ceil(seconds));
  const minutes = Math.floor(safe / 60);
  const remainder = String(safe % 60).padStart(2, "0");
  return `${minutes}:${remainder}`;
}

function roundedRect(context, x, y, width, height, radius) {
  const r = Math.min(radius, Math.abs(width) / 2, Math.abs(height) / 2);
  context.beginPath();
  context.moveTo(x + r, y);
  context.arcTo(x + width, y, x + width, y + height, r);
  context.arcTo(x + width, y + height, x, y + height, r);
  context.arcTo(x, y + height, x, y, r);
  context.arcTo(x, y, x + width, y, r);
  context.closePath();
}

function hexToRgba(hex, alpha) {
  const normalized = hex.replace("#", "");
  const value = Number.parseInt(normalized, 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function mixColor(hexA, hexB, amount) {
  const a = Number.parseInt(hexA.replace("#", ""), 16);
  const b = Number.parseInt(hexB.replace("#", ""), 16);
  const ar = (a >> 16) & 255;
  const ag = (a >> 8) & 255;
  const ab = a & 255;
  const br = (b >> 16) & 255;
  const bg = (b >> 8) & 255;
  const bb = b & 255;
  const r = Math.round(ar + (br - ar) * amount);
  const g = Math.round(ag + (bg - ag) * amount);
  const bl = Math.round(ab + (bb - ab) * amount);
  return `rgb(${r}, ${g}, ${bl})`;
}

canvas.addEventListener("pointerdown", (event) => {
  event.preventDefault();
  canvas.setPointerCapture(event.pointerId);
  handleCanvasPointer(event);
});

canvas.addEventListener("pointermove", (event) => {
  state.hover = eventToWorld(event);
});

canvas.addEventListener("pointerleave", () => {
  state.hover = null;
});

startButton.addEventListener("click", () => {
  state = beginRound(state);
  resultSavedForScore = null;
});

playAgainButton.addEventListener("click", () => {
  state = restartRound(state);
  resultSavedForScore = null;
});

restartButton.addEventListener("click", () => {
  state = restartRound(state);
  resultSavedForScore = null;
});

pauseButton.addEventListener("click", () => {
  if (state.status === "paused") {
    resumeGame(state);
  } else {
    pauseGame(state);
  }
});

finishButton.addEventListener("click", () => {
  endRound(state, "complete");
});

speedButton.addEventListener("click", cycleSpeed);

for (const button of toolButtons) {
  button.addEventListener("click", () => {
    setMode(state, button.dataset.mode);
  });
}

document.addEventListener("keydown", (event) => {
  if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
    return;
  }
  if (event.key === " ") {
    event.preventDefault();
    togglePause(state);
  } else if (event.key.toLowerCase() === "r") {
    state = restartRound(state);
    resultSavedForScore = null;
  } else if (event.key === "1") {
    setMode(state, "build");
  } else if (event.key === "2") {
    setMode(state, "select");
  } else if (event.key === "3") {
    setMode(state, "upgrade");
  } else if (event.key.toLowerCase() === "e") {
    setMode(state, "erase");
  } else if (event.key === "+" || event.key === "=") {
    setSpeed(state, Math.min(4, state.speed + 1));
  } else if (event.key === "-" || event.key === "_") {
    setSpeed(state, Math.max(1, state.speed - 1));
  } else if (event.key === "Escape") {
    pauseGame(state);
  }
});

document.addEventListener("visibilitychange", () => {
  if (document.hidden && state.status === "playing") {
    pauseGame(state);
  }
});

window.addEventListener("blur", () => {
  if (state.status === "playing") {
    pauseGame(state);
  }
});

window.__transitCitySwarm = {
  getState: () => state,
  getSnapshot: () => getSnapshot(state),
  actions: {
    begin: () => {
      state = beginRound(state);
      resultSavedForScore = null;
      return state;
    },
    restart: () => {
      state = restartRound(state);
      resultSavedForScore = null;
      return state;
    },
    end: () => endRound(state, "complete"),
    setMode: (mode) => setMode(state, mode),
    setSpeed: (speed) => setSpeed(state, speed)
  }
};

syncUi();
requestAnimationFrame(frame);
