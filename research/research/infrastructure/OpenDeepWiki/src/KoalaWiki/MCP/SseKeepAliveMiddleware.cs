using System.Text;
using ILogger = Microsoft.Extensions.Logging.ILogger;

namespace KoalaWiki.MCP;

/// <summary>
/// Middleware that adds SSE keep-alive pings to prevent connection timeout.
/// Claude Code and other MCP clients disconnect SSE connections after ~5 minutes of inactivity.
/// This middleware sends periodic keep-alive comments to maintain the connection.
/// </summary>
public class SseKeepAliveMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<SseKeepAliveMiddleware> _logger;
    private static readonly TimeSpan KeepAliveInterval = TimeSpan.FromSeconds(25);

    public SseKeepAliveMiddleware(RequestDelegate next, ILogger<SseKeepAliveMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Only apply to SSE endpoint
        if (!context.Request.Path.StartsWithSegments("/api/mcp/sse"))
        {
            await _next(context);
            return;
        }

        _logger.LogInformation("SSE Keep-Alive: Starting for path {Path}", context.Request.Path);

        // Save original response body stream
        var originalBodyStream = context.Response.Body;

        try
        {
            // Create wrapper to intercept SSE data
            using var responseWrapper = new SseKeepAliveStream(originalBodyStream, _logger);
            context.Response.Body = responseWrapper;

            // Start keep-alive timer
            using var cts = new CancellationTokenSource();
            var keepAliveTask = SendKeepAliveAsync(responseWrapper, cts.Token);

            try
            {
                // Call next middleware (MCP endpoint)
                await _next(context);
            }
            finally
            {
                // Stop keep-alive timer
                await cts.CancelAsync();

                try
                {
                    await keepAliveTask;
                }
                catch (OperationCanceledException)
                {
                    // Expected when cancelled
                }
            }

            // Finalize stream
            await responseWrapper.FinalizeAsync();
        }
        finally
        {
            // Restore original stream
            context.Response.Body = originalBodyStream;
        }

        _logger.LogInformation("SSE Keep-Alive: Completed for path {Path}", context.Request.Path);
    }

    private async Task SendKeepAliveAsync(SseKeepAliveStream stream, CancellationToken cancellationToken)
    {
        try
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                await Task.Delay(KeepAliveInterval, cancellationToken);

                if (!cancellationToken.IsCancellationRequested)
                {
                    await stream.WriteKeepAliveAsync(cancellationToken);
                    _logger.LogDebug("SSE Keep-Alive: Ping sent");
                }
            }
        }
        catch (OperationCanceledException)
        {
            // Expected when cancelled
            _logger.LogDebug("SSE Keep-Alive: Timer stopped");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "SSE Keep-Alive: Error in keep-alive task");
        }
    }
}

/// <summary>
/// Stream wrapper that adds SSE keep-alive pings.
/// Uses a semaphore for thread-safe writes between the main MCP endpoint and keep-alive task.
/// </summary>
internal class SseKeepAliveStream : Stream
{
    private readonly Stream _innerStream;
    private readonly ILogger _logger;
    private readonly SemaphoreSlim _writeLock = new(1, 1);
    private bool _disposed;

    public SseKeepAliveStream(Stream innerStream, ILogger logger)
    {
        _innerStream = innerStream ?? throw new ArgumentNullException(nameof(innerStream));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task WriteKeepAliveAsync(CancellationToken cancellationToken = default)
    {
        await _writeLock.WaitAsync(cancellationToken);
        try
        {
            // SSE keep-alive comment format: ": keepalive\n\n"
            // Comments in SSE start with colon and are ignored by clients
            var keepAliveBytes = Encoding.UTF8.GetBytes(": keepalive\n\n");
            await _innerStream.WriteAsync(keepAliveBytes, cancellationToken);
            await _innerStream.FlushAsync(cancellationToken);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    public async Task FinalizeAsync()
    {
        await _writeLock.WaitAsync();
        try
        {
            await _innerStream.FlushAsync();
        }
        finally
        {
            _writeLock.Release();
        }
    }

    public override async Task WriteAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken)
    {
        await _writeLock.WaitAsync(cancellationToken);
        try
        {
            await _innerStream.WriteAsync(buffer, offset, count, cancellationToken);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    public override async ValueTask WriteAsync(ReadOnlyMemory<byte> buffer, CancellationToken cancellationToken = default)
    {
        await _writeLock.WaitAsync(cancellationToken);
        try
        {
            await _innerStream.WriteAsync(buffer, cancellationToken);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    public override async Task FlushAsync(CancellationToken cancellationToken)
    {
        await _innerStream.FlushAsync(cancellationToken);
    }

    public override void Flush() => _innerStream.Flush();

    public override int Read(byte[] buffer, int offset, int count) =>
        _innerStream.Read(buffer, offset, count);

    public override long Seek(long offset, SeekOrigin origin) =>
        _innerStream.Seek(offset, origin);

    public override void SetLength(long value) =>
        _innerStream.SetLength(value);

    public override void Write(byte[] buffer, int offset, int count)
    {
        _writeLock.Wait();
        try
        {
            _innerStream.Write(buffer, offset, count);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    public override bool CanRead => _innerStream.CanRead;
    public override bool CanSeek => _innerStream.CanSeek;
    public override bool CanWrite => _innerStream.CanWrite;
    public override long Length => _innerStream.Length;
    public override long Position
    {
        get => _innerStream.Position;
        set => _innerStream.Position = value;
    }

    protected override void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                _writeLock?.Dispose();
                // Do NOT dispose _innerStream - it's owned by ASP.NET Core
            }
            _disposed = true;
        }
        base.Dispose(disposing);
    }
}
