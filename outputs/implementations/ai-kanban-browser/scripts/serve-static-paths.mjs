import path from "node:path";

export function decodeRequestPath(requestUrl) {
  return decodeURIComponent(
    new URL(requestUrl, "http://static.invalid").pathname,
  );
}

export function resolveContainedPath(root, requestPath, pathApi = path) {
  let relativeRequest = String(requestPath).replace(/[\\/]+/g, pathApi.sep);
  while (relativeRequest.startsWith(pathApi.sep)) {
    relativeRequest = relativeRequest.slice(pathApi.sep.length);
  }
  const candidate = pathApi.resolve(root, relativeRequest);
  const relation = pathApi.relative(root, candidate);
  if (
    relation === ".." ||
    relation.startsWith(`..${pathApi.sep}`) ||
    pathApi.isAbsolute(relation)
  ) {
    throw new Error("Requested path escapes the static root.");
  }
  return candidate;
}
