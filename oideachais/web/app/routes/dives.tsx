import { useEffect, useState } from "react";
import { getEmbedSession } from "../server/motherduck";

export function Dives() {
  const [session, setSession] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await getEmbedSession({
          data: { username: "oideachais_service_user" },
        });
        if (mounted) {
          if (res.session) setSession(res.session);
          else setError("No session returned");
        }
      } catch (err) {
        if (mounted) setError(String(err));
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="flex flex-col h-full">
      <h2 className="font-cinzel text-2xl font-bold mb-4 text-emerald-500">Embedded Dives</h2>
      <p className="text-slate-400 mb-6">
        Zero-latency interactions powered by MotherDuck dual-execution (DuckDB-WASM).
        Embed sessions minted by the TanStack Start server function at
        <code className="ml-1 px-1 bg-slate-800 rounded">/api/motherduck/embed-session</code>
        using the MotherDuck REST API.
      </p>

      <div className="flex-1 bg-slate-950 rounded-xl border border-slate-800 overflow-hidden relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-400">
            <p className="font-bold mb-2">Failed to load MotherDuck session</p>
            <pre className="text-xs text-slate-500 text-left inline-block">{error}</pre>
          </div>
        ) : session ? (
          <iframe
            src={`https://embed-motherduck.com/sandbox/#session=${session}`}
            sandbox="allow-scripts allow-same-origin"
            className="w-full h-full border-none"
            title="MotherDuck Embedded Dive"
          />
        ) : (
          <div className="p-8 text-center text-slate-500">No session available</div>
        )}
      </div>
    </div>
  );
}
