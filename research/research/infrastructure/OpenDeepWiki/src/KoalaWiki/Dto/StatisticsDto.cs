namespace KoalaWiki.Dto;

/// <summary>
/// 系统统计数据DTO
/// </summary>
public class SystemStatisticsDto
{
    /// <summary>
    /// 总用户数
    /// </summary>
    public int TotalUsers { get; set; }

    /// <summary>
    /// 总仓库数
    /// </summary>
    public int TotalRepositories { get; set; }

    /// <summary>
    /// 总文档数
    /// </summary>
    public int TotalDocuments { get; set; }

    /// <summary>
    /// 总访问量
    /// </summary>
    public long TotalViews { get; set; }

    /// <summary>
    /// 本月新增用户数
    /// </summary>
    public int MonthlyNewUsers { get; set; }

    /// <summary>
    /// 本月新增仓库数
    /// </summary>
    public int MonthlyNewRepositories { get; set; }

    /// <summary>
    /// 本月新增文档数
    /// </summary>
    public int MonthlyNewDocuments { get; set; }

    /// <summary>
    /// 本月访问量
    /// </summary>
    public long MonthlyViews { get; set; }

    /// <summary>
    /// 用户增长率
    /// </summary>
    public decimal UserGrowthRate { get; set; }

    /// <summary>
    /// 仓库增长率
    /// </summary>
    public decimal RepositoryGrowthRate { get; set; }

    /// <summary>
    /// 文档增长率
    /// </summary>
    public decimal DocumentGrowthRate { get; set; }

    /// <summary>
    /// 访问量增长率
    /// </summary>
    public decimal ViewGrowthRate { get; set; }
}

/// <summary>
/// 最近仓库信息DTO
/// </summary>
public class RecentRepositoryDto
{
    /// <summary>
    /// 仓库ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 仓库名称
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 组织名称
    /// </summary>
    public string OrganizationName { get; set; } = string.Empty;

    /// <summary>
    /// 描述
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// 状态
    /// </summary>
    public string Status { get; set; } = string.Empty;

    /// <summary>
    /// 是否推荐
    /// </summary>
    public bool IsRecommended { get; set; }

    /// <summary>
    /// 文档数量
    /// </summary>
    public int DocumentCount { get; set; }
}

/// <summary>
/// 最近用户信息DTO
/// </summary>
public class RecentUserDto
{
    /// <summary>
    /// 用户ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 用户名
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 邮箱
    /// </summary>
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// 最后登录时间
    /// </summary>
    public DateTime? LastLoginAt { get; set; }

    /// <summary>
    /// 角色
    /// </summary>
    public List<string> Roles { get; set; } = new List<string>();

    /// <summary>
    /// 是否在线
    /// </summary>
    public bool IsOnline { get; set; }
}

/// <summary>
/// 趋势数据DTO
/// </summary>
public class TrendDataDto
{
    /// <summary>
    /// 日期
    /// </summary>
    public string Date { get; set; } = string.Empty;

    /// <summary>
    /// 数值
    /// </summary>
    public long Value { get; set; }
}

/// <summary>
/// 详细统计数据DTO
/// </summary>
public class DetailedStatisticsDto
{
    /// <summary>
    /// 系统统计数据
    /// </summary>
    public SystemStatisticsDto SystemStats { get; set; } = new();

    /// <summary>
    /// 最近创建的仓库
    /// </summary>
    public List<RecentRepositoryDto> RecentRepositories { get; set; } = new();

    /// <summary>
    /// 最近注册的用户
    /// </summary>
    public List<RecentUserDto> RecentUsers { get; set; } = new();

    /// <summary>
    /// 用户趋势数据（最近30天）
    /// </summary>
    public List<TrendDataDto> UserTrends { get; set; } = new();

    /// <summary>
    /// 仓库趋势数据（最近30天）
    /// </summary>
    public List<TrendDataDto> RepositoryTrends { get; set; } = new();

    /// <summary>
    /// 文档趋势数据（最近30天）
    /// </summary>
    public List<TrendDataDto> DocumentTrends { get; set; } = new();

    /// <summary>
    /// 访问量趋势数据（最近30天）
    /// </summary>
    public List<TrendDataDto> ViewTrends { get; set; } = new();
}

/// <summary>
/// 热门内容DTO
/// </summary>
public class PopularContentDto
{
    /// <summary>
    /// 内容ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 内容标题
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// 内容类型
    /// </summary>
    public string Type { get; set; } = string.Empty;

    /// <summary>
    /// 访问次数
    /// </summary>
    public long ViewCount { get; set; }

    /// <summary>
    /// 最后访问时间
    /// </summary>
    public DateTime LastViewAt { get; set; }
}

/// <summary>
/// 系统性能监控DTO
/// </summary>
public class SystemPerformanceDto
{
    /// <summary>
    /// CPU使用率（百分比）
    /// </summary>
    public double CpuUsage { get; set; }

    /// <summary>
    /// 内存使用率（百分比）
    /// </summary>
    public double MemoryUsage { get; set; }

    /// <summary>
    /// 磁盘使用率（百分比）
    /// </summary>
    public double DiskUsage { get; set; }

    /// <summary>
    /// 总内存（MB）
    /// </summary>
    public long TotalMemory { get; set; }

    /// <summary>
    /// 已使用内存（MB）
    /// </summary>
    public long UsedMemory { get; set; }

    /// <summary>
    /// 总磁盘空间（GB）
    /// </summary>
    public long TotalDiskSpace { get; set; }

    /// <summary>
    /// 已使用磁盘空间（GB）
    /// </summary>
    public long UsedDiskSpace { get; set; }

    /// <summary>
    /// 系统启动时间
    /// </summary>
    public DateTime SystemStartTime { get; set; }

    /// <summary>
    /// 系统运行时间（秒）
    /// </summary>
    public long UptimeSeconds { get; set; }

    /// <summary>
    /// 活跃连接数
    /// </summary>
    public int ActiveConnections { get; set; }
}

/// <summary>
/// 仓库状态分布DTO
/// </summary>
public class RepositoryStatusDistributionDto
{
    /// <summary>
    /// 状态名称
    /// </summary>
    public string Status { get; set; } = string.Empty;

    /// <summary>
    /// 数量
    /// </summary>
    public int Count { get; set; }

    /// <summary>
    /// 百分比
    /// </summary>
    public decimal Percentage { get; set; }
}

/// <summary>
/// 用户活跃度统计DTO
/// </summary>
public class UserActivityStatsDto
{
    /// <summary>
    /// 在线用户数
    /// </summary>
    public int OnlineUsers { get; set; }

    /// <summary>
    /// 今日活跃用户数
    /// </summary>
    public int DailyActiveUsers { get; set; }

    /// <summary>
    /// 本周活跃用户数
    /// </summary>
    public int WeeklyActiveUsers { get; set; }

    /// <summary>
    /// 本月活跃用户数
    /// </summary>
    public int MonthlyActiveUsers { get; set; }

    /// <summary>
    /// 活跃用户增长率
    /// </summary>
    public decimal ActiveUserGrowthRate { get; set; }

    /// <summary>
    /// 最近登录的用户
    /// </summary>
    public List<RecentLoginUserDto> RecentLoginUsers { get; set; } = new();
}

/// <summary>
/// 最近登录用户DTO
/// </summary>
public class RecentLoginUserDto
{
    /// <summary>
    /// 用户ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 用户名
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 头像
    /// </summary>
    public string? Avatar { get; set; }

    /// <summary>
    /// 登录时间
    /// </summary>
    public DateTime LoginTime { get; set; }

    /// <summary>
    /// IP地址
    /// </summary>
    public string? IpAddress { get; set; }

    /// <summary>
    /// 是否在线
    /// </summary>
    public bool IsOnline { get; set; }
}

/// <summary>
/// 系统错误日志DTO
/// </summary>
public class SystemErrorLogDto
{
    /// <summary>
    /// 日志ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 错误级别
    /// </summary>
    public string Level { get; set; } = string.Empty;

    /// <summary>
    /// 错误消息
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// 错误来源
    /// </summary>
    public string Source { get; set; } = string.Empty;

    /// <summary>
    /// 用户ID
    /// </summary>
    public string? UserId { get; set; }

    /// <summary>
    /// 用户名
    /// </summary>
    public string? UserName { get; set; }

    /// <summary>
    /// 发生时间
    /// </summary>
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// 异常详情
    /// </summary>
    public string? Exception { get; set; }

    /// <summary>
    /// 请求路径
    /// </summary>
    public string? Path { get; set; }

    /// <summary>
    /// HTTP方法
    /// </summary>
    public string? Method { get; set; }

    /// <summary>
    /// 状态码
    /// </summary>
    public int? StatusCode { get; set; }
}

/// <summary>
/// 系统健康度检查DTO
/// </summary>
public class SystemHealthCheckDto
{
    /// <summary>
    /// 总体健康度评分（0-100）
    /// </summary>
    public int OverallScore { get; set; }

    /// <summary>
    /// 健康度等级
    /// </summary>
    public string HealthLevel { get; set; } = string.Empty;

    /// <summary>
    /// 数据库连接状态
    /// </summary>
    public HealthCheckItemDto Database { get; set; } = new();

    /// <summary>
    /// AI服务状态
    /// </summary>
    public HealthCheckItemDto AiService { get; set; } = new();

    /// <summary>
    /// 邮件服务状态
    /// </summary>
    public HealthCheckItemDto EmailService { get; set; } = new();

    /// <summary>
    /// 文件存储状态
    /// </summary>
    public HealthCheckItemDto FileStorage { get; set; } = new();

    /// <summary>
    /// 系统性能状态
    /// </summary>
    public HealthCheckItemDto SystemPerformance { get; set; } = new();

    /// <summary>
    /// 检查时间
    /// </summary>
    public DateTime CheckTime { get; set; }

    /// <summary>
    /// 警告消息
    /// </summary>
    public List<string> Warnings { get; set; } = new();

    /// <summary>
    /// 错误消息
    /// </summary>
    public List<string> Errors { get; set; } = new();
}

/// <summary>
/// 健康检查项DTO
/// </summary>
public class HealthCheckItemDto
{
    /// <summary>
    /// 服务名称
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 状态
    /// </summary>
    public string Status { get; set; } = string.Empty;

    /// <summary>
    /// 是否健康
    /// </summary>
    public bool IsHealthy { get; set; }

    /// <summary>
    /// 响应时间（毫秒）
    /// </summary>
    public long ResponseTime { get; set; }

    /// <summary>
    /// 错误消息
    /// </summary>
    public string? Error { get; set; }

    /// <summary>
    /// 最后检查时间
    /// </summary>
    public DateTime LastCheckTime { get; set; }
}

/// <summary>
/// 完整的仪表板数据DTO
/// </summary>
public class ComprehensiveDashboardDto
{
    /// <summary>
    /// 系统统计数据
    /// </summary>
    public SystemStatisticsDto SystemStats { get; set; } = new();

    /// <summary>
    /// 系统性能数据
    /// </summary>
    public SystemPerformanceDto Performance { get; set; } = new();

    /// <summary>
    /// 仓库状态分布
    /// </summary>
    public List<RepositoryStatusDistributionDto> RepositoryStatusDistribution { get; set; } = new();

    /// <summary>
    /// 用户活跃度统计
    /// </summary>
    public UserActivityStatsDto UserActivity { get; set; } = new();

    /// <summary>
    /// 最近创建的仓库
    /// </summary>
    public List<RecentRepositoryDto> RecentRepositories { get; set; } = new();

    /// <summary>
    /// 最近注册的用户
    /// </summary>
    public List<RecentUserDto> RecentUsers { get; set; } = new();

    /// <summary>
    /// 热门内容
    /// </summary>
    public List<PopularContentDto> PopularContent { get; set; } = new();

    /// <summary>
    /// 最近错误日志
    /// </summary>
    public List<SystemErrorLogDto> RecentErrors { get; set; } = new();

    /// <summary>
    /// 系统健康度检查
    /// </summary>
    public SystemHealthCheckDto HealthCheck { get; set; } = new();

    /// <summary>
    /// 趋势数据
    /// </summary>
    public DashboardTrendsDto Trends { get; set; } = new();
}

/// <summary>
/// 仪表板趋势数据DTO
/// </summary>
public class DashboardTrendsDto
{
    /// <summary>
    /// 用户趋势数据（最近30天）
    /// </summary>
    public List<TrendDataDto> UserTrends { get; set; } = new();

    /// <summary>
    /// 仓库趋势数据（最近30天）
    /// </summary>
    public List<TrendDataDto> RepositoryTrends { get; set; } = new();

    /// <summary>
    /// 文档趋势数据（最近30天）
    /// </summary>
    public List<TrendDataDto> DocumentTrends { get; set; } = new();

    /// <summary>
    /// 访问量趋势数据（最近30天）
    /// </summary>
    public List<TrendDataDto> ViewTrends { get; set; } = new();

    /// <summary>
    /// 性能趋势数据（最近24小时）
    /// </summary>
    public List<PerformanceTrendDto> PerformanceTrends { get; set; } = new();
}

/// <summary>
/// 性能趋势数据DTO
/// </summary>
public class PerformanceTrendDto
{
    /// <summary>
    /// 时间点
    /// </summary>
    public DateTime Time { get; set; }

    /// <summary>
    /// CPU使用率
    /// </summary>
    public double CpuUsage { get; set; }

    /// <summary>
    /// 内存使用率
    /// </summary>
    public double MemoryUsage { get; set; }

    /// <summary>
    /// 活跃连接数
    /// </summary>
    public int ActiveConnections { get; set; }
} 