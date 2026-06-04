export function Header() {
  return (
    <header className="h-14 bg-slate-950 border-b border-slate-800 flex items-center px-4 justify-between shrink-0">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center font-cinzel font-bold border-2 border-slate-800">
          A
        </div>
        <h1 className="font-cinzel font-bold text-xl tracking-widest text-emerald-500">
          AWEN HUB
        </h1>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
          <span className="text-xs font-mono text-slate-300">MCP Connected</span>
        </div>
        <button className="btn-tactile text-sm">Sign In (Web3)</button>
      </div>
    </header>
  );
}
