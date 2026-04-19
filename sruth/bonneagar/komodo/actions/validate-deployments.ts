// =============================================================================
// VALIDATE DEPLOYMENTS ACTION
// =============================================================================
// Performs post-deployment health checks across all stacks and servers.
// Run this after deployments to verify services are running correctly.
//
// Usage:
//   km run action validate-deployments
//   km run action validate-deployments --stack=forgejo
//   km run action validate-deployments --server=arm1-oci
// =============================================================================

const targetStack = ARGS.stack || "";
const targetServer = ARGS.server || "";
const timeout = ARGS.timeout || 30; // seconds

interface ValidationResult {
  name: string;
  type: "stack" | "server" | "endpoint";
  status: "healthy" | "unhealthy" | "unknown";
  message: string;
  details?: object;
}

const results: ValidationResult[] = [];

console.log("=== Validating Deployments ===\n");

// 1. Validate Servers
console.log("Checking servers...");
const servers = await komodo.read("ListServers", {});

for (const server of servers) {
  if (targetServer && server.name !== targetServer) continue;

  const details = await komodo.read("GetServer", { server: server.name });
  const state = details?.info?.state;

  if (state === "Ok") {
    console.log(`  [OK] ${server.name} - Periphery connected`);
    results.push({
      name: server.name,
      type: "server",
      status: "healthy",
      message: "Periphery connected",
      details: { state, version: details?.info?.version },
    });
  } else {
    console.log(`  [FAIL] ${server.name} - State: ${state || "Unknown"}`);
    results.push({
      name: server.name,
      type: "server",
      status: "unhealthy",
      message: `State: ${state || "Unknown"}`,
    });
  }
}

// 2. Validate Stacks
console.log("\nChecking stacks...");
const stacks = await komodo.read("ListStacks", {});

for (const stack of stacks) {
  if (targetStack && stack.name !== targetStack) continue;
  if (targetServer && stack.info?.server_id !== targetServer) continue;

  const details = await komodo.read("GetStack", { stack: stack.name });
  const state = details?.info?.state;

  // Check if stack is running
  if (state === "Running") {
    // Try to get container status
    const serverName = servers.find((s) => s.id === details?.config?.server)?.name;
    if (serverName) {
      try {
        const psResult = await komodo.execute("RunCommand", {
          server: serverName,
          command: `docker compose -f /etc/komodo/${stack.name}/compose.yaml ps --format json 2>/dev/null || echo "[]"`,
        });

        const containers = JSON.parse(psResult.stdout || "[]");
        const runningCount = Array.isArray(containers)
          ? containers.filter((c: { State?: string }) => c.State === "running").length
          : 0;
        const totalCount = Array.isArray(containers) ? containers.length : 0;

        if (runningCount === totalCount && totalCount > 0) {
          console.log(`  [OK] ${stack.name} - ${runningCount}/${totalCount} containers running`);
          results.push({
            name: stack.name,
            type: "stack",
            status: "healthy",
            message: `${runningCount}/${totalCount} containers running`,
            details: { server: serverName, containers: totalCount },
          });
        } else {
          console.log(`  [WARN] ${stack.name} - ${runningCount}/${totalCount} containers running`);
          results.push({
            name: stack.name,
            type: "stack",
            status: "unhealthy",
            message: `${runningCount}/${totalCount} containers running`,
            details: { server: serverName, containers: totalCount },
          });
        }
      } catch (err) {
        console.log(`  [WARN] ${stack.name} - Could not check containers`);
        results.push({
          name: stack.name,
          type: "stack",
          status: "unknown",
          message: "Could not check container status",
        });
      }
    }
  } else if (state === "Unknown" || !state) {
    console.log(`  [SKIP] ${stack.name} - Not deployed`);
  } else {
    console.log(`  [FAIL] ${stack.name} - State: ${state}`);
    results.push({
      name: stack.name,
      type: "stack",
      status: "unhealthy",
      message: `State: ${state}`,
    });
  }
}

// 3. Validate Endpoints (for stacks with known domains)
console.log("\nChecking endpoints...");

const endpointChecks = [
  { name: "Komodo", url: "https://komodo.cianfhoghlaim.ie/health" },
  { name: "Pangolin", url: "https://pangolin.cianfhoghlaim.ie/api/v1/health" },
  { name: "Auth", url: "https://auth.cianfhoghlaim.ie/.well-known/openid-configuration" },
];

for (const endpoint of endpointChecks) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout * 1000);

    const response = await fetch(endpoint.url, {
      method: "GET",
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      console.log(`  [OK] ${endpoint.name} - ${endpoint.url}`);
      results.push({
        name: endpoint.name,
        type: "endpoint",
        status: "healthy",
        message: `HTTP ${response.status}`,
        details: { url: endpoint.url },
      });
    } else {
      console.log(`  [WARN] ${endpoint.name} - HTTP ${response.status}`);
      results.push({
        name: endpoint.name,
        type: "endpoint",
        status: "unhealthy",
        message: `HTTP ${response.status}`,
        details: { url: endpoint.url },
      });
    }
  } catch (err) {
    const errorMessage = (err as Error).message;
    if (errorMessage.includes("abort")) {
      console.log(`  [FAIL] ${endpoint.name} - Timeout after ${timeout}s`);
      results.push({
        name: endpoint.name,
        type: "endpoint",
        status: "unhealthy",
        message: `Timeout after ${timeout}s`,
        details: { url: endpoint.url },
      });
    } else {
      console.log(`  [FAIL] ${endpoint.name} - ${errorMessage}`);
      results.push({
        name: endpoint.name,
        type: "endpoint",
        status: "unhealthy",
        message: errorMessage,
        details: { url: endpoint.url },
      });
    }
  }
}

// Summary
console.log("\n=== Validation Summary ===");
const healthy = results.filter((r) => r.status === "healthy").length;
const unhealthy = results.filter((r) => r.status === "unhealthy").length;
const unknown = results.filter((r) => r.status === "unknown").length;

console.log(`  Healthy:   ${healthy}`);
console.log(`  Unhealthy: ${unhealthy}`);
console.log(`  Unknown:   ${unknown}`);

const overallSuccess = unhealthy === 0;
console.log(`\nOverall: ${overallSuccess ? "PASSED" : "FAILED"}`);

return {
  success: overallSuccess,
  summary: {
    total: results.length,
    healthy,
    unhealthy,
    unknown,
  },
  results,
};
