const { getDefaultConfig, mergeConfig } = require("@react-native/metro-config");
const path = require("node:path");

var list = [/\/__tests__\/.*/];

function escapeRegExp(pattern) {
  if (Object.prototype.toString.call(pattern) === "[object RegExp]") {
    // the forward slash may or may not be escaped in regular expression depends
    // on if it's in brackets. See this post for details
    // https://github.com/nodejs/help/issues/3039. The or condition in string
    // replace regexp is to cover both use cases.
    // We should replace all forward slashes to proper OS specific separators.
    // The separator needs to be escaped in the regular expression source string,
    // hence the '\\' prefix.
    return pattern.source.replace(/\/|\\\//g, "\\" + path.sep);
  } else if (typeof pattern === "string") {
    // Make sure all the special characters used by regular expression are properly
    // escaped. The string inputs are supposed to match as is.
    var escaped = pattern.replace(/[\-\[\]\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
    // convert the '/' into an escaped local file separator. The separator needs
    // to be escaped in the regular expression source string, hence the '\\' prefix.
    return escaped.replaceAll("/", "\\" + path.sep);
  } else {
    throw new Error("Unexpected exclusion pattern: " + pattern);
  }
}

function exclusionList(additionalExclusions) {
  return new RegExp(
    "(" +
      (additionalExclusions || []).concat(list).map(escapeRegExp).join("|") +
      ")$"
  );
}

/**
 * Metro configuration
 * https://reactnative.dev/docs/metro
 *
 * @type {import('@react-native/metro-config').MetroConfig}
 */

const defaultConfig = getDefaultConfig(__dirname);

const config = {
  // Watch the project root and its parent directory (the repository root)
  watchFolders: [
    path.resolve(__dirname, "."), // the example folder itself
    path.resolve(__dirname, "../"), // parent folder (repo root)
  ],
  resolver: {
    // Resolve modules from the example's node_modules first
    nodeModulesPaths: [path.resolve(__dirname, "./node_modules")],
    // Exclude the parent folder's node_modules from being processed by Metro
    blockList: exclusionList([
      // This regex matches any path that contains "/../node_modules/" (or Windows equivalent)
      new RegExp(
        `${path.resolve(__dirname, "..")}${path.sep}node_modules${path.sep}.*`
      ),
    ]),
    unstable_enableSymlinks: true,
  },
};

const config_merged = mergeConfig(defaultConfig, config);

module.exports = config_merged;
