const Module = require("module");
const path = require("path");

function loadWithVscodeMock(relativePath, vscodeMock) {
  const absolutePath = path.resolve(__dirname, "..", relativePath);
  const extensionRoot = path.resolve(__dirname, "..");
  for (const key of Object.keys(require.cache)) {
    if (key.startsWith(extensionRoot + path.sep)) {
      delete require.cache[key];
    }
  }

  const originalLoad = Module._load;
  Module._load = function patchedLoad(request, parent, isMain) {
    if (request === "vscode") return vscodeMock;
    return originalLoad.call(this, request, parent, isMain);
  };
  try {
    return require(absolutePath);
  } finally {
    Module._load = originalLoad;
  }
}

module.exports = { loadWithVscodeMock };
