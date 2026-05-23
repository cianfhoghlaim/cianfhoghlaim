import { Outlet, createRootRoute } from '@tanstack/react-router'
import * as React from 'react'
import { CopilotKit } from "@copilotkit/react-core"
import { AwenChat } from "../components/AwenChat"

export const Route = createRootRoute({
  component: RootComponent,
})

function RootComponent() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      {/* Navigation 3000 Layout - Top Nav */}
      <header className="h-14 bg-slate-950 border-b border-slate-800 flex items-center px-4 justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center font-cinzel font-bold border-2 border-slate-800">A</div>
          <h1 className="font-cinzel font-bold text-xl tracking-widest text-emerald-500">AWEN HUB</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
            <span className="text-xs font-mono text-slate-300">MCP Connected</span>
          </div>
          <button className="btn-tactile text-sm">Sign In (Web3)</button>
        </div>
      </header>

      {/* 3-Panel Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Panel 1: Object Explorer (Sidebar) */}
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
          <div className="p-4 border-b border-slate-800">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">Codex</h2>
          </div>
          <nav className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
            <a href="/" className="px-3 py-2 rounded-md hover:bg-slate-800/50 text-slate-300 transition-colors font-medium text-sm flex items-center gap-2">
              <span>📚</span> Curriculum
            </a>
            <a href="/dives" className="px-3 py-2 rounded-md hover:bg-slate-800/50 text-slate-300 transition-colors font-medium text-sm flex items-center gap-2">
              <span>🦆</span> Dives (MotherDuck)
            </a>
            <a href="/quests" className="px-3 py-2 rounded-md hover:bg-slate-800/50 text-slate-300 transition-colors font-medium text-sm flex items-center gap-2">
              <span>⚔️</span> Quests
            </a>
            <a href="/agents" className="px-3 py-2 rounded-md hover:bg-slate-800/50 text-slate-300 transition-colors font-medium text-sm flex items-center gap-2">
              <span>🤖</span> AgUI Agents
            </a>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col min-w-0 bg-stone-texture bg-slate-900 relative">
          <div className="flex-1 overflow-y-auto p-6">
            <Outlet />
          </div>
        </main>
      </div>
      
      {/* CopilotKit Popup Widget */}
      <AwenChat />
    </CopilotKit>
  )
}
