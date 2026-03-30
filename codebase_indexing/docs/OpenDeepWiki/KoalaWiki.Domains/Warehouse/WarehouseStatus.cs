namespace KoalaWiki.Domains.Warehouse;

public enum WarehouseStatus : byte
{
    /// <summary>
    /// 待处理
    /// </summary>
    Pending = 0,

    /// <summary>
    /// 处理中
    /// </summary>
    Processing = 1,

    /// <summary>
    /// 已完成
    /// </summary>
    Completed = 2,

    /// <summary>
    /// 已取消
    /// </summary>
    Canceled = 3,

    /// <summary>
    /// 未授权
    /// </summary>
    Unauthorized = 4,

    /// <summary>
    /// 已失败
    //// </summary>
    Failed = 99
}