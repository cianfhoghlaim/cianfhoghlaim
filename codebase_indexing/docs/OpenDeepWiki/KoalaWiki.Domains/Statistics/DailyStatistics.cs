using System;
using KoalaWiki.Entities;

namespace KoalaWiki.Domains.Statistics;

/// <summary>
/// 每日统计实体
/// </summary>
public class DailyStatistics : Entity<string>
{
    /// <summary>
    /// 统计日期
    /// </summary>
    public DateTime Date { get; set; }

    /// <summary>
    /// 新增用户数
    /// </summary>
    public int NewUsersCount { get; set; }

    /// <summary>
    /// 新增仓库数
    /// </summary>
    public int NewRepositoriesCount { get; set; }

    /// <summary>
    /// 新增文档数
    /// </summary>
    public int NewDocumentsCount { get; set; }

    /// <summary>
    /// 页面访问量
    /// </summary>
    public int PageViews { get; set; }

    /// <summary>
    /// 独立访问用户数
    /// </summary>
    public int UniqueVisitors { get; set; }

    /// <summary>
    /// 活跃用户数
    /// </summary>
    public int ActiveUsers { get; set; }

    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; }
}