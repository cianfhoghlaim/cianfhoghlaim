namespace KoalaWiki.Domains.Warehouse;

/// <summary>
/// 表示仓库与角色的权限关系。
/// </summary>
public class WarehouseInRole
{
    /// <summary>
    /// 仓库ID。
    /// </summary>
    public string WarehouseId { get; set; } = null!;

    /// <summary>
    /// 角色ID。
    /// </summary>
    public string RoleId { get; set; } = null!;

    /// <summary>
    /// 是否只读权限。
    /// </summary>
    public bool IsReadOnly { get; set; } = false;

    /// <summary>
    /// 是否有写入权限。
    /// </summary>
    public bool IsWrite { get; set; } = false;

    /// <summary>
    /// 是否有删除权限。
    /// </summary>
    public bool IsDelete { get; set; } = false;
}