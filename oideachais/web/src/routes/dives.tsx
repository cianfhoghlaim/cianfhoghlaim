import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useState } from 'react'

export const Route = createFileRoute('/dives')({
  component: DivesComponent,
})

function DivesComponent() {
  const [session, setSession] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // In a real app, this would hit our TanStack Start server function
    // which securely calls MotherDuck using MOTHERDUCK_TOKEN
    const fetchSession = async () => {
      try {
        const response = await fetch('/api/motherduck/embed-session', { method: 'POST' })
        if (response.ok) {
          const data = await response.json()
          setSession(data.session)
        } else {
          console.error("Failed to fetch session")
        }
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    
    // Fallback dummy for development
    setTimeout(() => {
      setSession("dummy_session_id")
      setLoading(false)
    }, 1000)
    
    // Uncomment for actual API call
    // fetchSession()
  }, [])

  return (
    <div className="flex flex-col h-full">
      <h2 className="font-cinzel text-2xl font-bold mb-4 text-emerald-500">Embedded Dives</h2>
      <p className="text-slate-400 mb-6">Zero-latency interactions powered by MotherDuck dual-execution (DuckDB-Wasm).</p>
      
      <div className="flex-1 bg-slate-950 rounded-xl border border-slate-800 overflow-hidden relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div>
          </div>
        ) : session ? (
          <iframe 
            src={`https://embed-motherduck.com/sandbox/#session=${session}`}
            sandbox="allow-scripts allow-same-origin"
            className="w-full h-full border-none"
            title="MotherDuck Embedded Dive"
          />
        ) : (
          <div className="p-8 text-center text-red-400">Failed to load MotherDuck session</div>
        )}
      </div>
    </div>
  )
}
