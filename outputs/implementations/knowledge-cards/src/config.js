export const APP_VERSION = "1.0.0";
export const DB_NAME = "knowledge-cards-local";
export const DB_VERSION = 1;
export const PACK_INDEX_URL = "./content/packs/index.json";
export const DEFAULT_SESSION_SEED = "knowledge-cards-v1";
export const HISTORY_LIMIT = 500;

export const STORE_NAMES = Object.freeze({
  packCache: "packCache",
  progress: "progress",
  sessionOrders: "sessionOrders",
  cardStates: "cardStates",
  notes: "notes",
  noteDrafts: "noteDrafts",
  savedCards: "savedCards",
  revisitQueue: "revisitQueue",
  history: "history",
  preferences: "preferences",
  importExports: "importExports"
});

export const DEFAULT_PREFERENCES = Object.freeze({
  id: "default",
  orderedMode: "adaptive",
  textSize: "regular",
  reducedMotion: false,
  onboardingDismissed: false,
  sessionCardLimit: 10,
  sessionMinuteLimit: 10
});
