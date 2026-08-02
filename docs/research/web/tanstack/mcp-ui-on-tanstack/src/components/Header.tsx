import { Link } from '@tanstack/react-router'

import TanStackChatHeaderUser from '../integrations/tanchat/header-user.tsx'

export default function Header() {
  return (
    <header className="p-2 flex gap-2 bg-white text-black justify-between">
      <nav className="flex flex-row">
        <div className="px-2 font-bold">
          <Link to="/">Home</Link>
        </div>

        <div className="px-2 font-bold">
          <Link to="/demo/start/server-funcs">Start - Server Functions</Link>
        </div>

        <div className="px-2 font-bold">
          <Link to="/demo/start/api-request">Start - API Request</Link>
        </div>

        <div className="px-2 font-bold">
          <Link to="/demo/mcp-todos">MCP</Link>
        </div>

        <div className="px-2 font-bold">
          <Link to="/example/chat">Chat</Link>
        </div>

        <div className="px-2 font-bold">
          <Link to="/example/guitars">Guitar Demo</Link>
        </div>

        <div className="px-2 font-bold">
          <Link to="/demo/store">Store</Link>
        </div>
      </nav>

      <div>
        <TanStackChatHeaderUser />
      </div>
    </header>
  )
}
