import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream({
    start(controller) {
      // Send initial plan
      const initialPlan = [
        {
          id: '1',
          title: 'Analyze Requirements',
          description: 'Parse user requirements and identify key components needed',
          status: 'pending'
        },
        {
          id: '2',
          title: 'Design Architecture',
          description: 'Plan the component structure and data flow',
          status: 'pending'
        },
        {
          id: '3',
          title: 'Generate Code',
          description: 'Write the React component with TypeScript',
          status: 'pending'
        },
        {
          id: '4',
          title: 'Test & Validate',
          description: 'Run tests and validate the implementation',
          status: 'pending'
        }
      ]

      controller.enqueue(
        encoder.encode(`data: ${JSON.stringify({ type: 'plan', data: initialPlan })}\n\n`)
      )

      // Simulate plan execution updates
      let stepIndex = 0
      const interval = setInterval(() => {
        if (stepIndex < initialPlan.length) {
          const updatedStep = {
            ...initialPlan[stepIndex],
            status: stepIndex === initialPlan.length - 1 ? 'running' : 'completed',
            output: `Step ${stepIndex + 1} ${stepIndex === initialPlan.length - 1 ? 'in progress...' : 'completed successfully'}`,
            duration: Math.floor(Math.random() * 5) + 1
          }

          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({ 
              type: 'step_update', 
              data: { stepId: initialPlan[stepIndex].id, update: updatedStep }
            })}\n\n`)
          )

          stepIndex++
        } else {
          // Complete the last step
          const finalStep = {
            ...initialPlan[initialPlan.length - 1],
            status: 'completed',
            output: 'All steps completed successfully!',
            duration: 3
          }

          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({ 
              type: 'step_update', 
              data: { stepId: initialPlan[initialPlan.length - 1].id, update: finalStep }
            })}\n\n`)
          )

          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({ type: 'execution_complete' })}\n\n`)
          )

          clearInterval(interval)
          controller.close()
        }
      }, 2000)

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
