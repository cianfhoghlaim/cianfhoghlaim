import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream({
    start(controller) {
      // Send initial agent message
      setTimeout(() => {
        const message = {
          id: Date.now().toString(),
          type: 'agent',
          content: 'I understand! Let me create a plan to build that for you. I\'ll break this down into manageable steps and execute them one by one.',
          timestamp: new Date().toISOString()
        }

        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ type: 'message', data: message })}\n\n`)
        )
      }, 1000)

      // Send progress updates
      const updates = [
        'Analyzing your requirements...',
        'Creating the execution plan...',
        'Starting code generation...',
        'Applying best practices...',
        'Almost done! Finalizing the implementation...'
      ]

      let updateIndex = 0
      const interval = setInterval(() => {
        if (updateIndex < updates.length) {
          const message = {
            id: (Date.now() + updateIndex).toString(),
            type: 'agent',
            content: updates[updateIndex],
            timestamp: new Date().toISOString()
          }

          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({ type: 'message', data: message })}\n\n`)
          )

          updateIndex++
        } else {
          const finalMessage = {
            id: (Date.now() + 999).toString(),
            type: 'agent',
            content: 'Perfect! I\'ve successfully completed your request. The code has been generated and is ready for use.',
            timestamp: new Date().toISOString()
          }

          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({ type: 'message', data: finalMessage })}\n\n`)
          )

          clearInterval(interval)
          controller.close()
        }
      }, 3000)

      // Clean up on abort
      request.signal.addEventListener('abort', () => {
        clearInterval(interval)
        controller.close()
      })
    }
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
