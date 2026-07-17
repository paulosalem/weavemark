export const WORLD = Object.freeze({
  width: 960,
  height: 600,
  cellSize: 24,
  cols: 40,
  rows: 25,
  roundLength: 210,
  scoreTarget: 1400,
  maxAgents: 220
});

export const COSTS = Object.freeze({
  firstStation: 48,
  station: 58,
  segmentPerPixel: 0.12,
  stationUpgrade: 86,
  segmentUpgrade: 72,
  prune: 12
});

export const DISTRICTS = Object.freeze([
  { id: "north-homes", name: "Northfold", type: "residential", x: 70, y: 55, w: 270, h: 170, color: "#78d6a5" },
  { id: "west-homes", name: "Lumen Row", type: "residential", x: 55, y: 315, w: 245, h: 200, color: "#66cfa4" },
  { id: "center-commerce", name: "Civic Core", type: "commercial", x: 365, y: 190, w: 245, h: 205, color: "#7cc4ff" },
  { id: "east-campus", name: "Glass Campus", type: "commercial", x: 660, y: 70, w: 235, h: 185, color: "#9bb8ff" },
  { id: "south-yards", name: "South Yards", type: "industrial", x: 620, y: 365, w: 260, h: 170, color: "#f6bd60" }
]);

export const BLOCKERS = Object.freeze([
  { id: "river", name: "Quiet Canal", x: 452, y: 0, w: 42, h: 165, color: "#123f63" },
  { id: "river-b", name: "Quiet Canal", x: 452, y: 435, w: 42, h: 165, color: "#123f63" },
  { id: "garden", name: "Civic Garden", x: 430, y: 255, w: 92, h: 75, color: "#174934" }
]);

const BUILDING_COUNTS = Object.freeze({
  residential: 14,
  commercial: 11,
  industrial: 10
});

export function createGame(seed = 20260709) {
  const random = makeRng(seed);
  const buildings = createBuildings(random);
  const game = {
    seed,
    random,
    phase: "menu",
    speed: 1,
    time: 0,
    score: 0,
    budget: 420,
    reliability: 1,
    populationPressure: 0.25,
    deliveredTrips: 0,
    missedTrips: 0,
    selectedStationId: null,
    mode: "build",
    nextStationId: 1,
    nextSegmentId: 1,
    nextAgentId: 1,
    spawnTimer: 0,
    growthTimer: 0,
    message: "Start a round to watch the first citizens reveal demand.",
    endReason: "",
    buildings,
    stations: [],
    segments: [],
    agents: [],
    trails: new Float32Array(WORLD.cols * WORLD.rows),
    congestion: new Float32Array(WORLD.cols * WORLD.rows),
    growthGlow: new Float32Array(WORLD.cols * WORLD.rows),
    population: 0,
    jobs: 0
  };
  recalculateCityTotals(game);
  return game;
}

export function startRun(game) {
  if (game.phase === "results") {
    return createGame(game.seed);
  }
  game.phase = "playing";
  game.message = "Swarm demand is waking up. Build along the brightest desire trails.";
  return game;
}

export function togglePause(game) {
  if (game.phase === "playing") {
    game.phase = "paused";
    game.message = "Paused. Planning tools still work while the city waits.";
  } else if (game.phase === "paused") {
    game.phase = "playing";
    game.message = "Resumed. Watch for red overload before extending again.";
  }
}

export function setMode(game, mode) {
  if (!["build", "upgrade", "delete"].includes(mode)) {
    return { ok: false, message: "Unknown planning mode." };
  }
  game.mode = mode;
  game.message = mode === "build"
    ? "Build mode: click empty land to add a stop, or click an existing stop to extend from it."
    : mode === "upgrade"
      ? "Upgrade mode: click a station or segment with red load."
      : "Prune mode: click a weak segment or station to remove it.";
  return { ok: true, message: game.message };
}

export function setSpeed(game, speed) {
  const next = Number(speed);
  game.speed = [1, 2, 4].includes(next) ? next : 1;
}

export function tryBuildStation(game, x, y) {
  if (!isPlanningAllowed(game)) {
    return result(false, "Start or restart the round before planning.");
  }

  const existing = findStationAt(game, x, y, 22);
  if (existing) {
    game.selectedStationId = existing.id;
    return result(true, `${existing.name} selected. Click clear land to extend the line.`);
  }

  const validation = validateStationPlacement(game, x, y);
  if (!validation.ok) {
    game.message = validation.message;
    return validation;
  }

  const selected = game.stations.find((station) => station.id === game.selectedStationId);
  const distance = selected ? dist(selected, { x, y }) : 0;
  const cost = game.stations.length === 0
    ? COSTS.firstStation
    : Math.round(COSTS.station + distance * COSTS.segmentPerPixel);

  if (game.budget < cost) {
    return result(false, `Need $${cost} to build this extension. Earn more trips or prune.`);
  }

  if (selected) {
    const segmentValidation = validateSegmentPlacement(game, selected, { x, y });
    if (!segmentValidation.ok) {
      game.message = segmentValidation.message;
      return segmentValidation;
    }
  } else if (game.stations.length > 0) {
    return result(false, "Select an existing station before starting another branch.");
  }

  const station = {
    id: game.nextStationId++,
    name: `Node ${game.nextStationId - 1}`,
    x,
    y,
    level: 1,
    capacity: 24,
    load: 0,
    pulse: 0
  };
  game.stations.push(station);

  if (selected) {
    game.segments.push({
      id: game.nextSegmentId++,
      from: selected.id,
      to: station.id,
      level: 1,
      load: 0,
      capacity: 30
    });
  }

  game.budget -= cost;
  game.selectedStationId = station.id;
  game.message = selected
    ? `Extended the line to ${station.name} for $${cost}.`
    : `${station.name} opened. Click another clear point to draw the first segment.`;
  return result(true, game.message);
}

export function tryUpgradeAt(game, x, y) {
  if (!isPlanningAllowed(game)) {
    return result(false, "Start or restart the round before upgrading.");
  }
  const station = findStationAt(game, x, y, 26);
  if (station) {
    if (station.level >= 3) {
      return result(false, `${station.name} is already at maximum capacity.`);
    }
    if (game.budget < COSTS.stationUpgrade) {
      return result(false, `Need $${COSTS.stationUpgrade} to upgrade a station.`);
    }
    station.level += 1;
    station.capacity += 18;
    game.budget -= COSTS.stationUpgrade;
    station.pulse = 1;
    game.message = `${station.name} upgraded to level ${station.level}.`;
    return result(true, game.message);
  }

  const segment = findSegmentAt(game, x, y, 15);
  if (segment) {
    if (segment.level >= 3) {
      return result(false, "This segment is already at maximum capacity.");
    }
    if (game.budget < COSTS.segmentUpgrade) {
      return result(false, `Need $${COSTS.segmentUpgrade} to upgrade a segment.`);
    }
    segment.level += 1;
    segment.capacity += 22;
    game.budget -= COSTS.segmentUpgrade;
    game.message = `Segment upgraded to level ${segment.level}.`;
    return result(true, game.message);
  }

  return result(false, "Click a station or blue segment to upgrade it.");
}

export function tryDeleteAt(game, x, y) {
  if (!isPlanningAllowed(game)) {
    return result(false, "Start or restart the round before pruning.");
  }
  const station = findStationAt(game, x, y, 24);
  if (station) {
    game.stations = game.stations.filter((candidate) => candidate.id !== station.id);
    game.segments = game.segments.filter((segment) => segment.from !== station.id && segment.to !== station.id);
    if (game.selectedStationId === station.id) {
      game.selectedStationId = game.stations.at(-1)?.id ?? null;
    }
    game.budget = Math.max(-160, game.budget - COSTS.prune + 18);
    game.message = `${station.name} pruned. Demand will adapt around the gap.`;
    return result(true, game.message);
  }

  const segment = findSegmentAt(game, x, y, 13);
  if (segment) {
    game.segments = game.segments.filter((candidate) => candidate.id !== segment.id);
    game.budget = Math.max(-160, game.budget - COSTS.prune + 10);
    game.message = "Segment pruned. Watch whether the trail evaporates or reroutes.";
    return result(true, game.message);
  }
  return result(false, "Click a station or segment to prune it.");
}

export function stepGame(game, deltaSeconds) {
  if (game.phase !== "playing") {
    return;
  }

  const dt = Math.min(0.18, Math.max(0, deltaSeconds)) * game.speed;
  game.time += dt;
  evaporateFields(game, dt);
  decayLoads(game, dt);

  const spawnInterval = Math.max(0.38, 1.6 - game.population / 1250 - game.populationPressure * 0.45);
  game.spawnTimer += dt;
  while (game.spawnTimer >= spawnInterval && game.agents.length < WORLD.maxAgents) {
    game.spawnTimer -= spawnInterval;
    spawnAgent(game);
  }

  for (const agent of game.agents) {
    updateAgent(game, agent, dt);
  }
  game.agents = game.agents.filter((agent) => !agent.done);

  game.growthTimer += dt;
  if (game.growthTimer >= 3) {
    game.growthTimer = 0;
    applyCityGrowth(game);
  }

  updateMetrics(game);
  evaluateEndState(game);
}

export function getRemainingSeconds(game) {
  return Math.max(0, WORLD.roundLength - game.time);
}

export function getCellIndex(x, y) {
  const col = Math.max(0, Math.min(WORLD.cols - 1, Math.floor(x / WORLD.cellSize)));
  const row = Math.max(0, Math.min(WORLD.rows - 1, Math.floor(y / WORLD.cellSize)));
  return row * WORLD.cols + col;
}

export function getCellCenter(index) {
  const col = index % WORLD.cols;
  const row = Math.floor(index / WORLD.cols);
  return {
    x: col * WORLD.cellSize + WORLD.cellSize / 2,
    y: row * WORLD.cellSize + WORLD.cellSize / 2
  };
}

export function findStationAt(game, x, y, radius = 20) {
  return game.stations.find((station) => dist(station, { x, y }) <= radius) ?? null;
}

export function findSegmentAt(game, x, y, tolerance = 12) {
  let best = null;
  let bestDistance = Infinity;
  for (const segment of game.segments) {
    const from = stationById(game, segment.from);
    const to = stationById(game, segment.to);
    if (!from || !to) {
      continue;
    }
    const distance = pointToSegmentDistance({ x, y }, from, to);
    if (distance < tolerance && distance < bestDistance) {
      best = segment;
      bestDistance = distance;
    }
  }
  return best;
}

export function pointInBlocker(x, y) {
  return BLOCKERS.some((blocker) =>
    x >= blocker.x && x <= blocker.x + blocker.w && y >= blocker.y && y <= blocker.y + blocker.h
  );
}

export function stationById(game, id) {
  return game.stations.find((station) => station.id === id) ?? null;
}

export function formatClock(seconds) {
  const whole = Math.max(0, Math.ceil(seconds));
  const minutes = String(Math.floor(whole / 60)).padStart(2, "0");
  const rest = String(whole % 60).padStart(2, "0");
  return `${minutes}:${rest}`;
}

export function summarize(game) {
  return {
    score: Math.round(game.score),
    budget: Math.round(game.budget),
    reliability: game.reliability,
    populationPressure: game.populationPressure,
    timeRemaining: getRemainingSeconds(game),
    trips: game.deliveredTrips,
    stations: game.stations.length,
    agents: game.agents.length
  };
}

function validateStationPlacement(game, x, y) {
  if (x < 28 || y < 28 || x > WORLD.width - 28 || y > WORLD.height - 28) {
    return result(false, "Stops need a little margin from the city edge.");
  }
  if (pointInBlocker(x, y)) {
    return result(false, "Cannot build inside water or the protected garden.");
  }
  const tooClose = game.stations.find((station) => dist(station, { x, y }) < 38);
  if (tooClose) {
    return result(false, `Too close to ${tooClose.name}. Keep stops readable.`);
  }
  return result(true, "Placement is clear.");
}

function validateSegmentPlacement(game, from, to) {
  const length = dist(from, to);
  if (length < 44) {
    return result(false, "Segments need enough distance to be legible.");
  }
  if (length > 265) {
    return result(false, "Segment is too long. Add an intermediate stop.");
  }
  if (lineCrossesBlocker(from, to)) {
    return result(false, "Segment crosses protected land or water. Bend around it.");
  }
  const duplicate = game.segments.some((segment) =>
    (segment.from === from.id && segment.to === to.id) || (segment.from === to.id && segment.to === from.id)
  );
  if (duplicate) {
    return result(false, "These stops are already connected.");
  }
  return result(true, "Segment is clear.");
}

function isPlanningAllowed(game) {
  return game.phase === "playing" || game.phase === "paused";
}

function spawnAgent(game) {
  const origin = weightedBuilding(game, "residential");
  const destination = weightedDestination(game, origin);
  if (!origin || !destination) {
    return;
  }
  const route = planRoute(game, origin, destination);
  game.agents.push({
    id: game.nextAgentId++,
    x: origin.x,
    y: origin.y,
    originId: origin.id,
    destinationId: destination.id,
    route,
    routeIndex: 0,
    transit: route.some((point) => point.mode === "transit"),
    age: 0,
    done: false
  });
}

function updateAgent(game, agent, dt) {
  agent.age += dt;
  const current = agent.route[agent.routeIndex];
  const target = agent.route[agent.routeIndex + 1];
  if (!target) {
    completeAgent(game, agent);
    return;
  }

  const index = getCellIndex(agent.x, agent.y);
  const congestion = game.congestion[index];
  const baseSpeed = target.mode === "transit" ? 112 : 48;
  const speed = baseSpeed * clamp(1 - congestion * 0.46, 0.34, 1.08);
  const dx = target.x - agent.x;
  const dy = target.y - agent.y;
  const distance = Math.hypot(dx, dy);
  const step = speed * dt;

  reinforceField(game.trails, index, target.mode === "transit" ? 0.012 : 0.026);
  reinforceField(game.congestion, index, target.mode === "transit" ? 0.008 : 0.02);

  if (target.stationId) {
    const station = stationById(game, target.stationId);
    if (station) {
      station.load += dt * (target.mode === "transit" ? 1.9 : 0.6);
      station.pulse = Math.min(1, station.pulse + 0.04);
    }
  }
  if (target.segmentId) {
    const segment = game.segments.find((candidate) => candidate.id === target.segmentId);
    if (segment) {
      segment.load += dt * 1.5;
    }
  }

  if (distance <= step || distance < 0.001) {
    agent.x = target.x;
    agent.y = target.y;
    agent.routeIndex += 1;
    if (!agent.route[agent.routeIndex + 1]) {
      completeAgent(game, agent);
    }
  } else {
    agent.x += (dx / distance) * step;
    agent.y += (dy / distance) * step;
  }

  if (agent.age > 36 && !agent.done) {
    game.missedTrips += 1;
    game.budget -= 2;
    agent.done = true;
  }
}

function completeAgent(game, agent) {
  const reward = agent.transit ? 9 : 3;
  const score = agent.transit ? 18 : 7;
  game.deliveredTrips += 1;
  game.budget += reward;
  game.score += score;
  agent.done = true;
}

function planRoute(game, origin, destination) {
  const start = nearestStation(game, origin, 155);
  const end = nearestStation(game, destination, 165);
  if (start && end && start.id !== end.id) {
    const path = shortestStationPath(game, start.id, end.id);
    if (path.length >= 2) {
      const route = [{ x: origin.x, y: origin.y, mode: "walk" }];
      route.push({ x: start.x, y: start.y, mode: "walk", stationId: start.id });
      for (let i = 1; i < path.length; i += 1) {
        const station = stationById(game, path[i]);
        const previous = stationById(game, path[i - 1]);
        const segment = segmentBetween(game, path[i - 1], path[i]);
        if (station && previous && segment) {
          route.push({
            x: station.x,
            y: station.y,
            mode: "transit",
            stationId: station.id,
            segmentId: segment.id
          });
        }
      }
      route.push({ x: destination.x, y: destination.y, mode: "walk" });
      return route;
    }
  }
  return [
    { x: origin.x, y: origin.y, mode: "walk" },
    { x: destination.x, y: destination.y, mode: "walk" }
  ];
}

function shortestStationPath(game, startId, endId) {
  const distances = new Map([[startId, 0]]);
  const previous = new Map();
  const unvisited = new Set(game.stations.map((station) => station.id));
  while (unvisited.size > 0) {
    let current = null;
    let best = Infinity;
    for (const id of unvisited) {
      const value = distances.get(id) ?? Infinity;
      if (value < best) {
        best = value;
        current = id;
      }
    }
    if (current === null || current === endId) {
      break;
    }
    unvisited.delete(current);
    for (const segment of game.segments) {
      const neighbor = segment.from === current ? segment.to : segment.to === current ? segment.from : null;
      if (neighbor === null || !unvisited.has(neighbor)) {
        continue;
      }
      const from = stationById(game, current);
      const to = stationById(game, neighbor);
      const overload = segment.load / Math.max(1, segment.capacity);
      const candidate = best + dist(from, to) * (1 + overload * 0.6) / Math.max(1, segment.level);
      if (candidate < (distances.get(neighbor) ?? Infinity)) {
        distances.set(neighbor, candidate);
        previous.set(neighbor, current);
      }
    }
  }
  if (!distances.has(endId)) {
    return [];
  }
  const path = [endId];
  while (path[0] !== startId) {
    const prev = previous.get(path[0]);
    if (!prev) {
      return [];
    }
    path.unshift(prev);
  }
  return path;
}

function nearestStation(game, point, radius) {
  let best = null;
  let bestDistance = radius;
  for (const station of game.stations) {
    const distance = dist(station, point);
    const loadPenalty = station.load / Math.max(1, station.capacity);
    if (distance < bestDistance && loadPenalty < 1.45) {
      best = station;
      bestDistance = distance;
    }
  }
  return best;
}

function segmentBetween(game, a, b) {
  return game.segments.find((segment) =>
    (segment.from === a && segment.to === b) || (segment.from === b && segment.to === a)
  ) ?? null;
}

function applyCityGrowth(game) {
  let totalPressure = 0;
  for (const building of game.buildings) {
    const station = nearestStation(game, building, 170);
    const accessibility = station ? clamp(1 - dist(station, building) / 190 + station.level * 0.12, 0, 1) : 0;
    const congestion = game.congestion[getCellIndex(building.x, building.y)];
    const lift = accessibility * 0.56 + game.reliability * 0.22 - congestion * 0.58 + game.random() * 0.18;
    building.accessibility = accessibility;
    building.congestion = congestion;
    building.pressure = clamp(building.pressure + (building.type === "residential" ? 0.015 : 0.01) + 0.08 - lift * 0.04, 0, 1);
    totalPressure += building.pressure;

    if (lift > 0.47 && building.level < 5) {
      building.level += 1;
      const glowIndex = getCellIndex(building.x, building.y);
      game.growthGlow[glowIndex] = Math.min(1, game.growthGlow[glowIndex] + 0.8);
      if (building.type === "residential") {
        building.population += 7 + building.level * 3;
      } else {
        building.jobs += 6 + building.level * 2;
      }
      game.score += 8;
      game.budget += 5;
    }

    if (congestion > 0.78) {
      game.budget -= 2;
      building.pressure = clamp(building.pressure + 0.08, 0, 1);
    }
  }
  game.populationPressure = clamp(totalPressure / Math.max(1, game.buildings.length), 0, 1);
  recalculateCityTotals(game);
}

function updateMetrics(game) {
  let occupied = 0;
  let congestionTotal = 0;
  for (const value of game.congestion) {
    if (value > 0.04) {
      occupied += 1;
      congestionTotal += value;
    }
  }
  const congestionScore = occupied === 0 ? 0 : congestionTotal / occupied;
  const stationOverload = game.stations.reduce((sum, station) => {
    return sum + Math.max(0, station.load / Math.max(1, station.capacity) - 1);
  }, 0);
  const segmentOverload = game.segments.reduce((sum, segment) => {
    return sum + Math.max(0, segment.load / Math.max(1, segment.capacity) - 1);
  }, 0);
  const missedPressure = game.missedTrips / Math.max(10, game.deliveredTrips + game.missedTrips);
  game.reliability = clamp(1 - congestionScore * 0.46 - stationOverload * 0.16 - segmentOverload * 0.11 - missedPressure * 0.32, 0, 1);
}

function evaluateEndState(game) {
  if (game.score >= WORLD.scoreTarget) {
    finish(game, "won", "The network matured into a reliable transit organism.");
    return;
  }
  if (game.time >= WORLD.roundLength) {
    if (game.score >= WORLD.scoreTarget * 0.62 && game.reliability >= 0.42) {
      finish(game, "won", "The city endured the growth wave with a working swarm network.");
    } else {
      finish(game, "lost", "The city outgrew the network. Demand hardened into congestion.");
    }
    return;
  }
  if (game.time > 45 && (game.budget < -125 || game.reliability < 0.18)) {
    finish(game, "lost", "Budget and reliability collapsed under congestion pressure.");
  }
}

function finish(game, outcome, message) {
  game.phase = "results";
  game.endReason = outcome;
  game.message = message;
}

function evaporateFields(game, dt) {
  const trailDecay = Math.exp(-dt * 0.14);
  const congestionDecay = Math.exp(-dt * 0.36);
  const glowDecay = Math.exp(-dt * 0.5);
  for (let i = 0; i < game.trails.length; i += 1) {
    game.trails[i] *= trailDecay;
    game.congestion[i] *= congestionDecay;
    game.growthGlow[i] *= glowDecay;
  }
}

function decayLoads(game, dt) {
  const decay = Math.exp(-dt * 0.52);
  for (const station of game.stations) {
    station.load *= decay;
    station.pulse *= Math.exp(-dt * 1.2);
  }
  for (const segment of game.segments) {
    segment.load *= decay;
  }
}

function weightedBuilding(game, type) {
  const candidates = game.buildings.filter((building) => building.type === type);
  return weightedPick(game.random, candidates, (building) =>
    Math.max(1, building.population + building.pressure * 45)
  );
}

function weightedDestination(game, origin) {
  const candidates = game.buildings.filter((building) => building.type !== origin.type);
  return weightedPick(game.random, candidates, (building) =>
    Math.max(1, building.jobs + building.pressure * 35 + dist(origin, building) / 80)
  );
}

function weightedPick(random, candidates, weight) {
  const total = candidates.reduce((sum, item) => sum + weight(item), 0);
  if (total <= 0) {
    return candidates[0] ?? null;
  }
  let cursor = random() * total;
  for (const candidate of candidates) {
    cursor -= weight(candidate);
    if (cursor <= 0) {
      return candidate;
    }
  }
  return candidates.at(-1) ?? null;
}

function createBuildings(random) {
  const buildings = [];
  let id = 1;
  for (const district of DISTRICTS) {
    const count = BUILDING_COUNTS[district.type];
    for (let i = 0; i < count; i += 1) {
      const x = district.x + 22 + random() * (district.w - 44);
      const y = district.y + 22 + random() * (district.h - 44);
      const level = 1 + Math.floor(random() * 2);
      buildings.push({
        id: id++,
        districtId: district.id,
        type: district.type,
        x,
        y,
        level,
        population: district.type === "residential" ? 28 + level * 8 : 0,
        jobs: district.type !== "residential" ? 24 + level * 9 : 0,
        pressure: 0.18 + random() * 0.22,
        accessibility: 0,
        congestion: 0
      });
    }
  }
  return buildings;
}

function recalculateCityTotals(game) {
  game.population = game.buildings.reduce((sum, building) => sum + building.population, 0);
  game.jobs = game.buildings.reduce((sum, building) => sum + building.jobs, 0);
}

function lineCrossesBlocker(a, b) {
  return BLOCKERS.some((blocker) => segmentIntersectsRect(a, b, blocker));
}

function segmentIntersectsRect(a, b, rect) {
  if (pointInsideRect(a, rect) || pointInsideRect(b, rect)) {
    return true;
  }
  const corners = [
    { x: rect.x, y: rect.y },
    { x: rect.x + rect.w, y: rect.y },
    { x: rect.x + rect.w, y: rect.y + rect.h },
    { x: rect.x, y: rect.y + rect.h }
  ];
  for (let i = 0; i < corners.length; i += 1) {
    if (segmentsIntersect(a, b, corners[i], corners[(i + 1) % corners.length])) {
      return true;
    }
  }
  return false;
}

function pointInsideRect(point, rect) {
  return point.x >= rect.x && point.x <= rect.x + rect.w && point.y >= rect.y && point.y <= rect.y + rect.h;
}

function segmentsIntersect(a, b, c, d) {
  const o1 = orientation(a, b, c);
  const o2 = orientation(a, b, d);
  const o3 = orientation(c, d, a);
  const o4 = orientation(c, d, b);
  return o1 !== o2 && o3 !== o4;
}

function orientation(a, b, c) {
  return Math.sign((b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y));
}

function pointToSegmentDistance(point, a, b) {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  if (dx === 0 && dy === 0) {
    return dist(point, a);
  }
  const t = clamp(((point.x - a.x) * dx + (point.y - a.y) * dy) / (dx * dx + dy * dy), 0, 1);
  return dist(point, { x: a.x + dx * t, y: a.y + dy * t });
}

function reinforceField(field, index, amount) {
  field[index] = Math.min(1, field[index] + amount);
}

function makeRng(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state * 1664525 + 1013904223) >>> 0;
    return state / 4294967296;
  };
}

function result(ok, message) {
  return { ok, message };
}

function dist(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}
