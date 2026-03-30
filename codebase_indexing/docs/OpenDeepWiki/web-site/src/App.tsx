import './App.css'
import { ThemeProvider } from "@/components/theme-provider"
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { Toaster } from 'sonner'
import ErrorBoundary from '@/components/common/ErrorBoundary'
import routes from './routes'

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <RouterProvider router={createBrowserRouter(routes)} />
        <Toaster position="top-right" richColors />
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App
