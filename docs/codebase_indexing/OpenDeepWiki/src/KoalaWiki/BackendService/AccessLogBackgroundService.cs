namespace KoalaWiki.BackendService;

/// <summary>
/// 访问日志后台处理服务
/// </summary>
public class AccessLogBackgroundService(
    IServiceProvider serviceProvider,
    AccessLogQueue logQueue,
    ILogger<AccessLogBackgroundService> logger)
    : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        logger.LogInformation("访问日志后台处理服务已启动");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var logEntry = await logQueue.DequeueAsync(stoppingToken);
                if (logEntry != null)
                {
                    await ProcessLogEntryAsync(logEntry);
                }
            }
            catch (OperationCanceledException)
            {
                // 正常的取消操作，退出循环
                break;
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "处理访问日志时发生错误");
                
                // 发生错误时等待一段时间再继续
                try
                {
                    await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
            }
        }

        logger.LogInformation("访问日志后台处理服务已停止");
    }

    private async Task ProcessLogEntryAsync(AccessLogEntry logEntry)
    {
        try
        {
            using var scope = serviceProvider.CreateScope();
            var statisticsService = scope.ServiceProvider.GetService<StatisticsService>();
            
            if (statisticsService != null)
            {
                await statisticsService.RecordAccessAsync(
                    resourceType: logEntry.ResourceType,
                    resourceId: logEntry.ResourceId,
                    userId: logEntry.UserId,
                    ipAddress: logEntry.IpAddress,
                    userAgent: logEntry.UserAgent,
                    path: logEntry.Path,
                    method: logEntry.Method,
                    statusCode: logEntry.StatusCode,
                    responseTime: logEntry.ResponseTime
                );
            }
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "处理访问日志条目失败: {ResourceType}/{ResourceId}, Path: {Path}", 
                logEntry.ResourceType, logEntry.ResourceId, logEntry.Path);
        }
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        logger.LogInformation("正在停止访问日志后台处理服务...");
        
        // 处理队列中剩余的日志条目
        var remainingCount = logQueue.Count;
        if (remainingCount > 0)
        {
            logger.LogInformation("处理队列中剩余的 {Count} 条访问日志", remainingCount);
            
            var timeout = TimeSpan.FromSeconds(30); // 最多等待30秒
            var endTime = DateTime.UtcNow.Add(timeout);
            
            while (logQueue.Count > 0 && DateTime.UtcNow < endTime)
            {
                try
                {
                    var logEntry = await logQueue.DequeueAsync(cancellationToken);
                    if (logEntry != null)
                    {
                        await ProcessLogEntryAsync(logEntry);
                    }
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    logger.LogError(ex, "停止时处理访问日志失败");
                }
            }
        }

        await base.StopAsync(cancellationToken);
    }
} 