import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCcw, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)

    this.setState({
      error,
      errorInfo
    })

    // 调用外部错误处理函数
    this.props.onError?.(error, errorInfo)

    // 在生产环境中，可以将错误发送到错误监控服务
    if (process.env.NODE_ENV === 'production') {
      // TODO: 发送错误到监控服务，如 Sentry
      // captureException(error, { extra: errorInfo })
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      // 如果有自定义的 fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback
      }

      // 默认的错误 UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-background">
          <div className="max-w-md w-full mx-auto text-center space-y-6 p-6">
            <div className="flex justify-center">
              <div className="rounded-full bg-destructive/10 p-4">
                <AlertTriangle className="h-8 w-8 text-destructive" />
              </div>
            </div>

            <div className="space-y-2">
              <h1 className="text-2xl font-bold text-foreground">
                出现了一些问题
              </h1>
              <p className="text-muted-foreground">
                页面遇到了意外错误，请尝试刷新页面或返回首页。
              </p>
            </div>

            {/* 开发环境显示错误详情 */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="text-left text-sm bg-muted p-4 rounded-lg">
                <summary className="cursor-pointer font-medium text-destructive mb-2">
                  错误详情 (仅开发环境显示)
                </summary>
                <div className="space-y-2 font-mono text-xs">
                  <div>
                    <strong>错误信息:</strong>
                    <div className="bg-background p-2 rounded border mt-1">
                      {this.state.error.message}
                    </div>
                  </div>
                  <div>
                    <strong>错误堆栈:</strong>
                    <div className="bg-background p-2 rounded border mt-1 max-h-32 overflow-y-auto">
                      {this.state.error.stack}
                    </div>
                  </div>
                  {this.state.errorInfo && (
                    <div>
                      <strong>组件堆栈:</strong>
                      <div className="bg-background p-2 rounded border mt-1 max-h-32 overflow-y-auto">
                        {this.state.errorInfo.componentStack}
                      </div>
                    </div>
                  )}
                </div>
              </details>
            )}

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button
                onClick={this.handleRetry}
                className="flex items-center gap-2"
              >
                <RefreshCcw className="h-4 w-4" />
                重试
              </Button>
              <Button
                variant="outline"
                onClick={this.handleGoHome}
                className="flex items-center gap-2"
              >
                <Home className="h-4 w-4" />
                返回首页
              </Button>
            </div>

            <p className="text-xs text-muted-foreground">
              如果问题持续存在，请联系技术支持。
            </p>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook 版本的 Error Boundary（使用 react-error-boundary 库的模式）
interface ErrorFallbackProps {
  error: Error
  resetErrorBoundary: () => void
}

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetErrorBoundary
}) => (
  <div className="min-h-[400px] flex items-center justify-center">
    <div className="text-center space-y-4 p-6">
      <div className="flex justify-center">
        <div className="rounded-full bg-destructive/10 p-3">
          <AlertTriangle className="h-6 w-6 text-destructive" />
        </div>
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-foreground">
          组件加载失败
        </h3>
        <p className="text-sm text-muted-foreground">
          {error.message || '遇到了意外错误'}
        </p>
      </div>
      <Button onClick={resetErrorBoundary} size="sm">
        重新加载
      </Button>
    </div>
  </div>
)

// 高阶组件，用于包装需要错误边界的组件
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode
) => {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary fallback={fallback}>
      <Component {...props} />
    </ErrorBoundary>
  )

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`

  return WrappedComponent
}

export default ErrorBoundary