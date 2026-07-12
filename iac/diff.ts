// bonneagar/iac/diff.ts — Deep-equal diff engine (for the plan command)

export interface DiffResult {
  added: Array<{ path: string; value: unknown }>;
  removed: Array<{ path: string; value: unknown }>;
  changed: Array<{ path: string; before: unknown; after: unknown }>;
}

export function deepDiff(before: unknown, after: unknown, path: string = "$"): DiffResult {
  const result: DiffResult = { added: [], removed: [], changed: [] };
  diff_(before, after, path, result);
  return result;
}

function diff_(a: unknown, b: unknown, path: string, out: DiffResult) {
  if (a === b) return;
  if (typeof a !== typeof b) {
    out.changed.push({ path, before: a, after: b });
    return;
  }
  if (a === null || b === null || typeof a !== "object") {
    if (a !== b) out.changed.push({ path, before: a, after: b });
    return;
  }
  const aKeys = Object.keys(a as Record<string, unknown>);
  const bKeys = Object.keys(b as Record<string, unknown>);
  const allKeys = new Set([...aKeys, ...bKeys]);
  for (const k of allKeys) {
    const childPath = `${path}.${k}`;
    const aHas = aKeys.includes(k);
    const bHas = bKeys.includes(k);
    if (!aHas) {
      out.added.push({ path: childPath, value: (b as Record<string, unknown>)[k] });
    } else if (!bHas) {
      out.removed.push({ path: childPath, value: (a as Record<string, unknown>)[k] });
    } else {
      diff_((a as Record<string, unknown>)[k], (b as Record<string, unknown>)[k], childPath, out);
    }
  }
}

export function redactSecrets<T>(obj: T, secretKeys: string[] = ["value", "password", "token", "client_secret", "api_key"]): T {
  // Walk the object and replace any field whose key matches a secret pattern
  if (obj === null || obj === undefined) return obj;
  if (typeof obj !== "object") return obj;
  if (Array.isArray(obj)) {
    return obj.map((item) => redactSecrets(item, secretKeys)) as T;
  }
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(obj as Record<string, unknown>)) {
    if (secretKeys.includes(k.toLowerCase()) && typeof v === "string" && v.length > 0) {
      out[k] = "***REDACTED***";
    } else {
      out[k] = redactSecrets(v, secretKeys);
    }
  }
  return out as T;
}
