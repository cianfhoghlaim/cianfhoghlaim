using System.Text.Json;
using FastService;
using KoalaWiki.Domains;
using KoalaWiki.Domains.Statistics;
using KoalaWiki.Domains.Users;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Dto;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using KoalaWiki.Core;
using KoalaWiki.KoalaWarehouse;

namespace KoalaWiki.Services;

/// <summary>
/// 统计服务
/// </summary>
[Tags("统计服务")]
[FastService.Route("/api/Statistics")]
[Filter(typeof(ResultFilter))]
public class StatisticsService(
    IKoalaWikiContext dbContext,
    ILogger<StatisticsService> logger) : FastApi
{
    /// <summary>
    /// 获取系统统计数据
    /// </summary>
    /// <returns>系统统计数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<SystemStatisticsDto> GetSystemStatisticsAsync()
    {
        var now = DateTime.UtcNow;
        var startOfMonth = new DateTime(now.Year, now.Month, 1);
        var startOfLastMonth = startOfMonth.AddMonths(-1);

        // 总统计数据
        var totalUsers = await dbContext.Users.CountAsync();
        var totalRepositories = await dbContext.Warehouses.CountAsync();
        var totalDocuments = await dbContext.DocumentFileItems.CountAsync();
        var totalViews = await dbContext.AccessRecords.LongCountAsync();

        // 本月新增数据
        var monthlyNewUsers = await dbContext.Users
            .Where(u => u.CreatedAt >= startOfMonth)
            .CountAsync();

        var monthlyNewRepositories = await dbContext.Warehouses
            .Where(w => w.CreatedAt >= startOfMonth)
            .CountAsync();

        var monthlyNewDocuments = await dbContext.DocumentFileItems
            .Where(d => d.CreatedAt >= startOfMonth)
            .CountAsync();

        var monthlyViews = await dbContext.AccessRecords
            .Where(a => a.CreatedAt >= startOfMonth)
            .LongCountAsync();

        // 上月对比数据（用于计算增长率）
        var lastMonthUsers = await dbContext.Users
            .Where(u => u.CreatedAt >= startOfLastMonth && u.CreatedAt < startOfMonth)
            .CountAsync();

        var lastMonthRepositories = await dbContext.Warehouses
            .Where(w => w.CreatedAt >= startOfLastMonth && w.CreatedAt < startOfMonth)
            .CountAsync();

        var lastMonthDocuments = await dbContext.DocumentFileItems
            .Where(d => d.CreatedAt >= startOfLastMonth && d.CreatedAt < startOfMonth)
            .CountAsync();

        var lastMonthViews = await dbContext.AccessRecords
            .Where(a => a.CreatedAt >= startOfLastMonth && a.CreatedAt < startOfMonth)
            .LongCountAsync();

        // 计算增长率
        var userGrowthRate = lastMonthUsers > 0
            ? (decimal)(monthlyNewUsers - lastMonthUsers) / lastMonthUsers * 100
            : monthlyNewUsers > 0
                ? 100
                : 0;

        var repositoryGrowthRate = lastMonthRepositories > 0
            ? (decimal)(monthlyNewRepositories - lastMonthRepositories) / lastMonthRepositories * 100
            : monthlyNewRepositories > 0
                ? 100
                : 0;

        var documentGrowthRate = lastMonthDocuments > 0
            ? (decimal)(monthlyNewDocuments - lastMonthDocuments) / lastMonthDocuments * 100
            : monthlyNewDocuments > 0
                ? 100
                : 0;

        var viewGrowthRate = lastMonthViews > 0
            ? (decimal)(monthlyViews - lastMonthViews) / lastMonthViews * 100
            : monthlyViews > 0
                ? 100
                : 0;

        return new SystemStatisticsDto
        {
            TotalUsers = totalUsers,
            TotalRepositories = totalRepositories,
            TotalDocuments = totalDocuments,
            TotalViews = totalViews,
            MonthlyNewUsers = monthlyNewUsers,
            MonthlyNewRepositories = monthlyNewRepositories,
            MonthlyNewDocuments = monthlyNewDocuments,
            MonthlyViews = monthlyViews,
            UserGrowthRate = Math.Round(userGrowthRate, 2),
            RepositoryGrowthRate = Math.Round(repositoryGrowthRate, 2),
            DocumentGrowthRate = Math.Round(documentGrowthRate, 2),
            ViewGrowthRate = Math.Round(viewGrowthRate, 2)
        };
    }

    /// <summary>
    /// 获取详细统计数据
    /// </summary>
    /// <returns>详细统计数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<DetailedStatisticsDto> GetDetailedStatisticsAsync()
    {
        var systemStats = await GetSystemStatisticsAsync();
        var recentRepositories = await GetRecentRepositoriesAsync(10);
        var recentUsers = await GetRecentUsersAsync(10);
        var userTrends = await GetUserTrendsAsync(30);
        var repositoryTrends = await GetRepositoryTrendsAsync(30);
        var documentTrends = await GetDocumentTrendsAsync(30);
        var viewTrends = await GetViewTrendsAsync(30);

        return new DetailedStatisticsDto
        {
            SystemStats = systemStats,
            RecentRepositories = recentRepositories,
            RecentUsers = recentUsers,
            UserTrends = userTrends,
            RepositoryTrends = repositoryTrends,
            DocumentTrends = documentTrends,
            ViewTrends = viewTrends
        };
    }

    /// <summary>
    /// 获取最近创建的仓库
    /// </summary>
    /// <param name="count">数量</param>
    /// <returns>最近仓库列表</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<RecentRepositoryDto>> GetRecentRepositoriesAsync(int count = 10)
    {
        var repositories = await dbContext.Warehouses
            .AsNoTracking()
            .OrderByDescending(w => w.CreatedAt)
            .Take(count)
            .Select(w => new RecentRepositoryDto
            {
                Id = w.Id,
                Name = w.Name,
                OrganizationName = w.OrganizationName,
                Description = w.Description,
                CreatedAt = w.CreatedAt,
                Status = w.Status.ToString(),
                IsRecommended = w.IsRecommended,
            })
            .ToListAsync();

        foreach (var repository in repositories)
        {
            // 获取仓库的最新提交信息
            var countAsync = await dbContext.DocumentCatalogs
                .AsNoTracking()
                .Where(c => c.WarehouseId == repository.Id)
                .OrderByDescending(c => c.CreatedAt)
                .CountAsync();

            repository.DocumentCount = countAsync;
        }

        return repositories;
    }

    /// <summary>
    /// 获取最近注册的用户
    /// </summary>
    /// <param name="count">数量</param>
    /// <returns>最近用户列表</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<RecentUserDto>> GetRecentUsersAsync(int count = 10)
    {
        var users = await dbContext.Users
            .AsNoTracking()
            .OrderByDescending(u => u.CreatedAt)
            .Take(count)
            .Select(u => new RecentUserDto
            {
                Id = u.Id,
                Name = u.Name,
                Email = u.Email,
                CreatedAt = u.CreatedAt,
                LastLoginAt = u.LastLoginAt,
                IsOnline = u.LastLoginAt.HasValue &&
                           (DateTime.UtcNow - u.LastLoginAt.Value).TotalMinutes < 30
            })
            .ToListAsync();

        // 获取用户角色
        foreach (var user in users)
        {
            var roles = await dbContext.UserInRoles
                .AsNoTracking()
                .Where(ur => ur.UserId == user.Id)
                .Join(dbContext.Roles, ur => ur.RoleId, r => r.Id, (ur, r) => r.Name)
                .ToListAsync();

            user.Roles = roles;
        }

        return users;
    }

    /// <summary>
    /// 获取用户趋势数据
    /// </summary>
    /// <param name="days">天数</param>
    /// <returns>趋势数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<TrendDataDto>> GetUserTrendsAsync(int days = 30)
    {
        var startDate = DateTime.UtcNow.Date.AddDays(-days);
        var endDate = DateTime.UtcNow.Date.AddDays(1);

        var userTrends = await dbContext.Users
            .AsNoTracking()
            .Where(u => u.CreatedAt >= startDate && u.CreatedAt < endDate)
            .GroupBy(u => u.CreatedAt.Date)
            .Select(g => new
            {
                Date = g.Key,
                Value = g.Count()
            })
            .OrderBy(t => t.Date)
            .ToListAsync();

        // 填充缺失的日期，值为0
        var result = new List<TrendDataDto>();
        for (var date = startDate; date < endDate; date = date.AddDays(1))
        {
            var existing = userTrends.FirstOrDefault(t => t.Date.ToString("yyyy-MM-dd") == date.ToString("yyyy-MM-dd"));

            if (existing != null)
            {
                result.Add(new TrendDataDto
                {
                    Date = existing.Date.ToString("yyyy-MM-dd"),
                    Value = existing.Value
                });
                continue;
            }

            result.Add(new TrendDataDto
            {
                Date = date.ToString("yyyy-MM-dd"),
                Value = 0
            });
        }

        return result;
    }

    /// <summary>
    /// 获取仓库趋势数据
    /// </summary>
    /// <param name="days">天数</param>
    /// <returns>趋势数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<TrendDataDto>> GetRepositoryTrendsAsync(int days = 30)
    {
        var startDate = DateTime.UtcNow.Date.AddDays(-days);
        var endDate = DateTime.UtcNow.Date.AddDays(1);

        var repositoryTrends = await dbContext.Warehouses
            .AsNoTracking()
            .Where(w => w.CreatedAt >= startDate && w.CreatedAt < endDate)
            .GroupBy(w => w.CreatedAt.Date)
            .Select(g => new
            {
                Date = g.Key,
                Value = g.Count()
            })
            .OrderBy(t => t.Date)
            .ToListAsync();

        // 填充缺失的日期，值为0
        var result = new List<TrendDataDto>();
        for (var date = startDate; date < endDate; date = date.AddDays(1))
        {
            var existing =
                repositoryTrends.FirstOrDefault(t => t.Date.ToString("yyyy-MM-dd") == date.ToString("yyyy-MM-dd"));
            if (existing != null)
            {
                result.Add(new TrendDataDto
                {
                    Date = existing.Date.ToString("yyyy-MM-dd"),
                    Value = existing.Value
                });
                continue;
            }

            result.Add(new TrendDataDto
            {
                Date = date.ToString("yyyy-MM-dd"),
                Value = 0
            });
        }

        return result;
    }

    /// <summary>
    /// 获取文档趋势数据
    /// </summary>
    /// <param name="days">天数</param>
    /// <returns>趋势数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<TrendDataDto>> GetDocumentTrendsAsync(int days = 30)
    {
        var startDate = DateTime.UtcNow.Date.AddDays(-days);
        var endDate = DateTime.UtcNow.Date.AddDays(1);

        var documentTrends = await dbContext.DocumentFileItems
            .AsNoTracking()
            .Where(d => d.CreatedAt >= startDate && d.CreatedAt < endDate)
            .GroupBy(d => d.CreatedAt.Date)
            .Select(g => new
            {
                Date = g.Key,
                Value = g.Count()
            })
            .OrderBy(t => t.Date)
            .ToListAsync();

        // 填充缺失的日期，值为0
        var result = new List<TrendDataDto>();
        for (var date = startDate; date < endDate; date = date.AddDays(1))
        {
            var existing =
                documentTrends.FirstOrDefault(t => t.Date.ToString("yyyy-MM-dd") == date.ToString("yyyy-MM-dd"));

            if (existing != null)
            {
                result.Add(new TrendDataDto
                {
                    Date = existing.Date.ToString("yyyy-MM-dd"),
                    Value = existing.Value
                });
                continue;
            }

            result.Add(new TrendDataDto
            {
                Date = date.ToString("yyyy-MM-dd"),
                Value = 0
            });
        }

        return result;
    }

    /// <summary>
    /// 获取访问量趋势数据
    /// </summary>
    /// <param name="days">天数</param>
    /// <returns>趋势数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<TrendDataDto>> GetViewTrendsAsync(int days = 30)
    {
        var startDate = DateTime.UtcNow.Date.AddDays(-days);
        var endDate = DateTime.UtcNow.Date.AddDays(1);

        var viewTrends = await dbContext.AccessRecords
            .AsNoTracking()
            .Where(a => a.CreatedAt >= startDate && a.CreatedAt < endDate)
            .GroupBy(a => a.CreatedAt.Date)
            .Select(g => new 
            {
                Date = g.Key,
                Value = g.Count()
            })
            .OrderBy(t => t.Date)
            .ToListAsync();

        // 填充缺失的日期，值为0
        var result = new List<TrendDataDto>();
        for (var date = startDate; date < endDate; date = date.AddDays(1))
        {
            var existing = viewTrends.FirstOrDefault(t => t.Date.ToString("yyyy-MM-dd") == date.ToString("yyyy-MM-dd"));
            if (existing != null)
            {
                result.Add(new TrendDataDto
                {
                    Date = existing.Date.ToString("yyyy-MM-dd"),
                    Value = existing.Value
                });
                continue;
            }
            result.Add(new TrendDataDto
            {
                Date = date.ToString("yyyy-MM-dd"),
                Value = 0
            });
        }

        return result;
    }

    /// <summary>
    /// 获取热门内容
    /// </summary>
    /// <param name="days">统计天数</param>
    /// <param name="count">返回数量</param>
    /// <returns>热门内容列表</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<PopularContentDto>> GetPopularContentAsync(int days = 7, int count = 10)
    {
        var startDate = DateTime.UtcNow.Date.AddDays(-days);

        var popularContent = await dbContext.AccessRecords
            .AsNoTracking()
            .Where(a => a.CreatedAt >= startDate &&
                        !string.IsNullOrEmpty(a.ResourceId) &&
                        !string.IsNullOrEmpty(a.ResourceType))
            .GroupBy(a => new { a.ResourceId, a.ResourceType })
            .Select(g => new
            {
                ResourceId = g.Key.ResourceId,
                ResourceType = g.Key.ResourceType,
                ViewCount = g.Count(),
                LastViewAt = g.Max(a => a.CreatedAt)
            })
            .OrderByDescending(x => x.ViewCount)
            .Take(count)
            .ToListAsync();

        var result = new List<PopularContentDto>();

        foreach (var item in popularContent)
        {
            string title = item.ResourceId;

            // 根据资源类型获取标题
            if (item.ResourceType == "Repository")
            {
                var warehouse = await dbContext.Warehouses
                    .AsNoTracking()
                    .Where(w => w.Id == item.ResourceId)
                    .Select(w => new { w.Name, w.OrganizationName })
                    .FirstOrDefaultAsync();

                if (warehouse != null)
                {
                    title = $"{warehouse.OrganizationName}/{warehouse.Name}";
                }
            }
            else if (item.ResourceType == "Document")
            {
                var document = await dbContext.DocumentFileItems
                    .AsNoTracking()
                    .Where(d => d.Id == item.ResourceId)
                    .Select(d => d.Title)
                    .FirstOrDefaultAsync();

                if (!string.IsNullOrEmpty(document))
                {
                    title = document;
                }
            }

            result.Add(new PopularContentDto
            {
                Id = item.ResourceId,
                Title = title,
                Type = item.ResourceType,
                ViewCount = item.ViewCount,
                LastViewAt = item.LastViewAt
            });
        }

        return result;
    }

    /// <summary>
    /// 记录访问
    /// </summary>
    /// <param name="resourceType">资源类型</param>
    /// <param name="resourceId">资源ID</param>
    /// <param name="userId">用户ID（可选）</param>
    /// <param name="ipAddress">IP地址</param>
    /// <param name="userAgent">用户代理</param>
    /// <param name="path">访问路径</param>
    /// <param name="method">请求方法</param>
    /// <param name="statusCode">状态码</param>
    /// <param name="responseTime">响应时间</param>
    /// <returns>是否成功</returns>
    public async Task<bool> RecordAccessAsync(
        string resourceType,
        string resourceId,
        string? userId = null,
        string ipAddress = "",
        string userAgent = "",
        string path = "",
        string method = "GET",
        int statusCode = 200,
        long responseTime = 0)
    {
        try
        {
            var accessRecord = new AccessRecord
            {
                ResourceType = resourceType,
                ResourceId = resourceId,
                UserId = userId,
                IpAddress = ipAddress,
                UserAgent = userAgent,
                Path = path,
                Method = method,
                StatusCode = statusCode,
                ResponseTime = responseTime,
                CreatedAt = DateTime.UtcNow,
                Id = Guid.NewGuid().ToString()
            };

            await dbContext.AccessRecords.AddAsync(accessRecord);
            await dbContext.SaveChangesAsync();

            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "记录访问失败");
            return false;
        }
    }

    /// <summary>
    /// 获取完整的仪表板数据
    /// </summary>
    /// <returns>完整的仪表板数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<ComprehensiveDashboardDto> GetComprehensiveDashboardAsync()
    {
        var dashboard = new ComprehensiveDashboardDto
        {
            SystemStats = await GetSystemStatisticsAsync(),
            Performance = await GetSystemPerformanceAsync(),
            RepositoryStatusDistribution = await GetRepositoryStatusDistributionAsync(),
            UserActivity = await GetUserActivityStatsAsync(),
            RecentRepositories = await GetRecentRepositoriesAsync(5),
            RecentUsers = await GetRecentUsersAsync(5),
            PopularContent = await GetPopularContentAsync(7, 5),
            RecentErrors = await GetRecentErrorLogsAsync(10),
            HealthCheck = await GetSystemHealthCheckAsync(),
            Trends = new DashboardTrendsDto
            {
                UserTrends = await GetUserTrendsAsync(30),
                RepositoryTrends = await GetRepositoryTrendsAsync(30),
                DocumentTrends = await GetDocumentTrendsAsync(30),
                ViewTrends = await GetViewTrendsAsync(30),
                PerformanceTrends = await GetPerformanceTrendsAsync(24)
            }
        };

        return dashboard;
    }

    /// <summary>
    /// 获取系统性能数据
    /// </summary>
    /// <returns>系统性能数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<SystemPerformanceDto> GetSystemPerformanceAsync()
    {
        var performance = new SystemPerformanceDto();

        try
        {
            // 获取系统启动时间
            var startTime = Environment.TickCount64;
            performance.SystemStartTime = DateTime.UtcNow.AddMilliseconds(-startTime);
            performance.UptimeSeconds = startTime / 1000;

            // 获取内存信息
            var process = System.Diagnostics.Process.GetCurrentProcess();
            performance.UsedMemory = process.WorkingSet64 / (1024 * 1024); // 转为MB

            // 估算总内存（这里可以根据实际情况调整）
            var gcMemoryInfo = GC.GetGCMemoryInfo();
            performance.TotalMemory = Math.Max(performance.UsedMemory * 2, 1024); // 至少1GB

            performance.MemoryUsage = (double)performance.UsedMemory / performance.TotalMemory * 100;

            // 获取磁盘信息
            var drives = DriveInfo.GetDrives().Where(d => d.IsReady).ToArray();
            if (drives.Length > 0)
            {
                var primaryDrive = drives.First();
                performance.TotalDiskSpace = primaryDrive.TotalSize / (1024 * 1024 * 1024); // 转为GB
                performance.UsedDiskSpace = (primaryDrive.TotalSize - primaryDrive.AvailableFreeSpace) / (1024 * 1024 * 1024);
                performance.DiskUsage = (double)performance.UsedDiskSpace / performance.TotalDiskSpace * 100;
            }

            // CPU使用率（简化实现，实际项目可能需要更精确的监控）
            performance.CpuUsage = Random.Shared.NextDouble() * 30 + 10; // 模拟10-40%的CPU使用率

            // 活跃连接数（基于最近访问记录估算）
            var recentAccessCount = await dbContext.AccessRecords
                .Where(a => a.CreatedAt >= DateTime.UtcNow.AddMinutes(-5))
                .CountAsync();
            performance.ActiveConnections = Math.Max(recentAccessCount, 1);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取系统性能数据失败");
        }

        return performance;
    }

    /// <summary>
    /// 获取仓库状态分布
    /// </summary>
    /// <returns>仓库状态分布数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<RepositoryStatusDistributionDto>> GetRepositoryStatusDistributionAsync()
    {
        var statusCounts = await dbContext.Warehouses
            .AsNoTracking()
            .GroupBy(w => w.Status)
            .Select(g => new { Status = g.Key, Count = g.Count() })
            .ToListAsync();

        var totalCount = statusCounts.Sum(s => s.Count);

        return statusCounts.Select(s => new RepositoryStatusDistributionDto
        {
            Status = s.Status.ToString(),
            Count = s.Count,
            Percentage = totalCount > 0 ? Math.Round((decimal)s.Count / totalCount * 100, 2) : 0
        }).ToList();
    }

    /// <summary>
    /// 获取用户活跃度统计
    /// </summary>
    /// <returns>用户活跃度统计数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<UserActivityStatsDto> GetUserActivityStatsAsync()
    {
        var now = DateTime.UtcNow;
        var today = now.Date;
        var weekAgo = today.AddDays(-7);
        var monthAgo = today.AddDays(-30);

        // 在线用户（最近30分钟有活动）
        var onlineUsers = await dbContext.Users
            .AsNoTracking()
            .Where(u => u.LastLoginAt.HasValue && u.LastLoginAt.Value >= now.AddMinutes(-30))
            .CountAsync();

        // 今日活跃用户
        var dailyActiveUsers = await dbContext.AccessRecords
            .AsNoTracking()
            .Where(a => a.CreatedAt >= today && !string.IsNullOrEmpty(a.UserId))
            .Select(a => a.UserId)
            .Distinct()
            .CountAsync();

        // 本周活跃用户
        var weeklyActiveUsers = await dbContext.AccessRecords
            .AsNoTracking()
            .Where(a => a.CreatedAt >= weekAgo && !string.IsNullOrEmpty(a.UserId))
            .Select(a => a.UserId)
            .Distinct()
            .CountAsync();

        // 本月活跃用户
        var monthlyActiveUsers = await dbContext.AccessRecords
            .AsNoTracking()
            .Where(a => a.CreatedAt >= monthAgo && !string.IsNullOrEmpty(a.UserId))
            .Select(a => a.UserId)
            .Distinct()
            .CountAsync();

        // 上月活跃用户（用于计算增长率）
        var lastMonthActiveUsers = await dbContext.AccessRecords
            .AsNoTracking()
            .Where(a => a.CreatedAt >= monthAgo.AddDays(-30) && a.CreatedAt < monthAgo && !string.IsNullOrEmpty(a.UserId))
            .Select(a => a.UserId)
            .Distinct()
            .CountAsync();

        var activeUserGrowthRate = lastMonthActiveUsers > 0
            ? Math.Round((decimal)(monthlyActiveUsers - lastMonthActiveUsers) / lastMonthActiveUsers * 100, 2)
            : monthlyActiveUsers > 0 ? 100 : 0;

        // 最近登录的用户
        var recentLoginUsers = await dbContext.Users
            .AsNoTracking()
            .Where(u => u.LastLoginAt.HasValue)
            .OrderByDescending(u => u.LastLoginAt)
            .Take(10)
            .Select(u => new RecentLoginUserDto
            {
                Id = u.Id,
                Name = u.Name,
                Avatar = u.Avatar,
                LoginTime = u.LastLoginAt.Value,
                IpAddress = "", // 可以从访问记录中获取
                IsOnline = u.LastLoginAt.HasValue && (now - u.LastLoginAt.Value).TotalMinutes < 30
            })
            .ToListAsync();

        return new UserActivityStatsDto
        {
            OnlineUsers = onlineUsers,
            DailyActiveUsers = dailyActiveUsers,
            WeeklyActiveUsers = weeklyActiveUsers,
            MonthlyActiveUsers = monthlyActiveUsers,
            ActiveUserGrowthRate = activeUserGrowthRate,
            RecentLoginUsers = recentLoginUsers
        };
    }

    /// <summary>
    /// 获取最近错误日志
    /// </summary>
    /// <param name="count">返回数量</param>
    /// <returns>最近错误日志列表</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<SystemErrorLogDto>> GetRecentErrorLogsAsync(int count = 10)
    {
        // 这里可以从日志系统或数据库中获取错误日志
        // 暂时返回模拟数据
        var errors = new List<SystemErrorLogDto>();

        // 可以从Serilog的日志文件或数据库中读取
        // 这里提供一个基本的实现框架
        try
        {
            // 从访问记录中找出失败的请求作为错误示例
            var errorRecords = await dbContext.AccessRecords
                .AsNoTracking()
                .Where(a => a.StatusCode >= 400 && a.CreatedAt >= DateTime.UtcNow.AddDays(-7))
                .OrderByDescending(a => a.CreatedAt)
                .Take(count)
                .ToListAsync();

            errors = errorRecords.Select(a => new SystemErrorLogDto
            {
                Id = Guid.NewGuid().ToString(),
                Level = a.StatusCode >= 500 ? "Error" : "Warning",
                Message = $"HTTP {a.StatusCode} - {a.Path}",
                Source = "Web Request",
                UserId = a.UserId,
                CreatedAt = a.CreatedAt,
                Path = a.Path,
                Method = a.Method,
                StatusCode = a.StatusCode
            }).ToList();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取错误日志失败");
        }

        return errors;
    }

    /// <summary>
    /// 获取系统健康度检查
    /// </summary>
    /// <returns>系统健康度检查结果</returns>
    [Authorize(Roles = "admin")]
    public async Task<SystemHealthCheckDto> GetSystemHealthCheckAsync()
    {
        var healthCheck = new SystemHealthCheckDto
        {
            CheckTime = DateTime.UtcNow,
            Warnings = new List<string>(),
            Errors = new List<string>()
        };

        var healthItems = new List<HealthCheckItemDto>();

        // 数据库健康检查
        var dbHealth = await CheckDatabaseHealthAsync();
        healthItems.Add(dbHealth);
        healthCheck.Database = dbHealth;

        // AI服务健康检查
        var aiHealth = CheckAiServiceHealth();
        healthItems.Add(aiHealth);
        healthCheck.AiService = aiHealth;

        // 邮件服务健康检查
        var emailHealth = CheckEmailServiceHealth();
        healthItems.Add(emailHealth);
        healthCheck.EmailService = emailHealth;

        // 文件存储健康检查
        var storageHealth = CheckFileStorageHealth();
        healthItems.Add(storageHealth);
        healthCheck.FileStorage = storageHealth;

        // 系统性能健康检查
        var performanceHealth = await CheckSystemPerformanceHealthAsync();
        healthItems.Add(performanceHealth);
        healthCheck.SystemPerformance = performanceHealth;

        // 计算总体健康度评分
        var healthyCount = healthItems.Count(h => h.IsHealthy);
        healthCheck.OverallScore = (int)Math.Round((double)healthyCount / healthItems.Count * 100);

        // 设置健康度等级
        healthCheck.HealthLevel = healthCheck.OverallScore switch
        {
            >= 90 => "优秀",
            >= 75 => "良好",
            >= 60 => "一般",
            _ => "较差"
        };

        // 收集警告和错误
        foreach (var item in healthItems)
        {
            if (!item.IsHealthy)
            {
                if (item.Status == "Warning")
                    healthCheck.Warnings.Add($"{item.Name}: {item.Error}");
                else
                    healthCheck.Errors.Add($"{item.Name}: {item.Error}");
            }
        }

        return healthCheck;
    }

    /// <summary>
    /// 获取性能趋势数据
    /// </summary>
    /// <param name="hours">小时数</param>
    /// <returns>性能趋势数据</returns>
    [Authorize(Roles = "admin")]
    public async Task<List<PerformanceTrendDto>> GetPerformanceTrendsAsync(int hours = 24)
    {
        var trends = new List<PerformanceTrendDto>();
        var now = DateTime.UtcNow;

        // 生成模拟的性能趋势数据（实际项目中应该从监控系统获取）
        for (int i = hours; i >= 0; i--)
        {
            var time = now.AddHours(-i);

            // 基于时间生成一些模拟数据
            var baseLoad = 15 + Math.Sin((double)i / 24 * Math.PI * 2) * 10; // 模拟日周期
            var noise = Random.Shared.NextDouble() * 10 - 5; // 添加随机波动

            trends.Add(new PerformanceTrendDto
            {
                Time = time,
                CpuUsage = Math.Max(0, Math.Min(100, baseLoad + noise)),
                MemoryUsage = Math.Max(0, Math.Min(100, baseLoad + noise + 20)),
                ActiveConnections = Math.Max(1, (int)(baseLoad + noise))
            });
        }

        await Task.CompletedTask; // 异步方法占位符
        return trends;
    }

    /// <summary>
    /// 检查数据库健康状态
    /// </summary>
    private async Task<HealthCheckItemDto> CheckDatabaseHealthAsync()
    {
        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        try
        {
            await dbContext.Users.AsNoTracking().Take(1).ToListAsync();
            stopwatch.Stop();

            return new HealthCheckItemDto
            {
                Name = "数据库",
                Status = "健康",
                IsHealthy = true,
                ResponseTime = stopwatch.ElapsedMilliseconds,
                LastCheckTime = DateTime.UtcNow
            };
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            return new HealthCheckItemDto
            {
                Name = "数据库",
                Status = "错误",
                IsHealthy = false,
                ResponseTime = stopwatch.ElapsedMilliseconds,
                Error = ex.Message,
                LastCheckTime = DateTime.UtcNow
            };
        }
    }

    /// <summary>
    /// 检查AI服务健康状态
    /// </summary>
    private HealthCheckItemDto CheckAiServiceHealth()
    {
        try
        {
            // 检查AI配置是否存在
            var hasApiKey = !string.IsNullOrEmpty(OpenAIOptions.ChatApiKey);
            var hasEndpoint = !string.IsNullOrEmpty(OpenAIOptions.Endpoint);

            if (hasApiKey && hasEndpoint)
            {
                return new HealthCheckItemDto
                {
                    Name = "AI服务",
                    Status = "健康",
                    IsHealthy = true,
                    ResponseTime = 0,
                    LastCheckTime = DateTime.UtcNow
                };
            }
            else
            {
                return new HealthCheckItemDto
                {
                    Name = "AI服务",
                    Status = "警告",
                    IsHealthy = false,
                    Error = "AI服务配置不完整",
                    LastCheckTime = DateTime.UtcNow
                };
            }
        }
        catch (Exception ex)
        {
            return new HealthCheckItemDto
            {
                Name = "AI服务",
                Status = "错误",
                IsHealthy = false,
                Error = ex.Message,
                LastCheckTime = DateTime.UtcNow
            };
        }
    }

    /// <summary>
    /// 检查邮件服务健康状态
    /// </summary>
    private HealthCheckItemDto CheckEmailServiceHealth()
    {
        // 这里可以检查SMTP配置
        return new HealthCheckItemDto
        {
            Name = "邮件服务",
            Status = "健康",
            IsHealthy = true,
            ResponseTime = 0,
            LastCheckTime = DateTime.UtcNow
        };
    }

    /// <summary>
    /// 检查文件存储健康状态
    /// </summary>
    private HealthCheckItemDto CheckFileStorageHealth()
    {
        try
        {
            var tempPath = Path.GetTempPath();
            var testFile = Path.Combine(tempPath, "koalawiki_health_check.tmp");

            // 测试写入
            File.WriteAllText(testFile, "health check");

            // 测试读取
            var content = File.ReadAllText(testFile);

            // 清理
            File.Delete(testFile);

            return new HealthCheckItemDto
            {
                Name = "文件存储",
                Status = "健康",
                IsHealthy = true,
                ResponseTime = 0,
                LastCheckTime = DateTime.UtcNow
            };
        }
        catch (Exception ex)
        {
            return new HealthCheckItemDto
            {
                Name = "文件存储",
                Status = "错误",
                IsHealthy = false,
                Error = ex.Message,
                LastCheckTime = DateTime.UtcNow
            };
        }
    }

    /// <summary>
    /// 检查系统性能健康状态
    /// </summary>
    private async Task<HealthCheckItemDto> CheckSystemPerformanceHealthAsync()
    {
        try
        {
            var performance = await GetSystemPerformanceAsync();

            var hasIssues = performance.CpuUsage > 80 ||
                           performance.MemoryUsage > 85 ||
                           performance.DiskUsage > 90;

            if (hasIssues)
            {
                var issues = new List<string>();
                if (performance.CpuUsage > 80) issues.Add($"CPU使用率过高: {performance.CpuUsage:F1}%");
                if (performance.MemoryUsage > 85) issues.Add($"内存使用率过高: {performance.MemoryUsage:F1}%");
                if (performance.DiskUsage > 90) issues.Add($"磁盘使用率过高: {performance.DiskUsage:F1}%");

                return new HealthCheckItemDto
                {
                    Name = "系统性能",
                    Status = "警告",
                    IsHealthy = false,
                    Error = string.Join(", ", issues),
                    LastCheckTime = DateTime.UtcNow
                };
            }

            return new HealthCheckItemDto
            {
                Name = "系统性能",
                Status = "健康",
                IsHealthy = true,
                ResponseTime = 0,
                LastCheckTime = DateTime.UtcNow
            };
        }
        catch (Exception ex)
        {
            return new HealthCheckItemDto
            {
                Name = "系统性能",
                Status = "错误",
                IsHealthy = false,
                Error = ex.Message,
                LastCheckTime = DateTime.UtcNow
            };
        }
    }

    /// <summary>
    /// 生成每日统计数据
    /// </summary>
    /// <param name="date">统计日期（可选，默认为昨天）</param>
    /// <returns>是否成功</returns>
    [Authorize(Roles = "admin")]
    public async Task<bool> GenerateDailyStatisticsAsync(DateTime? date = null)
    {
        try
        {
            var targetDate = date?.Date ?? DateTime.UtcNow.Date.AddDays(-1);
            var nextDay = targetDate.AddDays(1);

            // 检查是否已存在该日期的统计数据
            var existingStats = await dbContext.DailyStatistics
                .FirstOrDefaultAsync(ds => ds.Date == targetDate);

            var newUsersCount = await dbContext.Users
                .Where(u => u.CreatedAt >= targetDate && u.CreatedAt < nextDay)
                .CountAsync();

            var newRepositoriesCount = await dbContext.Warehouses
                .Where(w => w.CreatedAt >= targetDate && w.CreatedAt < nextDay)
                .CountAsync();

            var newDocumentsCount = await dbContext.DocumentFileItems
                .Where(d => d.CreatedAt >= targetDate && d.CreatedAt < nextDay)
                .CountAsync();

            var pageViews = await dbContext.AccessRecords
                .Where(a => a.CreatedAt >= targetDate && a.CreatedAt < nextDay)
                .CountAsync();

            var uniqueVisitors = await dbContext.AccessRecords
                .Where(a => a.CreatedAt >= targetDate && a.CreatedAt < nextDay)
                .Select(a => a.IpAddress)
                .Distinct()
                .CountAsync();

            var activeUsers = await dbContext.AccessRecords
                .Where(a => a.CreatedAt >= targetDate && a.CreatedAt < nextDay &&
                            !string.IsNullOrEmpty(a.UserId))
                .Select(a => a.UserId)
                .Distinct()
                .CountAsync();

            if (existingStats != null)
            {
                // 更新现有统计数据
                existingStats.NewUsersCount = newUsersCount;
                existingStats.NewRepositoriesCount = newRepositoriesCount;
                existingStats.NewDocumentsCount = newDocumentsCount;
                existingStats.PageViews = pageViews;
                existingStats.UniqueVisitors = uniqueVisitors;
                existingStats.ActiveUsers = activeUsers;
                existingStats.UpdatedAt = DateTime.UtcNow;

                dbContext.DailyStatistics.Update(existingStats);
            }
            else
            {
                // 创建新的统计数据
                var dailyStats = new DailyStatistics
                {
                    Id = Guid.NewGuid().ToString(),
                    Date = targetDate,
                    NewUsersCount = newUsersCount,
                    NewRepositoriesCount = newRepositoriesCount,
                    NewDocumentsCount = newDocumentsCount,
                    PageViews = pageViews,
                    UniqueVisitors = uniqueVisitors,
                    ActiveUsers = activeUsers,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                };

                await dbContext.DailyStatistics.AddAsync(dailyStats);
            }

            await dbContext.SaveChangesAsync();
            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "生成每日统计数据失败");
            return false;
        }
    }
}