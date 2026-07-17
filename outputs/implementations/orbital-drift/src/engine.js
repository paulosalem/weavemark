export const GAME_STATE = Object.freeze({
  READY: "ready",
  PLAYING: "playing",
  PAUSED: "paused",
  FINISHED: "finished",
});

export const PHYSICS = Object.freeze({
  THRUST_ACCELERATION: 430,
  ROTATION_SPEED: 3.25,
  LINEAR_DAMPING: 0.992,
  BRAKE_DAMPING: 0.86,
  MAX_SPEED: 390,
  MAX_GRAVITY_ACCELERATION: 210,
  MAX_DELTA_SECONDS: 0.05,
  COLLISION_RESTITUTION: 0.58,
  COLLISION_PENALTY_SECONDS: 2,
  COLLISION_COOLDOWN_SECONDS: 0.7,
  STUN_SECONDS: 0.16,
});

export const COURSE = Object.freeze({
  width: 1200,
  height: 760,
  requiredLaps: 2,
  startGate: Object.freeze({
    x: 140,
    y: 380,
    radius: 64,
    label: "Start / Finish",
  }),
  checkpoints: Object.freeze([
    Object.freeze({ x: 330, y: 330, radius: 68, label: "Gate 1" }),
    Object.freeze({ x: 555, y: 210, radius: 64, label: "Gate 2" }),
    Object.freeze({ x: 865, y: 270, radius: 66, label: "Gate 3" }),
    Object.freeze({ x: 980, y: 520, radius: 70, label: "Gate 4" }),
    Object.freeze({ x: 620, y: 610, radius: 68, label: "Gate 5" }),
    Object.freeze({ x: 300, y: 520, radius: 64, label: "Gate 6" }),
  ]),
  planets: Object.freeze([
    Object.freeze({
      x: 900,
      y: 120,
      radius: 45,
      label: "Aurelia",
      colors: ["#ffd99c", "#b86d31"],
      gravityRadius: 140,
      gravityStrength: 48,
      collidable: true,
    }),
    Object.freeze({
      x: 205,
      y: 628,
      radius: 52,
      label: "Cerule",
      colors: ["#68e0ff", "#146482"],
      gravityRadius: 0,
      gravityStrength: 0,
      collidable: true,
    }),
    Object.freeze({
      x: 1060,
      y: 650,
      radius: 38,
      label: "Vesper",
      colors: ["#f09bff", "#6731a1"],
      gravityRadius: 115,
      gravityStrength: 36,
      collidable: true,
    }),
  ]),
  asteroids: Object.freeze([
    Object.freeze({ x: 470, y: 350, radius: 19, spin: 0.4 }),
    Object.freeze({ x: 515, y: 410, radius: 16, spin: -0.34 }),
    Object.freeze({ x: 750, y: 315, radius: 22, spin: 0.22 }),
    Object.freeze({ x: 825, y: 448, radius: 18, spin: -0.28 }),
    Object.freeze({ x: 725, y: 560, radius: 21, spin: 0.31 }),
    Object.freeze({ x: 430, y: 580, radius: 17, spin: -0.18 }),
    Object.freeze({ x: 1015, y: 405, radius: 15, spin: 0.26 }),
  ]),
  gravityWells: Object.freeze([
    Object.freeze({
      x: 645,
      y: 405,
      radius: 188,
      strength: 152,
      label: "Blue well",
      color: "#6bb7ff",
    }),
    Object.freeze({
      x: 360,
      y: 190,
      radius: 120,
      strength: 92,
      label: "Violet well",
      color: "#b98cff",
    }),
  ]),
});

const SPAWN = Object.freeze({ x: 78, y: 380, angle: 0 });

export function createInitialGameState(options = {}) {
  const bestTime = Number.isFinite(options.bestTime) ? options.bestTime : null;

  return {
    state: GAME_STATE.READY,
    course: COURSE,
    craft: {
      x: SPAWN.x,
      y: SPAWN.y,
      vx: 0,
      vy: 0,
      angle: SPAWN.angle,
      radius: 14,
      thrusting: false,
      braking: false,
      stun: 0,
      collisionCooldown: 0,
      lastSafeCheckpoint: { x: SPAWN.x, y: SPAWN.y },
    },
    progress: {
      lap: 1,
      nextCheckpoint: 0,
      requiredLaps: COURSE.requiredLaps,
    },
    timer: {
      elapsed: 0,
      final: null,
    },
    bestTime,
    finishRecorded: false,
    message: {
      text: "Press W, Arrow Up, or Enter to start.",
      type: "neutral",
      time: Number.POSITIVE_INFINITY,
    },
    effects: {
      checkpoint: 0,
      lap: 0,
      collision: 0,
      finish: 0,
      gravity: 0,
      gravitySource: null,
    },
  };
}

export function startRace(state) {
  if (state.state === GAME_STATE.READY) {
    state.state = GAME_STATE.PLAYING;
    state.message = timedMessage("Go! The cyan gate is your next target.", "checkpoint");
  } else if (state.state === GAME_STATE.PAUSED) {
    state.state = GAME_STATE.PLAYING;
    state.message = timedMessage("Race resumed.", "neutral", 1.4);
  }

  return state;
}

export function setPaused(state, paused = true) {
  if (paused && state.state === GAME_STATE.PLAYING) {
    state.state = GAME_STATE.PAUSED;
    state.craft.thrusting = false;
    state.craft.braking = false;
    state.message = timedMessage("Paused. Press P, Escape, or Enter to resume.", "neutral", 2.4);
  } else if (!paused && state.state === GAME_STATE.PAUSED) {
    startRace(state);
  }

  return state;
}

export function restartGame(previousState) {
  return createInitialGameState({
    bestTime: previousState?.bestTime ?? null,
  });
}

export function updateGame(state, input = {}, rawDeltaSeconds = 0) {
  const dt = clamp(rawDeltaSeconds, 0, PHYSICS.MAX_DELTA_SECONDS);
  tickTransientState(state, dt);

  if (state.state !== GAME_STATE.PLAYING || dt <= 0) {
    state.craft.thrusting = false;
    state.craft.braking = false;
    return state;
  }

  state.timer.elapsed += dt;

  const craft = state.craft;
  craft.stun = Math.max(0, craft.stun - dt);
  craft.collisionCooldown = Math.max(0, craft.collisionCooldown - dt);

  const turn = (input.right ? 1 : 0) - (input.left ? 1 : 0);
  if (craft.stun <= 0) {
    craft.angle = normalizeAngle(craft.angle + turn * PHYSICS.ROTATION_SPEED * dt);
  }

  craft.thrusting = Boolean(input.thrust) && craft.stun <= 0;
  craft.braking = Boolean(input.brake);

  if (craft.thrusting) {
    craft.vx += Math.cos(craft.angle) * PHYSICS.THRUST_ACCELERATION * dt;
    craft.vy += Math.sin(craft.angle) * PHYSICS.THRUST_ACCELERATION * dt;
  }

  applyGravity(state, dt);

  const damping = Math.pow(PHYSICS.LINEAR_DAMPING, dt * 60);
  craft.vx *= damping;
  craft.vy *= damping;

  if (craft.braking) {
    const brake = Math.pow(PHYSICS.BRAKE_DAMPING, dt * 60);
    craft.vx *= brake;
    craft.vy *= brake;
  }

  limitSpeed(craft, PHYSICS.MAX_SPEED);
  craft.x += craft.vx * dt;
  craft.y += craft.vy * dt;

  resolveBounds(state);
  resolveHazardCollisions(state);
  advanceCourseIfNeeded(state);

  return state;
}

export function getActiveTarget(state) {
  if (state.progress.nextCheckpoint < COURSE.checkpoints.length) {
    const checkpoint = COURSE.checkpoints[state.progress.nextCheckpoint];
    return {
      ...checkpoint,
      type: "checkpoint",
      order: state.progress.nextCheckpoint,
    };
  }

  return {
    ...COURSE.startGate,
    type: "finish",
    order: COURSE.checkpoints.length,
  };
}

export function formatTime(seconds) {
  if (!Number.isFinite(seconds)) {
    return "--:--.-";
  }

  const safeSeconds = Math.max(0, seconds);
  const minutes = Math.floor(safeSeconds / 60);
  const wholeSeconds = Math.floor(safeSeconds % 60);
  const tenths = Math.floor((safeSeconds % 1) * 10);
  return `${String(minutes).padStart(2, "0")}:${String(wholeSeconds).padStart(2, "0")}.${tenths}`;
}

export function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

export function computeGravityAcceleration(point, source) {
  const reach = source.radius ?? source.gravityRadius ?? 0;
  const strength = source.strength ?? source.gravityStrength ?? 0;

  if (reach <= 0 || strength <= 0) {
    return { ax: 0, ay: 0, intensity: 0 };
  }

  const dx = source.x - point.x;
  const dy = source.y - point.y;
  const dist = Math.hypot(dx, dy);

  if (dist <= 0.001 || dist > reach) {
    return { ax: 0, ay: 0, intensity: 0 };
  }

  const falloff = 1 - dist / reach;
  const magnitude = Math.min(PHYSICS.MAX_GRAVITY_ACCELERATION, strength * falloff);

  return {
    ax: (dx / dist) * magnitude,
    ay: (dy / dist) * magnitude,
    intensity: magnitude / PHYSICS.MAX_GRAVITY_ACCELERATION,
  };
}

function applyGravity(state, dt) {
  const craft = state.craft;
  let ax = 0;
  let ay = 0;
  let strongest = { intensity: 0, source: null };
  const sources = [
    ...COURSE.gravityWells,
    ...COURSE.planets
      .filter((planet) => planet.gravityRadius > 0 && planet.gravityStrength > 0)
      .map((planet) => ({
        x: planet.x,
        y: planet.y,
        radius: planet.gravityRadius,
        strength: planet.gravityStrength,
        label: `${planet.label} gravity`,
        color: "#ffd99c",
      })),
  ];

  for (const source of sources) {
    const acceleration = computeGravityAcceleration(craft, source);
    ax += acceleration.ax;
    ay += acceleration.ay;
    if (acceleration.intensity > strongest.intensity) {
      strongest = { intensity: acceleration.intensity, source };
    }
  }

  craft.vx += ax * dt;
  craft.vy += ay * dt;
  state.effects.gravity = strongest.intensity;
  state.effects.gravitySource = strongest.source;
}

function resolveBounds(state) {
  const craft = state.craft;
  const minX = craft.radius;
  const maxX = COURSE.width - craft.radius;
  const minY = craft.radius;
  const maxY = COURSE.height - craft.radius;

  if (craft.x < minX) {
    craft.x = minX;
    applyCollisionResponse(state, { x: 1, y: 0 }, "Boundary hit");
  } else if (craft.x > maxX) {
    craft.x = maxX;
    applyCollisionResponse(state, { x: -1, y: 0 }, "Boundary hit");
  }

  if (craft.y < minY) {
    craft.y = minY;
    applyCollisionResponse(state, { x: 0, y: 1 }, "Boundary hit");
  } else if (craft.y > maxY) {
    craft.y = maxY;
    applyCollisionResponse(state, { x: 0, y: -1 }, "Boundary hit");
  }
}

function resolveHazardCollisions(state) {
  for (const asteroid of COURSE.asteroids) {
    resolveCircleCollision(state, asteroid, "Asteroid strike");
  }

  for (const planet of COURSE.planets) {
    if (planet.collidable) {
      resolveCircleCollision(state, planet, `${planet.label} contact`);
    }
  }
}

function resolveCircleCollision(state, body, label) {
  const craft = state.craft;
  const dx = craft.x - body.x;
  const dy = craft.y - body.y;
  const dist = Math.hypot(dx, dy);
  const minDist = craft.radius + body.radius;

  if (dist >= minDist) {
    return;
  }

  const nx = dist > 0.001 ? dx / dist : Math.cos(craft.angle);
  const ny = dist > 0.001 ? dy / dist : Math.sin(craft.angle);
  const overlap = minDist - dist + 0.4;
  craft.x += nx * overlap;
  craft.y += ny * overlap;
  applyCollisionResponse(state, { x: nx, y: ny }, label);
}

function applyCollisionResponse(state, normal, label) {
  const craft = state.craft;
  const impact = craft.vx * normal.x + craft.vy * normal.y;

  if (impact < 0) {
    craft.vx -= (1 + PHYSICS.COLLISION_RESTITUTION) * impact * normal.x;
    craft.vy -= (1 + PHYSICS.COLLISION_RESTITUTION) * impact * normal.y;
  } else {
    craft.vx += normal.x * 65;
    craft.vy += normal.y * 65;
  }

  limitSpeed(craft, PHYSICS.MAX_SPEED * 0.72);

  if (craft.collisionCooldown <= 0) {
    state.timer.elapsed += PHYSICS.COLLISION_PENALTY_SECONDS;
    craft.collisionCooldown = PHYSICS.COLLISION_COOLDOWN_SECONDS;
    craft.stun = PHYSICS.STUN_SECONDS;
    state.effects.collision = 0.7;
    state.message = timedMessage(
      `${label}: +${PHYSICS.COLLISION_PENALTY_SECONDS}s penalty`,
      "collision",
      1.7,
    );
  }
}

function advanceCourseIfNeeded(state) {
  const target = getActiveTarget(state);

  if (distance(state.craft, target) > target.radius) {
    return;
  }

  if (target.type === "checkpoint") {
    state.craft.lastSafeCheckpoint = { x: target.x, y: target.y };
    state.progress.nextCheckpoint += 1;
    state.effects.checkpoint = 0.85;
    state.message = timedMessage(`${target.label} cleared`, "checkpoint", 1.1);
    return;
  }

  if (state.progress.lap >= state.progress.requiredLaps) {
    state.state = GAME_STATE.FINISHED;
    state.timer.final = state.timer.elapsed;
    state.effects.finish = 1.6;
    state.craft.thrusting = false;
    state.craft.braking = false;
    state.message = {
      text: `Race complete: ${formatTime(state.timer.final)}. Press R to restart.`,
      type: "finish",
      time: Number.POSITIVE_INFINITY,
    };
    return;
  }

  state.progress.lap += 1;
  state.progress.nextCheckpoint = 0;
  state.effects.lap = 1.2;
  state.message = timedMessage(`Lap ${state.progress.lap} started`, "lap", 1.5);
}

function tickTransientState(state, dt) {
  const effects = state.effects;
  effects.checkpoint = Math.max(0, effects.checkpoint - dt);
  effects.lap = Math.max(0, effects.lap - dt);
  effects.collision = Math.max(0, effects.collision - dt);
  effects.finish = Math.max(0, effects.finish - dt);

  if (Number.isFinite(state.message.time)) {
    state.message.time = Math.max(0, state.message.time - dt);
  }
}

function timedMessage(text, type = "neutral", time = 1.35) {
  return { text, type, time };
}

function limitSpeed(craft, maxSpeed) {
  const speed = Math.hypot(craft.vx, craft.vy);
  if (speed > maxSpeed) {
    const scale = maxSpeed / speed;
    craft.vx *= scale;
    craft.vy *= scale;
  }
}

function normalizeAngle(angle) {
  const twoPi = Math.PI * 2;
  return ((angle % twoPi) + twoPi) % twoPi;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}
