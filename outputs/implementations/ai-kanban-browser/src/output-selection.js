const SUCCESSFUL_STATUSES = new Set(["complete", "approved"]);

export function latestSuccessfulOutput(card) {
  const outputs = Array.isArray(card?.outputs) ? card.outputs : [];
  if (card?.latestSuccessfulOutputVersionId && card?.outputVersions) {
    for (const output of outputs) {
      const version = (card.outputVersions[output.id] || []).find(
        (item) => item.id === card.latestSuccessfulOutputVersionId,
      );
      if (version && SUCCESSFUL_STATUSES.has(version.status)) {
        return {
          ...output,
          title: version.title,
          content: version.content,
          status: version.status,
          updatedAt: version.createdAt,
          successfulVersion: version.version,
        };
      }
    }
  }
  const projected = card?.latestOutputId
    ? outputs.find(
        (output) =>
          output.id === card.latestOutputId &&
          SUCCESSFUL_STATUSES.has(output.status),
      )
    : null;
  if (projected) return projected;
  return outputs
    .filter((output) => SUCCESSFUL_STATUSES.has(output.status))
    .sort(
      (left, right) =>
        Date.parse(right.updatedAt || right.createdAt || 0) -
        Date.parse(left.updatedAt || left.createdAt || 0),
    )[0] || null;
}
