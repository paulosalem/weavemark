// WeaveMark — lightweight source analysis shared by editor providers

const OPAQUE_BODY_DIRECTIVES = new Set([
  "embed",
  "execute",
  "note",
  "output",
  "package",
  "tool",
]);

function analyzeSource(text) {
  const lines = text.split(/\r?\n/);
  const ignoredLines = new Set();
  const literalLines = new Set();
  const declaredDirectives = new Set();
  const moduleAliases = new Set();
  let fence = null;
  let opaqueIndent = null;

  for (let index = 0; index < lines.length; index++) {
    const line = lines[index];
    const stripped = line.trimStart();
    const indent = line.length - stripped.length;
    const fenceMatch = stripped.match(/^(`{3,}|~{3,})/);

    if (fence) {
      ignoredLines.add(index);
      literalLines.add(index);
      if (fenceMatch && fenceMatch[1][0] === fence[0] && fenceMatch[1].length >= fence.length) {
        fence = null;
      }
      continue;
    }
    if (fenceMatch) {
      ignoredLines.add(index);
      literalLines.add(index);
      fence = fenceMatch[1];
      continue;
    }
    if (opaqueIndent !== null) {
      if (stripped === "" || indent > opaqueIndent) {
        ignoredLines.add(index);
        continue;
      }
      opaqueIndent = null;
    }
    if (stripped.startsWith("@@")) {
      ignoredLines.add(index);
      literalLines.add(index);
      continue;
    }

    const directive = findDirectiveToken(line);
    if (!directive) continue;
    const name = directive.name.replace(/\?$/, "");
    const directiveSource = directive.source;

    if (name === "define") {
      const definition = directiveSource.match(
        /^@define\s+([A-Za-z_][\w-]*)/
      );
      if (definition) declaredDirectives.add(definition[1]);
    } else if (name === "use") {
      collectUseImports(directiveSource, declaredDirectives, moduleAliases);
    }

    if (OPAQUE_BODY_DIRECTIVES.has(name)) {
      opaqueIndent = indent;
    }
  }

  return {
    declaredDirectives,
    ignoredLines,
    lines,
    literalLines,
    moduleAliases,
  };
}

function findDirectiveToken(line) {
  const direct = line.match(
    /^(\s*)@([A-Za-z_][\w.-]*\??)(?:\s|$)/
  );
  if (direct) {
    return {
      name: direct[2],
      start: direct[1].length,
      tokenLength: direct[2].length + 1,
      source: line.slice(direct[1].length),
    };
  }
  const heading = line.match(
    /^(\s*#{1,6}\s+)@([A-Za-z_][\w.-]*\??)(?:\s|$)/
  );
  if (heading) {
    return {
      name: heading[2],
      start: heading[1].length,
      tokenLength: heading[2].length + 1,
      source: line.slice(heading[1].length),
    };
  }
  const callout = line.match(
    /^(\s*>\s*\[!PROMPLET\s+)([A-Za-z_][\w.-]*\??)(.*)\]/
  );
  if (callout) {
    return {
      name: callout[2],
      start: callout[1].length,
      tokenLength: callout[2].length,
      source: `@${callout[2]}${callout[3]}`,
    };
  }
  return null;
}

function collectUseImports(line, declaredDirectives, moduleAliases) {
  const alias = line.match(/\bas\s+([A-Za-z_][\w-]*)\s*$/);
  if (alias) moduleAliases.add(alias[1]);

  const exposing = line.match(/\bexposing\s+(.+?)(?:\s+as\s+\S+)?\s*$/);
  if (!exposing) return;
  for (const name of exposing[1].split(/[\s,]+/)) {
    if (/^[A-Za-z_][\w-]*$/.test(name)) {
      declaredDirectives.add(name);
    }
  }
}

function isKnownDirective(name, catalogNames, analysis) {
  if (catalogNames.has(name) || analysis.declaredDirectives.has(name)) {
    return true;
  }
  const separator = name.indexOf(".");
  return (
    separator > 0 &&
    analysis.moduleAliases.has(name.slice(0, separator))
  );
}

module.exports = {
  OPAQUE_BODY_DIRECTIVES,
  analyzeSource,
  findDirectiveToken,
  isKnownDirective,
};
