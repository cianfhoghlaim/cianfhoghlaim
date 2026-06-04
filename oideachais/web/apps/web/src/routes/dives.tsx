import { useState, useEffect } from "react";
import { client } from "../utils/orpc";

export function DivesPage() {
  const [session, setSession] = useState<string | null>(null);
  useEffect(() => {
    client.motherduck.embedSession.call({ username: "oideachais_service_user" }).then((r: { session: string }) => setSession(r.session)).catch(console.error);
  }, []);

  return (
    <div className="flex flex-col h-full">
      <h2 className="font-cinzel text-2xl font-bold mb-4 text-emerald-500">Embedded Dives</h2>
      <p className="text-slate-400 mb-6">Zero-latency MotherDuck Dives via <code className="px-1 bg-slate-800 rounded">@oideachais/api</code> oRPC.</p>
      <div className="flex-1 bg-slate-950 rounded-xl border border-slate-800 overflow-hidden relative">
        {session ? <iframe src={`https://embed-motherduck.com/sandbox/#session=${session}`} sandbox="allow-scripts allow-same-origin" className="w-full h-full border-none" title="MotherDuck Dive" /> : <div className="absolute inset-0 flex items-center justify-center text-slate-500">Loading MotherDuck session…</div>}
      </div>
    </div>
  );
}
