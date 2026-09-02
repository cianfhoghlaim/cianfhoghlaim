import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/biep-v2/__init__')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/biep-v2/__init__"!</div>
}
