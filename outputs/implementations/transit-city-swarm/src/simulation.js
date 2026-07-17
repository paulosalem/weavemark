export const WORLD_WIDTH = 960;
export const WORLD_HEIGHT = 640;
export const TRAIL_COLS = 64;
export const TRAIL_ROWS = 42;

const CELL_WIDTH = WORLD_WIDTH / TRAIL_COLS;
const CELL_HEIGHT = WORLD_HEIGHT / TRAIL_ROWS;
const DEFAULT_SEED = 1427;
const MAX_AGENTS = 280;

const DISTRICT_TEMPLATES = [
  { id: "forge", name: "Forge Market", x: 164, y: 142, tint: "#f97373", role: "commercial" },
  { id: "canopy", name: "Canopy Flats", x: 426, y: 104, tint: "#74d680", role: "residential" },
  { id: "quay", name: "Glass Quay", x: 764, y: 160, tint: "#56c4ff", role: "waterfront" },
  { id: "loam", name: "Loam Yards", x: 196, y: 450, tint: "#d9a55c", role: "industrial" },
  { id: "spire", name: "Spire Garden", x: 520, y: 356, tint: "#b78cff", role: "civic" },
  { id: "arc", name: "Arc Residences", x: 792, y: 486, tint: "#f4d35e", role: "residential" }
];

const BUILDING_TYPES = [
  { type: "home", color: "#dbeafe", minPop: 7, maxPop: 26, maxScale: 1.35 },
  { type: "workshop", color: "#fef3c7", minPop: 5, maxPop: 22, maxScale: 1.18 },
  { type: "market", color: "#fecdd3", minPop: 6, maxPop: 24, maxScale: 1.25 },
  { type: "civic", color: "#ddd6fe", minPop: 4, maxPop: 18, maxScale: 1.15 }
];

export function createGameState(seed = DEFAULT_SEED) {
  const state = {
    version: 1,
    startSeed: seed >>> 0,
    seed: seed >>> 0,
    nextId: 1,
    status: "menu",
    mode: "build",
    speed: 1,
    time: 0,
    duration: 300,
    score: 0,
    budget: 260,
    reliability: 82,
    population: 0,
    served: 0,
    missed: 0,
    demand: 0,
    frame: 0,
    pendingStationId: null,
    selectedStationId: null,
    hover: null,
    message: "Start a round, then click the city to sketch a living transit line.",
    messageTone: "hint",
    messageTimer: 10,
    result: null,
    spawnAccumulator: 0,
    growthAccumulator: 0,
    economyAccumulator: 0,
    map: { width: WORLD_WIDTH, height: WORLD_HEIGHT },
    districts: DISTRICT_TEMPLATES.map((district) => ({ ...district })),
    roads: createRoads(),
    buildings: [],
    stations: [],
    lines: [
      {
        id: "aurora-line",
        name: "Aurora Line",
        color: "#36d7ff",
        stationIds: [],
        capacity: 10,
        level: 1
      }
    ],
    agents: [],
    trail: new Float32Array(TRAIL_COLS * TRAIL_ROWS),
    congestion: new Float32Array(TRAIL_COLS * TRAIL_ROWS)
  };

  state.buildings = createBuildings(state);
  state.population = Math.round(sum(state.buildings, (building) => building.population));
  return state;
}

export function beginRound(previousState) {
  const seed = previousState?.startSeed ?? DEFAULT_SEED;
  const state = createGameState(seed);
  state.status = "playing";
  setMessage(state, "Round started. Click to place stops; each corridor changes where the city grows.", "success", 4.5);
  return state;
}

export function restartRound(previousState) {
  const seed = previousState?.startSeed ?? DEFAULT_SEED;
  const state = createGameState(seed);
  state.status = "playing";
  setMessage(state, "Fresh city seeded. Draw a clean line where the demand trails glow.", "success", 4);
  return state;
}

export function pauseGame(state) {
  if (state.status === "playing") {
    state.status = "paused";
    setMessage(state, "Paused. Space resumes the swarm.", "hint", 3);
  }
  return state;
}

export function resumeGame(state) {
  if (state.status === "paused") {
    state.status = "playing";
    setMessage(state, "Resumed. Watch the trails reinforce useful corridors.", "hint", 3);
  }
  return state;
}

export function togglePause(state) {
  return state.status === "playing" ? pauseGame(state) : resumeGame(state);
}

export function setMode(state, mode) {
  if (!["build", "select", "upgrade", "erase"].includes(mode)) {
    return { ok: false, reason: "Unknown tool." };
  }
  state.mode = mode;
  const labels = {
    build: "Build tool: click to place connected stops.",
    select: "Inspect tool: click a stop to read load and capacity.",
    upgrade: "Upgrade tool: click a stop to add capacity.",
    erase: "Prune tool: click the last stop to remove the newest segment."
  };
  setMessage(state, labels[mode], "hint", 3);
  return { ok: true };
}

export function setSpeed(state, speed) {
  state.speed = clamp(speed, 1, 4);
  setMessage(state, `Simulation speed set to ${state.speed}x.`, "hint", 2);
}

export function endRound(state, reason = "complete") {
  if (state.status === "results") {
    return state.result;
  }

  const targetScore = 900;
  const won = reason === "win" || (reason !== "loss" && state.score >= targetScore && state.reliability >= 55);
  state.status = "results";
  state.result = {
    outcome: won ? "win" : "loss",
    reason,
    score: Math.round(state.score),
    budget: Math.round(state.budget),
    reliability: Math.round(state.reliability),
    population: Math.round(state.population),
    served: state.served,
    missed: state.missed
  };
  setMessage(
    state,
    won
      ? "Shift complete: the city accepted your living network."
      : "Shift complete: the swarm outgrew the network. Restart and reroute.",
    won ? "success" : "warning",
    8
  );
  return state.result;
}

export function attemptPlaceStation(state, rawX, rawY) {
  if (state.status !== "playing") {
    return fail(state, "Start or resume the round before building.");
  }

  const point = snapToTransitGrid(rawX, rawY);
  if (!isBuildable(point.x, point.y)) {
    return fail(state, "Stops must stay inside the city service boundary.");
  }

  const tooClose = findStationAt(state, point.x, point.y, 38);
  if (tooClose) {
    return fail(state, "Stops need breathing room. Use upgrade or inspect this stop instead.");
  }

  const line = state.lines[0];
  const previous = line.stationIds.length > 0 ? getStation(state, line.stationIds[line.stationIds.length - 1]) : null;
  let segmentCost = 0;

  if (previous) {
    const length = distance(previous, point);
    if (length < 55) {
      return fail(state, "Segment is too short to read clearly.");
    }
    if (length > 315) {
      return fail(state, "Segment is too long for first-build signal control.");
    }
    segmentCost = Math.round(length / 14);
  }

  const cost = 24 + segmentCost;
  if (state.budget < cost) {
    return fail(state, `Need ${cost} budget for that stop and segment.`);
  }

  const station = {
    id: nextId(state, "stop"),
    name: makeStationName(state, point),
    x: point.x,
    y: point.y,
    districtId: nearestDistrict(state, point).id,
    level: 1,
    capacity: 18,
    load: 0,
    lifetimeBoardings: 0,
    createdAt: state.time
  };

  state.stations.push(station);
  line.stationIds.push(station.id);
  state.pendingStationId = station.id;
  state.selectedStationId = station.id;
  state.budget -= cost;
  state.score += previous ? 8 : 4;
  reinforceCorridor(state, previous, station, previous ? 0.34 : 0.22);
  setMessage(
    state,
    previous
      ? `${station.name} connected for ${cost} budget. Watch whether the swarm reinforces it.`
      : `${station.name} opened for ${cost} budget. Extend toward bright trails.`,
    "success",
    4
  );
  return { ok: true, station, cost };
}

export function upgradeStation(state, stationId) {
  if (state.status !== "playing") {
    return fail(state, "Resume the round before upgrading.");
  }
  const station = getStation(state, stationId);
  if (!station) {
    return fail(state, "No stop selected.");
  }
  if (station.level >= 3) {
    return fail(state, "This stop is already at maximum first-build capacity.");
  }
  const cost = station.level * 42;
  if (state.budget < cost) {
    return fail(state, `Need ${cost} budget to upgrade ${station.name}.`);
  }

  station.level += 1;
  station.capacity += 18;
  const line = state.lines[0];
  line.level = Math.max(line.level, station.level);
  line.capacity += 6;
  state.budget -= cost;
  state.score += 18;
  state.selectedStationId = station.id;
  reinforceCorridor(state, null, station, 0.48);
  setMessage(state, `${station.name} upgraded to level ${station.level}. Capacity and reliability improved.`, "success", 4);
  return { ok: true, station, cost };
}

export function eraseLastStation(state) {
  if (state.status !== "playing") {
    return fail(state, "Resume the round before pruning.");
  }
  const line = state.lines[0];
  if (line.stationIds.length === 0) {
    return fail(state, "No stops to prune yet.");
  }

  const removedId = line.stationIds.pop();
  const removed = getStation(state, removedId);
  state.stations = state.stations.filter((station) => station.id !== removedId);
  state.pendingStationId = line.stationIds[line.stationIds.length - 1] ?? null;
  state.selectedStationId = state.pendingStationId;
  state.budget += 10;
  setMessage(state, `${removed?.name ?? "Last stop"} pruned. A small salvage refund was returned.`, "warning", 4);
  return { ok: true, station: removed };
}

export function findStationAt(state, x, y, radius = 24) {
  return state.stations.find((station) => distance(station, { x, y }) <= radius) ?? null;
}

export function getStation(state, stationId) {
  return state.stations.find((station) => station.id === stationId) ?? null;
}

export function getLineStations(state, line = state.lines[0]) {
  return line.stationIds.map((id) => getStation(state, id)).filter(Boolean);
}

export function readField(field, x, y) {
  const col = clamp(Math.floor(x / CELL_WIDTH), 0, TRAIL_COLS - 1);
  const row = clamp(Math.floor(y / CELL_HEIGHT), 0, TRAIL_ROWS - 1);
  return field[row * TRAIL_COLS + col];
}

export function fieldIndexToWorld(index) {
  const col = index % TRAIL_COLS;
  const row = Math.floor(index / TRAIL_COLS);
  return {
    x: col * CELL_WIDTH,
    y: row * CELL_HEIGHT,
    width: CELL_WIDTH,
    height: CELL_HEIGHT
  };
}

export function updateGame(state, rawDeltaSeconds) {
  const realDelta = clamp(rawDeltaSeconds, 0, 0.08);
  if (state.messageTimer > 0) {
    state.messageTimer = Math.max(0, state.messageTimer - realDelta);
  }

  if (state.status !== "playing") {
    return state;
  }

  const dt = realDelta * state.speed;
  state.frame += 1;
  state.time += dt;

  decayTrail(state, Math.pow(0.987, dt * 60));
  state.congestion.fill(0);
  for (const station of state.stations) {
    station.load = 0;
  }

  state.spawnAccumulator += dt * demandRate(state);
  while (state.spawnAccumulator >= 1 && state.agents.length < MAX_AGENTS) {
    spawnAgent(state);
    state.spawnAccumulator -= 1;
  }

  moveAgents(state, dt);
  growCity(state, dt);
  settleEconomy(state, dt);
  updateReliability(state);

  if (state.budget < -80 && state.time > 40) {
    endRound(state, "loss");
  } else if (state.score >= 1250 && state.population >= 470 && state.reliability >= 64) {
    endRound(state, "win");
  } else if (state.time >= state.duration) {
    endRound(state, "complete");
  }

  return state;
}

export function getAccessibilityAt(state, x, y) {
  if (state.stations.length === 0) {
    return 0;
  }
  let best = 0;
  for (const station of state.stations) {
    const reach = 150 + station.level * 14;
    const d = distance(station, { x, y });
    if (d < reach) {
      best = Math.max(best, (1 - d / reach) * (0.72 + station.level * 0.16));
    }
  }
  return clamp(best, 0, 1.25);
}

export function getSnapshot(state) {
  return {
    status: state.status,
    mode: state.mode,
    speed: state.speed,
    time: state.time,
    timeRemaining: Math.max(0, state.duration - state.time),
    score: Math.round(state.score),
    budget: Math.round(state.budget),
    reliability: Math.round(state.reliability),
    population: Math.round(state.population),
    served: state.served,
    missed: state.missed,
    demand: Math.round(state.demand),
    stops: state.stations.length,
    agents: state.agents.length,
    selectedStation: getStation(state, state.selectedStationId),
    lineStations: getLineStations(state)
  };
}

function createRoads() {
  const roads = [];
  for (const x of [96, 188, 292, 398, 504, 612, 718, 824]) {
    roads.push({ id: `v-${x}`, x1: x, y1: 58, x2: x + (x % 3) * 6, y2: 588, kind: "avenue" });
  }
  for (const y of [82, 156, 244, 330, 416, 516, 578]) {
    roads.push({ id: `h-${y}`, x1: 64, y1: y, x2: 896, y2: y + (y % 4) * 4, kind: "street" });
  }
  roads.push({ id: "diagonal-west", x1: 112, y1: 516, x2: 520, y2: 126, kind: "greenway" });
  roads.push({ id: "diagonal-east", x1: 438, y1: 566, x2: 854, y2: 162, kind: "greenway" });
  return roads;
}

function createBuildings(state) {
  const buildings = [];
  for (const district of state.districts) {
    const count = district.role === "residential" ? 8 : 6;
    for (let i = 0; i < count; i += 1) {
      const template = BUILDING_TYPES[Math.floor(rand(state) * BUILDING_TYPES.length)];
      const angle = rand(state) * Math.PI * 2;
      const radius = 28 + rand(state) * 92;
      const width = 16 + rand(state) * 24;
      const height = 14 + rand(state) * 30;
      const x = clamp(district.x + Math.cos(angle) * radius, 52, WORLD_WIDTH - 72);
      const y = clamp(district.y + Math.sin(angle) * radius, 54, WORLD_HEIGHT - 70);
      const maxPopulation = Math.round(template.maxPop * (1.1 + rand(state) * template.maxScale));
      const population = Math.round(template.minPop + rand(state) * (template.maxPop - template.minPop));
      buildings.push({
        id: nextId(state, "building"),
        districtId: district.id,
        type: template.type,
        color: template.color,
        x,
        y,
        width,
        height,
        population,
        maxPopulation,
        growth: 0,
        pressure: 0.25 + rand(state) * 0.5
      });
    }
  }
  return buildings;
}

function demandRate(state) {
  const populationPressure = clamp(state.population / 135, 0.8, 5.5);
  const timePressure = 1 + Math.sin(state.time / 18) * 0.18 + state.time / state.duration * 0.55;
  const underservedPressure = clamp((state.missed - state.served * 0.35) / 80, 0, 1.2);
  return (0.72 + populationPressure * 0.42 + underservedPressure) * timePressure;
}

function spawnAgent(state) {
  const origin = chooseBuilding(state);
  let destination = chooseBuilding(state);
  let guard = 0;
  while (destination.districtId === origin.districtId && guard < 8) {
    destination = chooseBuilding(state);
    guard += 1;
  }

  const route = createAgentRoute(state, origin, destination);
  state.agents.push({
    id: nextId(state, "agent"),
    x: origin.x,
    y: origin.y,
    originId: origin.id,
    destinationId: destination.id,
    targetIndex: 0,
    path: route.path,
    usedTransit: route.usedTransit,
    age: 0,
    expected: route.expected,
    patience: 18 + rand(state) * 34,
    hue: route.usedTransit ? 190 + rand(state) * 42 : 26 + rand(state) * 24
  });
}

function createAgentRoute(state, origin, destination) {
  const originPoint = buildingCenter(origin);
  const destinationPoint = buildingCenter(destination);
  const lineStations = getLineStations(state);

  if (lineStations.length >= 2) {
    const originStation = nearestStation(state, originPoint, 154);
    const destinationStation = nearestStation(state, destinationPoint, 154);
    if (originStation && destinationStation && originStation.id !== destinationStation.id) {
      const originIndex = lineStations.findIndex((station) => station.id === originStation.id);
      const destinationIndex = lineStations.findIndex((station) => station.id === destinationStation.id);
      const access = getAccessibilityAt(state, originPoint.x, originPoint.y) + getAccessibilityAt(state, destinationPoint.x, destinationPoint.y);
      const directCongestion = readField(state.trail, (originPoint.x + destinationPoint.x) / 2, (originPoint.y + destinationPoint.y) / 2);
      const transitDesire = clamp(0.23 + access * 0.28 + directCongestion * 0.035, 0.18, 0.86);
      if (originIndex >= 0 && destinationIndex >= 0 && rand(state) < transitDesire) {
        const step = originIndex < destinationIndex ? 1 : -1;
        const path = [{ x: originStation.x, y: originStation.y, mode: "walk" }];
        for (let index = originIndex + step; step > 0 ? index <= destinationIndex : index >= destinationIndex; index += step) {
          const station = lineStations[index];
          path.push({ x: station.x, y: station.y, mode: "transit", stationId: station.id });
        }
        path.push({ x: destinationPoint.x, y: destinationPoint.y, mode: "walk" });
        return {
          usedTransit: true,
          path,
          expected: routeLength([{ x: originPoint.x, y: originPoint.y }, ...path]) / 125
        };
      }
    }
  }

  return {
    usedTransit: false,
    path: [{ x: destinationPoint.x, y: destinationPoint.y, mode: "walk" }],
    expected: distance(originPoint, destinationPoint) / 52
  };
}

function moveAgents(state, dt) {
  const active = [];
  for (const agent of state.agents) {
    agent.age += dt;
    const target = agent.path[agent.targetIndex];
    if (!target) {
      completeTrip(state, agent);
      continue;
    }

    const currentCongestion = readField(state.congestion, agent.x, agent.y);
    const fieldPressure = readField(state.trail, agent.x, agent.y);
    const transitLeg = target.mode === "transit";
    const baseSpeed = transitLeg ? 142 : agent.usedTransit ? 76 : 56;
    const slowDown = clamp(1 - currentCongestion * 0.032, 0.48, 1);
    const speed = baseSpeed * slowDown;
    const dx = target.x - agent.x;
    const dy = target.y - agent.y;
    const length = Math.hypot(dx, dy);
    const step = speed * dt;

    depositField(state.congestion, agent.x, agent.y, transitLeg ? 0.52 : 0.88);
    depositField(state.trail, agent.x, agent.y, transitLeg ? 0.045 : 0.085 + fieldPressure * 0.002);
    updateNearbyStationLoad(state, agent, transitLeg);

    if (length <= step || length < 0.01) {
      agent.x = target.x;
      agent.y = target.y;
      agent.targetIndex += 1;
      if (target.stationId) {
        const station = getStation(state, target.stationId);
        if (station) {
          station.lifetimeBoardings += 1;
        }
      }
    } else {
      const avoid = transitLeg ? 0 : clamp(fieldPressure / 80, 0, 0.34);
      const nx = dx / length;
      const ny = dy / length;
      agent.x += (nx - ny * avoid) * step;
      agent.y += (ny + nx * avoid) * step;
    }

    active.push(agent);
  }
  state.agents = active;
}

function updateNearbyStationLoad(state, agent, transitLeg) {
  if (!agent.usedTransit) {
    return;
  }
  for (const station of state.stations) {
    const d = distance(agent, station);
    if (d < 32) {
      station.load += transitLeg ? 0.42 : 0.22;
    }
  }
}

function completeTrip(state, agent) {
  const destination = state.buildings.find((building) => building.id === agent.destinationId);
  const lateness = agent.age > agent.expected * 1.8 || agent.age > agent.patience;

  if (agent.usedTransit) {
    state.served += 1;
    state.budget += lateness ? 1.2 : 2.8;
    state.score += lateness ? 8 : 15;
    if (destination) {
      destination.pressure = clamp(destination.pressure + 0.04, 0, 1.4);
    }
  } else {
    state.missed += 1;
    state.budget -= lateness ? 0.7 : 0.28;
    state.score += 1.5;
    if (destination) {
      destination.pressure = clamp(destination.pressure + 0.08, 0, 1.6);
    }
  }
}

function growCity(state, dt) {
  state.growthAccumulator += dt;
  if (state.growthAccumulator < 0.5) {
    return;
  }

  const tick = state.growthAccumulator;
  state.growthAccumulator = 0;
  let population = 0;
  let demand = 0;

  for (const building of state.buildings) {
    const center = buildingCenter(building);
    const access = getAccessibilityAt(state, center.x, center.y);
    const trail = readField(state.trail, center.x, center.y);
    const congestion = readField(state.congestion, center.x, center.y);
    const headroom = clamp((building.maxPopulation - building.population) / building.maxPopulation, 0, 1);
    const growthSignal = (access * 0.82 + trail * 0.012 + building.pressure * 0.18 - congestion * 0.06 - 0.06) * headroom;
    const delta = growthSignal * tick * (building.type === "home" ? 1.14 : 0.92);
    building.population = clamp(building.population + delta, 1, building.maxPopulation);
    building.growth = delta / Math.max(tick, 0.001);
    building.pressure = clamp(building.pressure * 0.994 + trail * 0.0009 + (access > 0 ? 0.002 : -0.001), 0.05, 1.7);
    population += building.population;
    demand += trail + building.pressure * 10;
  }

  state.population = population;
  state.demand = demand;
}

function settleEconomy(state, dt) {
  state.economyAccumulator += dt;
  if (state.economyAccumulator < 1) {
    return;
  }

  const tick = state.economyAccumulator;
  state.economyAccumulator = 0;
  const line = state.lines[0];
  const maintenance = (state.stations.length * 0.34 + Math.max(0, line.stationIds.length - 1) * 0.16) * tick;
  const populationTax = state.population * 0.0038 * tick;
  const congestionTax = averageField(state.congestion) * 0.82 * tick;
  state.budget += populationTax - maintenance - congestionTax;
  state.score += Math.max(0, state.reliability - 50) * 0.018 * tick + state.stations.length * 0.05 * tick;
}

function updateReliability(state) {
  const totalTrips = state.served + state.missed;
  const serviceRatio = totalTrips === 0 ? 0.34 : state.served / totalTrips;
  const stationLoadPenalty = state.stations.reduce((penalty, station) => {
    const overload = Math.max(0, station.load - station.capacity);
    return penalty + overload * 0.16;
  }, 0);
  const congestionPenalty = Math.min(30, averageField(state.congestion) * 5.5);
  const budgetPenalty = Math.max(0, -state.budget) * 0.16;
  const coverageBonus = clamp(state.stations.length * 2.2, 0, 12);
  state.reliability = clamp(46 + serviceRatio * 42 + coverageBonus - congestionPenalty - stationLoadPenalty - budgetPenalty, 0, 100);
}

function chooseBuilding(state) {
  const total = state.buildings.reduce((acc, building) => acc + building.population + building.pressure * 12, 0);
  let cursor = rand(state) * total;
  for (const building of state.buildings) {
    cursor -= building.population + building.pressure * 12;
    if (cursor <= 0) {
      return building;
    }
  }
  return state.buildings[state.buildings.length - 1];
}

function nearestStation(state, point, radius) {
  let best = null;
  let bestDistance = radius;
  for (const station of state.stations) {
    const d = distance(station, point);
    if (d < bestDistance) {
      best = station;
      bestDistance = d;
    }
  }
  return best;
}

function nearestDistrict(state, point) {
  let best = state.districts[0];
  let bestDistance = Infinity;
  for (const district of state.districts) {
    const d = distance(district, point);
    if (d < bestDistance) {
      best = district;
      bestDistance = d;
    }
  }
  return best;
}

function makeStationName(state, point) {
  const district = nearestDistrict(state, point);
  const suffixes = ["Gate", "Loop", "Exchange", "Hollow", "Link", "Terrace", "Pulse"];
  const suffix = suffixes[Math.floor(rand(state) * suffixes.length)];
  const districtStops = state.stations.filter((station) => station.districtId === district.id).length + 1;
  return `${district.name} ${suffix} ${districtStops}`;
}

function reinforceCorridor(state, from, to, amount) {
  if (!to) {
    return;
  }
  if (!from) {
    depositField(state.trail, to.x, to.y, amount * 8);
    return;
  }
  const steps = Math.max(4, Math.ceil(distance(from, to) / 18));
  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps;
    depositField(
      state.trail,
      from.x + (to.x - from.x) * t,
      from.y + (to.y - from.y) * t,
      amount
    );
  }
}

function snapToTransitGrid(x, y) {
  return {
    x: clamp(Math.round(x / 16) * 16, 32, WORLD_WIDTH - 32),
    y: clamp(Math.round(y / 16) * 16, 32, WORLD_HEIGHT - 32)
  };
}

function isBuildable(x, y) {
  return x >= 42 && x <= WORLD_WIDTH - 42 && y >= 42 && y <= WORLD_HEIGHT - 42;
}

function depositField(field, x, y, amount) {
  const col = clamp(Math.floor(x / CELL_WIDTH), 0, TRAIL_COLS - 1);
  const row = clamp(Math.floor(y / CELL_HEIGHT), 0, TRAIL_ROWS - 1);
  const index = row * TRAIL_COLS + col;
  field[index] = clamp(field[index] + amount, 0, 120);
}

function decayTrail(state, factor) {
  for (let i = 0; i < state.trail.length; i += 1) {
    state.trail[i] *= factor;
    if (state.trail[i] < 0.002) {
      state.trail[i] = 0;
    }
  }
}

function averageField(field) {
  let total = 0;
  for (let i = 0; i < field.length; i += 1) {
    total += field[i];
  }
  return total / field.length;
}

function routeLength(points) {
  let total = 0;
  for (let i = 1; i < points.length; i += 1) {
    total += distance(points[i - 1], points[i]);
  }
  return total;
}

function buildingCenter(building) {
  return {
    x: building.x + building.width / 2,
    y: building.y + building.height / 2
  };
}

function nextId(state, prefix) {
  const id = `${prefix}-${state.nextId}`;
  state.nextId += 1;
  return id;
}

function fail(state, reason) {
  setMessage(state, reason, "warning", 3.5);
  return { ok: false, reason };
}

function setMessage(state, message, tone = "hint", seconds = 3) {
  state.message = message;
  state.messageTone = tone;
  state.messageTimer = seconds;
}

function rand(state) {
  state.seed = (state.seed + 0x6d2b79f5) | 0;
  let t = state.seed;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function sum(items, selector) {
  return items.reduce((total, item) => total + selector(item), 0);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}
