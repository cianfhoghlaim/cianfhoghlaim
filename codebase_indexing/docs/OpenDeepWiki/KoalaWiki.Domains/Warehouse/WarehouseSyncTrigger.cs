namespace KoalaWiki.Domains.Warehouse;

/// <summary>
/// 仓库同步触发方式
/// </summary>
public enum WarehouseSyncTrigger
{
    /// <summary>
    /// 自动触发
    /// </summary>
    Auto = 0,

    /// <summary>
    /// 手动触发
    /// </summary>
    Manual = 1
}