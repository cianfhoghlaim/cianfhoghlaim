import { defineConfig } from '@tanstack/react-start/config'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  tsr: {
    appDirectory: 'src',
  },
  vite: {
    plugins: [
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '~': '/Users/cliste/dev/bonneagar/hackathon/web/examples-working/tanstack-unified/src',
      },
    },
  },
})
