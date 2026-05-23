import { Router } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'

// Create a new router instance
export const router = new Router({ routeTree })

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
