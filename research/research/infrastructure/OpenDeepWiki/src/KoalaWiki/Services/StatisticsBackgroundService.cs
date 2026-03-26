using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace KoalaWiki.Services;

/// <summary>
/// 统计后台服务
/// </summary>
public class StatisticsBackgroundService : BackgroundService
{
    private readonly ILogger<StatisticsBackgroundService> _logger;
    private readonly IServiceProvider _serviceProvider;

    public StatisticsBackgroundService(
        ILogger<StatisticsBackgroundService> logger,
        IServiceProvider serviceProvider)
    {
        _logger = logger;
        _serviceProvider = serviceProvider;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("统计后台服务启动");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                // 等待到下一个运行时间
                var nextRunTime = GetNextRunTime();
                var delay = nextRunTime - DateTime.UtcNow;
                
                if (delay > TimeSpan.Zero)
                {
                    _logger.LogInformation("下次统计任务将在 {NextRunTime} 运行", nextRunTime);
                    await Task.Delay(delay, stoppingToken);
                }

                if (stoppingToken.IsCancellationRequested)
                {
                    break;
                }

                // 执行统计任务
                await ExecuteStatisticsTask();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "统计后台服务发生错误");
                
                // 发生错误时等待1小时后重试
                await Task.Delay(TimeSpan.FromHours(1), stoppingToken);
            }
        }

        _logger.LogInformation("统计后台服务停止");
    }

    private async Task ExecuteStatisticsTask()
    {
        using var scope = _serviceProvider.CreateScope();
        var statisticsService = scope.ServiceProvider.GetRequiredService<StatisticsService>();

        try
        {
            _logger.LogInformation("开始执行统计任务");

            // 生成昨天的统计数据
            var yesterday = DateTime.UtcNow.Date.AddDays(-1);
            var success = await statisticsService.GenerateDailyStatisticsAsync(yesterday);

            if (success)
            {
                _logger.LogInformation("统计任务执行成功，日期: {Date}", yesterday.ToString("yyyy-MM-dd"));
            }
            else
            {
                _logger.LogWarning("统计任务执行失败，日期: {Date}", yesterday.ToString("yyyy-MM-dd"));
            }

            // 清理旧的访问记录（保留90天）
            await CleanupOldAccessRecords(scope);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "执行统计任务时发生错误");
        }
    }

    private async Task CleanupOldAccessRecords(IServiceScope scope)
    {
        try
        {
            var dbContext = scope.ServiceProvider.GetRequiredService<IKoalaWikiContext>();
            var cutoffDate = DateTime.UtcNow.Date.AddDays(-90);

            var deletedCount = await dbContext.AccessRecords
                .Where(a => a.CreatedAt < cutoffDate)
                .ExecuteDeleteAsync();

            if (deletedCount > 0)
            {
                _logger.LogInformation("清理了 {Count} 条旧访问记录", deletedCount);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "清理旧访问记录时发生错误");
        }
    }

    private DateTime GetNextRunTime()
    {
        var now = DateTime.UtcNow;
        
        // 每天凌晨1点执行统计任务
        var nextRun = new DateTime(now.Year, now.Month, now.Day, 1, 0, 0, DateTimeKind.Utc);
        
        // 如果当前时间已经过了今天的运行时间，则安排明天运行
        if (now >= nextRun)
        {
            nextRun = nextRun.AddDays(1);
        }

        return nextRun;
    }
} 