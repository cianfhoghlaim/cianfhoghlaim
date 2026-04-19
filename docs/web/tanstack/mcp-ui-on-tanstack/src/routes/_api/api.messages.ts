import { createServerFileRoute } from '@tanstack/react-start/server'
import { transports } from '@/utils/demo.sse'

export const ServerRoute = createServerFileRoute('/_api/api/messages').methods({
  // @ts-ignore
  POST: async ({ request }) => {
    const body = await request.json()
    const url = new URL(request.url)
    const sessionId = url.searchParams.get('sessionId') as string
    const transport = transports[sessionId]
    if (transport) {
      try {
        await transport.handleMessage(body)
        return new Response(null, { status: 200 })
      } catch (error) {
        return new Response(null, { status: 500 })
      }
    } else {
      return new Response(null, { status: 404 })
    }
  },
})
