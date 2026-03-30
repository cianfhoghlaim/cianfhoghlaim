using System;
using KoalaWiki.Entities;

namespace KoalaWiki.Domains.Warehouse;

/// <summary>
/// 仓库同步记录
/// </summary>
public class WarehouseSyncRecord : Entity<string>
{
    /// <summary>
    /// 仓库ID
    /// </summary>
    public string WarehouseId { get; set; } = string.Empty;

    /// <summary>
    /// 同步状态 (Success, Failed, InProgress)
    /// </summary>
    public WarehouseSyncStatus Status { get; set; }

    /// <summary>
    /// 同步开始时间
    /// </summary>
    public DateTime StartTime { get; set; }

    /// <summary>
    /// 同步结束时间
    /// </summary>
    public DateTime? EndTime { get; set; }

    /// <summary>
    /// 同步前的版本
    /// </summary>
    public string? FromVersion { get; set; }

    /// <summary>
    /// 同步后的版本
    /// </summary>
    public string? ToVersion { get; set; }

    /// <summary>
    /// 错误信息
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// 同步的文件数量
    /// </summary>
    public int FileCount { get; set; }

    /// <summary>
    /// 更新的文件数量
    /// </summary>
    public int UpdatedFileCount { get; set; }

    /// <summary>
    /// 新增的文件数量
    /// </summary>
    public int AddedFileCount { get; set; }

    /// <summary>
    /// 删除的文件数量
    /// </summary>
    public int DeletedFileCount { get; set; }

    /// <summary>
    /// 同步触发方式 (Auto, Manual)
    /// </summary>
    public WarehouseSyncTrigger Trigger { get; set; }

    /// <summary>
    /// 关联的仓库
    /// </summary>
    public virtual Warehouse? Warehouse { get; set; }
}