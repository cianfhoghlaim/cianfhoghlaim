import { createMiddleware } from '@tanstack/react-start'
import { getHeaders } from '@tanstack/react-start/server'
import { auth } from './auth'

export const authMiddleware = createMiddleware({ type: 'function' }).server(
  async ({ next }) => {
    const session = await auth.api.getSession({
      headers: getHeaders() as unknown as Headers,
    })

    return await next({
      context: {
        user: session?.user
          ? {
              id: session.user.id,
              name: session.user.name,
              email: session.user.email,
              image: session.user.image,
            }
          : null,
      },
    })
  }
)
