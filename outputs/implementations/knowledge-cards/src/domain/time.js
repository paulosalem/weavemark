export function nowIso() {
  return new Date().toISOString();
}

export function minutesBetween(startIso, endDate = new Date()) {
  const start = Date.parse(startIso);
  if (!Number.isFinite(start)) return 0;
  return Math.max(0, Math.floor((endDate.getTime() - start) / 60000));
}
