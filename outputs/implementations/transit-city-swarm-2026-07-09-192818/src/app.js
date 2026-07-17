import {
  BLOCKERS,
  COSTS,
  DISTRICTS,
  WORLD,
  createGame,
  findSegmentAt,
  findStationAt,
  formatClock,
  getCellCenter,
  getRemainingSeconds,
  setMode,
  setSpeed,
  startRun,
  stationById,
  stepGame,
  summarize,
  togglePause,
  tryBuildStation,
  tryDeleteAt,
  tryUpgradeAt
} from "./simulation.js";

const canvas = document.querySelector("#gameCanvas");
const ctx = canvas.getContext("2d");
const overlay = document.querySelector("#overlay");
const overlayEyebrow = document.querySelector("#overlayEyebrow");
const overlayTitle = document.querySelector("#overlayTitle");
const overlayBody = document.querySelector("#overlayBody");
const overlayButton = document.querySelector("#overlayButton");
const startButton = document.querySelector("#startButton");
const pauseButton = document.querySelector("#pauseButton");
const restartButton = document.querySelector("#restartButton");
const toast = document.querySelector("#toast");
const statusLine = document.querySelector("#statusLine");
const scoreValue = document.querySelector("#scoreValue");
const budgetValue = document.querySelector("#budgetValue");
const reliabilityValue = document.querySelector("#reliabilityValue");
const reliabilityMeter = document.querySelector("#reliabilityMeter");
const pressureValue = document.querySelector("#pressureValue");
const pressureMeter = document.querySelector("#pressureMeter");
const timeValue = document.querySelector("#timeValue");
const tripsValue = document.querySelector("#tripsValue");
const stationsValue = document.querySelector("#stationsValue");
const agentsValue = document.querySelector("#agentsValue");

let game = createGame();
let hover = null;
let lastFrame = performance.now();
let toastTimer = 0;

const drawCosts = new Map([
  ["build", `Stop $${COSTS.station}+`],
  ["upgrade", `Station $${COSTS.stationUpgrade} / segment $${COSTS.segmentUpgrade}`],
  ["delete", `Prune $${COSTS.prune}`]
]);

resizeCanvas();
syncUi();
requestAnimationFrame(loop);

window.addEventListener("resize", resizeCanvas);
window.addEventListener("blur", pauseForVisibility);
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    pauseForVisibility();
  }
});

canvas.addEventListener("pointermove", (event) => {
  hover = eventToWorld(event);
});

canvas.addEventListener("pointerleave", () => {
  hover = null;
});

canvas.addEventListener("pointerdown", (event) => {
  const point = eventToWorld(event);
  if (game.phase === "menu") {
    game = startRun(game);
  }
  if (game.mode === "build") {
    showResult(tryBuildStation(game, point.x, point.y));
  } else if (game.mode === "upgrade") {
    showResult(tryUpgradeAt(game, point.x, point.y));
  } else {
    showResult(tryDeleteAt(game, point.x, point.y));
  }
  syncUi();
});

document.querySelectorAll("[data-mode]").forEach((button) => {
  button.addEventListener("click", () => {
    showResult(setMode(game, button.dataset.mode));
    syncUi();
  });
});

document.querySelectorAll("[data-speed]").forEach((button) => {
  button.addEventListener("click", () => {
    setSpeed(game, Number(button.dataset.speed));
    syncUi();
  });
});

startButton.addEventListener("click", () => {
  game = startRun(game);
  syncUi();
});

overlayButton.addEventListener("click", () => {
  if (game.phase === "results") {
    game = createGame(game.seed);
  }
  game = startRun(game);
  syncUi();
});

pauseButton.addEventListener("click", () => {
  togglePause(game);
  syncUi();
});

restartButton.addEventListener("click", () => {
  game = createGame(game.seed);
  syncUi();
});

document.addEventListener("keydown", (event) => {
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
    return;
  }
  const key = event.key.toLowerCase();
  if (key === " ") {
    event.preventDefault();
    togglePause(game);
  } else if (key === "b") {
    setMode(game, "build");
  } else if (key === "u") {
    setMode(game, "upgrade");
  } else if (key === "d") {
    setMode(game, "delete");
  } else if (key === "r") {
    game = createGame(game.seed);
  } else if (["1", "2", "4"].includes(key)) {
    setSpeed(game, Number(key));
  }
  syncUi();
});

function loop(now) {
  const dt = Math.min(0.12, (now - lastFrame) / 1000);
  lastFrame = now;
  stepGame(game, dt);
  if (toastTimer > 0) {
    toastTimer -= dt;
    if (toastTimer <= 0) {
      toast.classList.remove("visible");
    }
  }
  render();
  syncUi();
  requestAnimationFrame(loop);
}

function render() {
  ctx.save();
  ctx.setTransform(canvas.width / WORLD.width, 0, 0, canvas.height / WORLD.height, 0, 0);
  ctx.clearRect(0, 0, WORLD.width, WORLD.height);
  drawBackground();
  drawDistricts();
  drawFields();
  drawRoads();
  drawBuildings();
  drawNetwork();
  drawAgents();
  drawHover();
  ctx.restore();
}

function drawBackground() {
  const gradient = ctx.createLinearGradient(0, 0, WORLD.width, WORLD.height);
  gradient.addColorStop(0, "#081521");
  gradient.addColorStop(0.58, "#0e1f30");
  gradient.addColorStop(1, "#102033");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, WORLD.width, WORLD.height);

  ctx.strokeStyle = "rgba(148, 188, 215, 0.05)";
  ctx.lineWidth = 1;
  for (let x = 0; x <= WORLD.width; x += WORLD.cellSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, WORLD.height);
    ctx.stroke();
  }
  for (let y = 0; y <= WORLD.height; y += WORLD.cellSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(WORLD.width, y);
    ctx.stroke();
  }
}

function drawDistricts() {
  for (const district of DISTRICTS) {
    const gradient = ctx.createLinearGradient(district.x, district.y, district.x + district.w, district.y + district.h);
    gradient.addColorStop(0, withAlpha(district.color, 0.18));
    gradient.addColorStop(1, withAlpha(district.color, 0.04));
    roundRect(district.x, district.y, district.w, district.h, 22);
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.strokeStyle = withAlpha(district.color, 0.28);
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = withAlpha("#d9f4ff", 0.72);
    ctx.font = "600 13px Inter, system-ui, sans-serif";
    ctx.fillText(district.name, district.x + 18, district.y + 26);
  }

  for (const blocker of BLOCKERS) {
    roundRect(blocker.x, blocker.y, blocker.w, blocker.h, 18);
    ctx.fillStyle = withAlpha(blocker.color, 0.78);
    ctx.fill();
    ctx.strokeStyle = withAlpha("#a8e8ff", 0.18);
    ctx.stroke();
  }
}

function drawRoads() {
  ctx.save();
  ctx.strokeStyle = "rgba(199, 226, 239, 0.13)";
  ctx.lineWidth = 2;
  const roads = [
    [[120, 140], [410, 250], [710, 160], [870, 150]],
    [[120, 420], [370, 355], [600, 360], [845, 455]],
    [[230, 105], [385, 250], [515, 360], [720, 470]],
    [[110, 495], [345, 315], [610, 250], [805, 110]]
  ];
  for (const road of roads) {
    ctx.beginPath();
    road.forEach(([x, y], index) => {
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
  }
  ctx.restore();
}

function drawFields() {
  for (let index = 0; index < game.trails.length; index += 1) {
    const trail = game.trails[index];
    const congestion = game.congestion[index];
    const glow = game.growthGlow[index];
    if (trail < 0.018 && congestion < 0.02 && glow < 0.02) {
      continue;
    }
    const { x, y } = getCellCenter(index);
    if (trail > 0.018) {
      ctx.fillStyle = `rgba(255, 184, 77, ${Math.min(0.48, trail * 0.62)})`;
      ctx.beginPath();
      ctx.arc(x, y, 8 + trail * 19, 0, Math.PI * 2);
      ctx.fill();
    }
    if (congestion > 0.02) {
      ctx.fillStyle = `rgba(255, 82, 92, ${Math.min(0.46, congestion * 0.58)})`;
      ctx.beginPath();
      ctx.arc(x, y, 7 + congestion * 23, 0, Math.PI * 2);
      ctx.fill();
    }
    if (glow > 0.02) {
      ctx.fillStyle = `rgba(97, 255, 170, ${Math.min(0.42, glow * 0.38)})`;
      ctx.beginPath();
      ctx.arc(x, y, 11 + glow * 16, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

function drawBuildings() {
  for (const building of game.buildings) {
    const width = 8 + building.level * 4;
    const height = 8 + building.level * 5;
    const color = building.type === "residential"
      ? "#9df3bd"
      : building.type === "commercial"
        ? "#91c8ff"
        : "#ffd084";
    ctx.fillStyle = withAlpha(color, 0.78);
    roundRect(building.x - width / 2, building.y - height / 2, width, height, 3);
    ctx.fill();
    if (building.accessibility > 0.2) {
      ctx.strokeStyle = withAlpha("#ffffff", 0.25 + building.accessibility * 0.28);
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  }
}

function drawNetwork() {
  ctx.save();
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  for (const segment of game.segments) {
    const from = stationById(game, segment.from);
    const to = stationById(game, segment.to);
    if (!from || !to) {
      continue;
    }
    const loadRatio = segment.load / Math.max(1, segment.capacity);
    ctx.strokeStyle = loadRatio > 1 ? "rgba(255, 108, 113, 0.92)" : "rgba(90, 203, 255, 0.9)";
    ctx.lineWidth = 7 + segment.level * 2;
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
    ctx.strokeStyle = "rgba(6, 25, 39, 0.78)";
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  for (const station of game.stations) {
    const selected = station.id === game.selectedStationId;
    const overload = station.load / Math.max(1, station.capacity);
    const radius = 11 + station.level * 2 + station.pulse * 3;
    ctx.fillStyle = overload > 1 ? "#ff6971" : selected ? "#ffffff" : "#7be1ff";
    ctx.strokeStyle = selected ? "#63f6b5" : "rgba(4, 20, 31, 0.95)";
    ctx.lineWidth = selected ? 4 : 3;
    ctx.beginPath();
    ctx.arc(station.x, station.y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = selected ? "#071521" : "#082238";
    ctx.font = "700 10px Inter, system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(station.level), station.x, station.y + 0.5);
  }
  ctx.restore();
}

function drawAgents() {
  ctx.save();
  for (const agent of game.agents) {
    ctx.fillStyle = agent.transit ? "rgba(148, 229, 255, 0.95)" : "rgba(255, 205, 122, 0.88)";
    ctx.beginPath();
    ctx.arc(agent.x, agent.y, agent.transit ? 3.6 : 2.8, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

function drawHover() {
  if (!hover || game.phase === "results") {
    return;
  }
  const station = findStationAt(game, hover.x, hover.y, 24);
  const segment = findSegmentAt(game, hover.x, hover.y, 14);
  const blocked = BLOCKERS.some((blocker) =>
    hover.x >= blocker.x && hover.x <= blocker.x + blocker.w && hover.y >= blocker.y && hover.y <= blocker.y + blocker.h
  );
  ctx.save();
  ctx.globalAlpha = blocked ? 0.8 : 0.62;
  ctx.strokeStyle = blocked ? "#ff6471" : game.mode === "build" ? "#63f6b5" : game.mode === "upgrade" ? "#ffffff" : "#ffcf7a";
  ctx.lineWidth = 2;
  ctx.setLineDash([6, 6]);
  ctx.beginPath();
  ctx.arc(hover.x, hover.y, station || segment ? 24 : 18, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

function syncUi() {
  const summary = summarize(game);
  scoreValue.textContent = String(summary.score);
  budgetValue.textContent = `$${summary.budget}`;
  reliabilityValue.textContent = `${Math.round(summary.reliability * 100)}%`;
  reliabilityMeter.value = summary.reliability;
  pressureValue.textContent = `${Math.round(summary.populationPressure * 100)}%`;
  pressureMeter.value = summary.populationPressure;
  timeValue.textContent = formatClock(getRemainingSeconds(game));
  tripsValue.textContent = String(summary.trips);
  stationsValue.textContent = String(summary.stations);
  agentsValue.textContent = String(summary.agents);
  statusLine.textContent = `${game.message} ${drawCosts.get(game.mode) ?? ""}`;

  pauseButton.textContent = game.phase === "paused" ? "Resume" : "Pause";
  startButton.disabled = game.phase === "playing" || game.phase === "paused";
  pauseButton.disabled = game.phase === "menu" || game.phase === "results";

  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === game.mode);
  });
  document.querySelectorAll("[data-speed]").forEach((button) => {
    button.classList.toggle("active", Number(button.dataset.speed) === game.speed);
  });

  if (game.phase === "menu") {
    overlay.classList.remove("hidden");
    overlayEyebrow.textContent = "Ready";
    overlayTitle.textContent = "Grow a city by listening to its swarm.";
    overlayBody.textContent = "Citizens begin by walking through pressure corridors. Draw readable lines, upgrade overloaded places, and prune bad routes.";
    overlayButton.textContent = "Start round";
  } else if (game.phase === "results") {
    overlay.classList.remove("hidden");
    overlayEyebrow.textContent = game.endReason === "won" ? "Network alive" : "City stalled";
    overlayTitle.textContent = game.endReason === "won" ? "The swarm found a durable rhythm." : "Congestion overwhelmed the city.";
    overlayBody.textContent = `${game.message} Final score: ${Math.round(game.score)}. Trips delivered: ${game.deliveredTrips}.`;
    overlayButton.textContent = "Play again";
  } else {
    overlay.classList.add("hidden");
  }
}

function showResult(outcome) {
  game.message = outcome.message;
  toast.textContent = outcome.message;
  toast.classList.toggle("bad", !outcome.ok);
  toast.classList.add("visible");
  toastTimer = 2.4;
}

function pauseForVisibility() {
  if (game.phase === "playing") {
    togglePause(game);
    syncUi();
  }
}

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  canvas.width = Math.max(1, Math.round(rect.width * dpr));
  canvas.height = Math.max(1, Math.round(rect.height * dpr));
}

function eventToWorld(event) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: ((event.clientX - rect.left) / rect.width) * WORLD.width,
    y: ((event.clientY - rect.top) / rect.height) * WORLD.height
  };
}

function roundRect(x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + width, y, x + width, y + height, r);
  ctx.arcTo(x + width, y + height, x, y + height, r);
  ctx.arcTo(x, y + height, x, y, r);
  ctx.arcTo(x, y, x + width, y, r);
  ctx.closePath();
}

function withAlpha(hex, alpha) {
  const value = hex.replace("#", "");
  const r = parseInt(value.slice(0, 2), 16);
  const g = parseInt(value.slice(2, 4), 16);
  const b = parseInt(value.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
