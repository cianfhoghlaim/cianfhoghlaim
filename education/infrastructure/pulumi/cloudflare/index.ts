import * as pulumi from "@pulumi/pulumi";
import * as cloudflare from "@pulumi/cloudflare";

// This program provisions a Cloudflare KV Namespace and exports structured outputs for
// KV, plus metadata for R2 and D1 that you can use for Cloudflare Worker bindings.
//
// Notes
// - The Cloudflare provider must already be configured (e.g., pulumi config set cloudflare:accountId ...).
// - Optional app config values: r2BucketName, kvNamespaceName, d1Name (we default to project-stack-<svc>).
// - As of this writing, R2 Bucket and D1 Database don't have first-class resources in this provider.
//   We export consistent names/IDs you can bind in Worker scripts. Create the actual R2/D1 via
//   Wrangler/CLI/UI and bind using WorkerScript as shown in comments below.

const cfg = new pulumi.Config();
const project = pulumi.getProject();
const stack = pulumi.getStack();

// Optional names. If not provided, derive from project/stack.
const r2BucketName = cfg.get("r2BucketName") || `${project}-${stack}-r2`;
const kvNamespaceName = cfg.get("kvNamespaceName") || `${project}-${stack}-kv`;
const d1Name = cfg.get("d1Name") || `${project}-${stack}-d1`;

// KV Namespace
// Docs: https://www.pulumi.com/registry/packages/cloudflare/api-docs/workerskvnamespace/
const kv = new cloudflare.WorkersKvNamespace("kv", {
  // accountId is taken from the configured provider; if you are using multiple accounts,
  // pass a dedicated provider via the `provider` option instead of setting accountId here.
  title: kvNamespaceName,
});

// R2 Bucket metadata (name only) — exported for Worker bindings. Versioning/public listing disabled by default.
const r2BucketNameOut = pulumi.output(r2BucketName);

// D1 Database metadata — export intended name and a deterministic ID placeholder you can replace
// with the actual ID after creating the DB via Cloudflare CLI/API/UI.
const d1 = {
  name: d1Name,
  id: pulumi.interpolate`${project}-${stack}-d1-id`,
};

// Optional Worker showing how you'd bind KV and R2 using these outputs.
// Docs: https://www.pulumi.com/registry/packages/cloudflare/api-docs/workerscript/
/*
const worker = new cloudflare.WorkerScript("app-worker", {
  name: `${project}-${stack}-worker`,
  module: false, // set true if using module syntax
  compatibilityDate: "2024-11-01",
  content: `addEventListener('fetch', e => e.respondWith(new Response('ok')))`,
  r2BucketBindings: [{
    name: "BUCKET",
    bucketName: r2BucketNameOut,
  }],
  kvNamespaceBindings: [{
    name: "KV",
    namespaceId: kv.id,
  }],
  // D1 binding is not first-class yet; once available, add analogous binding here.
});
*/

// Structured exports
export const r2 = {
  bucketName: r2BucketNameOut,
  publicListingEnabled: false,
  versioningEnabled: false,
};

export const kvOut = {
  name: kvNamespaceName,
  namespaceId: kv.id,
};

export const d1Out = {
  name: d1.name,
  id: d1.id,
};

export const bindings = {
  r2: { bindingName: "BUCKET", bucketName: r2.bucketName },
  kv: { bindingName: "KV", namespaceId: kvOut.namespaceId },
  d1: { bindingName: "DB", databaseId: d1Out.id, databaseName: d1Out.name },
};