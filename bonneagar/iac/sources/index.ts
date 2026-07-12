// bonneagar/iac/sources/index.ts — Re-export the 4 source-discoverers

export { discoverStacks, type DiscoveredStack } from "./discover-stacks.ts";
export { discoverResources } from "./discover-resources.ts";
export { discoverSecrets } from "./discover-secrets.ts";
export { getKeyStacks, getKeyStacksByGroup, KEY_STACKS_5_GROUP_MODEL } from "./key-stacks.ts";
