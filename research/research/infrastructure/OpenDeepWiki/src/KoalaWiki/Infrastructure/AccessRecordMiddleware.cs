using System.Diagnostics;
using System.Security.Claims;
using KoalaWiki.Services;
using System.Collections.Concurrent;

namespace KoalaWiki.Infrastructure;

/// <summary>
/// 访问日志条目
/// </summary>
public class AccessLogEntry
{
    public string ResourceType { get; set; } = string.Empty;
    public string ResourceId { get; set; } = string.Empty;
    public string? UserId { get; set; }
    public string IpAddress { get; set; } = string.Empty;
    public string UserAgent { get; set; } = string.Empty;
    public string Path { get; set; } = string.Empty;
    public string Method { get; set; } = string.Empty;
    public int StatusCode { get; set; }
    public long ResponseTime { get; set; }
    public DateTime AccessTime { get; set; }
}

/// <summary>
/// 访问日志队列服务
/// </summary>
public class AccessLogQueue
{
    private readonly ConcurrentQueue<AccessLogEntry> _queue = new();
    private readonly SemaphoreSlim _semaphore = new(0);

    public void Enqueue(AccessLogEntry entry)
    {
        _queue.Enqueue(entry);
        _semaphore.Release();
    }

    public async Task<AccessLogEntry?> DequeueAsync(CancellationToken cancellationToken = default)
    {
        await _semaphore.WaitAsync(cancellationToken);
        _queue.TryDequeue(out var entry);
        return entry;
    }

    public int Count => _queue.Count;
}

/// <summary>
/// 访问记录中间件
/// </summary>
public class AccessRecordMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<AccessRecordMiddleware> _logger;
    private readonly AccessLogQueue _logQueue;

    public AccessRecordMiddleware(RequestDelegate next, ILogger<AccessRecordMiddleware> logger, AccessLogQueue logQueue)
    {
        _next = next;
        _logger = logger;
        _logQueue = logQueue;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        
        // 记录请求开始时间
        var startTime = DateTime.UtcNow;
        
        try
        {
            await _next(context);
        }
        finally
        {
            stopwatch.Stop();
            
            // 直接将日志条目加入队列，无需异步处理
            try
            {
                var logEntry = CreateAccessLogEntry(context, startTime, stopwatch.ElapsedMilliseconds);
                if (logEntry != null)
                {
                    _logQueue.Enqueue(logEntry);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "创建访问日志条目失败");
            }
        }
    }

    private AccessLogEntry? CreateAccessLogEntry(HttpContext context, DateTime startTime, long responseTime)
    {
        // 跳过静态资源和健康检查等不需要记录的请求
        if (ShouldSkipLogging(context))
        {
            return null;
        }

        // 获取用户信息
        var userId = context.User?.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        
        // 获取IP地址
        var ipAddress = GetClientIpAddress(context);
        
        // 获取用户代理
        var userAgent = context.Request.Headers["User-Agent"].FirstOrDefault() ?? "";
        
        // 解析资源类型和ID
        var (resourceType, resourceId) = ParseResourceInfo(context);

        return new AccessLogEntry
        {
            ResourceType = resourceType,
            ResourceId = resourceId,
            UserId = userId,
            IpAddress = ipAddress,
            UserAgent = userAgent,
            Path = context.Request.Path,
            Method = context.Request.Method,
            StatusCode = context.Response.StatusCode,
            ResponseTime = responseTime,
            AccessTime = startTime
        };
    }

    private bool ShouldSkipLogging(HttpContext context)
    {
        var path = context.Request.Path.Value?.ToLower();
        
        if (string.IsNullOrEmpty(path))
        {
            return true;
        }

        // 跳过静态资源
        if (path.Contains("/static/") || 
            path.Contains("/_next/") || 
            path.Contains("/favicon.ico") ||
            path.Contains("/robots.txt") ||
            path.Contains("/sitemap.xml") ||
            path.EndsWith(".css") ||
            path.EndsWith(".js") ||
            path.EndsWith(".png") ||
            path.EndsWith(".jpg") ||
            path.EndsWith(".jpeg") ||
            path.EndsWith(".gif") ||
            path.EndsWith(".svg") ||
            path.EndsWith(".ico") ||
            path.EndsWith(".woff") ||
            path.EndsWith(".woff2") ||
            path.EndsWith(".ttf") ||
            path.EndsWith(".eot"))
        {
            return true;
        }

        // 跳过健康检查和监控端点
        if (path.Contains("/health") ||
            path.Contains("/metrics") ||
            path.Contains("/swagger") ||
            path.Contains("/api/statistics/recordaccess"))
        {
            return true;
        }

        // 跳过开发环境的热重载请求
        if (path.Contains("/_framework/") ||
            path.Contains("/_vs/"))
        {
            return true;
        }

        return false;
    }

    private string GetClientIpAddress(HttpContext context)
    {
        // 尝试从不同的头部获取真实IP
        var headers = new[]
        {
            "CF-Connecting-IP",     // Cloudflare
            "X-Forwarded-For",      // 代理
            "X-Real-IP",            // Nginx
            "X-Client-IP",          // 其他代理
            "X-Forwarded",
            "X-Cluster-Client-IP",
            "Forwarded-For",
            "Forwarded"
        };

        foreach (var header in headers)
        {
            var value = context.Request.Headers[header].FirstOrDefault();
            if (!string.IsNullOrEmpty(value))
            {
                // X-Forwarded-For 可能包含多个IP，取第一个
                var ip = value.Split(',').FirstOrDefault()?.Trim();
                if (!string.IsNullOrEmpty(ip) && IsValidIpAddress(ip))
                {
                    return ip;
                }
            }
        }

        // 如果没有找到，使用连接的远程IP
        return context.Connection.RemoteIpAddress?.ToString() ?? "unknown";
    }

    private bool IsValidIpAddress(string ip)
    {
        if (string.IsNullOrEmpty(ip))
        {
            return false;
        }

        // 简单的IP格式验证
        return System.Net.IPAddress.TryParse(ip, out _);
    }

    private (string resourceType, string resourceId) ParseResourceInfo(HttpContext context)
    {
        var path = context.Request.Path.Value;
        
        if (string.IsNullOrEmpty(path))
        {
            return ("Page", "Unknown");
        }

        // 解析不同类型的资源
        var segments = path.Trim('/').Split('/');
        
        if (segments.Length == 0)
        {
            return ("Page", "Home");
        }

        // 仓库页面: /{owner}/{name}
        if (segments.Length >= 2 && !segments[0].StartsWith("api") && !segments[0].StartsWith("admin"))
        {
            var owner = segments[0];
            var name = segments[1];
            return ("Repository", $"{owner}/{name}");
        }

        // API调用
        if (segments.Length >= 1 && segments[0] == "api")
        {
            if (segments.Length >= 3)
            {
                var controller = segments[1];
                var action = segments[2];
                return ("API", $"{controller}/{action}");
            }
            return ("API", string.Join("/", segments.Skip(1)));
        }

        // 管理页面
        if (segments.Length >= 1 && segments[0] == "admin")
        {
            return ("Admin", string.Join("/", segments.Skip(1)));
        }

        // 搜索页面
        if (segments.Length >= 2 && segments[0] == "search")
        {
            return ("Search", segments[1]);
        }

        // 登录、注册等页面
        if (segments.Length >= 1)
        {
            var page = segments[0];
            switch (page.ToLower())
            {
                case "login":
                    return ("Page", "Login");
                case "register":
                    return ("Page", "Register");
                case "privacy":
                    return ("Page", "Privacy");
                case "terms":
                    return ("Page", "Terms");
                default:
                    return ("Page", page);
            }
        }

        return ("Page", "Unknown");
    }
}

/// <summary>
/// 访问记录中间件扩展
/// </summary>
public static class AccessRecordMiddlewareExtensions
{
    /// <summary>
    /// 使用访问记录中间件
    /// </summary>
    /// <param name="builder">应用构建器</param>
    /// <returns>应用构建器</returns>
    public static IApplicationBuilder UseAccessRecord(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<AccessRecordMiddleware>();
    }
} 