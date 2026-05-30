import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'

export const Route = createFileRoute('/')({
  component: IndexComponent,
})

function IndexComponent() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-8 h-full">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">Welcome to Awen Hub</h1>
        <p className="text-slate-400 text-lg">Your agentic gateway to the Celtic MMO.</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-600/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
            <span className="text-emerald-500">❖</span> Generative Curriculum
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Interact with dlt-ingested educational datasets using CopilotKit and TanStack AI.
          </p>
          <button className="btn-tactile w-full text-sm">Explore Datasets</button>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-600/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
            <span className="text-blue-500">⟠</span> Embedded Dives
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Interactive, zero-latency visualizations powered by MotherDuck and DuckDB-WASM.
          </p>
          <button className="btn-tactile w-full text-sm">Open MotherDuck</button>
        </div>
      </div>

      <div className="flex-1 bg-slate-950 rounded-xl border border-slate-800 p-4 flex flex-col">
        <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
          <h3 className="font-mono text-sm text-slate-400 font-bold">MCP_AGENT_TERMINAL</h3>
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-slate-700"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-slate-700"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500"></div>
          </div>
        </div>
        <div className="flex-1 flex flex-col justify-end">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm font-mono text-slate-300">
            <p className="text-emerald-500 mb-1">{'>'} Initializing Agno orchestration layer...</p>
            <p className="text-slate-500">{'>'} Awaiting input or generative UI events.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
