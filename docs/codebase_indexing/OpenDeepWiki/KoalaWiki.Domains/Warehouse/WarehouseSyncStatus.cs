namespace KoalaWiki.Domains.Warehouse;

/// <summary>
/// 仓库同步状态
/// </summary>
public enum WarehouseSyncStatus
{
    /// <summary>
    /// 同步中
    /// </summary>
    InProgress = 0,

    /// <summary>
    /// 同步成功
    /// </summary>
    Success = 1,

    /// <summary>
    /// 同步失败
    /// </summary>
    Failed = 2
}