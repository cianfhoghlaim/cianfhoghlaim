using KoalaWiki.Entities;

namespace KoalaWiki.Domains.Warehouse;

public class Warehouse : Entity<string>
{
    /// <summary>
    /// 组织名称
    /// </summary>
    /// <returns></returns>
    public string OrganizationName { get; set; } = string.Empty;

    /// <summary>
    /// 仓库名称
    /// </summary>
    public string Name { get; set; }

    /// <summary>
    /// 仓库描述
    /// </summary>
    public string Description { get; set; }

    /// <summary>
    /// 仓库地址
    /// </summary>
    /// <returns></returns>
    public string Address { get; set; }

    /// <summary>
    /// 私有化git账号
    /// </summary>
    public string? GitUserName { get; set; }

    /// <summary>
    /// 私有化git密码
    /// </summary>
    public string? GitPassword { get; set; }

    /// <summary>
    ///  私有化git邮箱
    /// </summary>
    public string? Email { get; set; }

    /// <summary>
    /// 仓库类型
    /// </summary>
    public string? Type { get; set; }

    /// <summary>
    /// 仓库分支
    /// </summary>
    public string? Branch { get; set; }

    /// <summary>
    /// 仓库状态
    /// </summary>
    public WarehouseStatus Status { get; set; }

    /// <summary>
    /// 错误信息
    /// </summary>
    public string? Error { get; set; }

    /// <summary>
    /// 仓库版本
    /// </summary>
    public string? Version { get; set; }
    
    /// <summary>
    /// 是否嵌入完成
    /// </summary>
    public bool IsEmbedded { get; set; }
    
    /// <summary>
    /// 是否推荐
    /// </summary>
    /// <returns></returns>
    public bool IsRecommended { get; set; }

    /// <summary>
    /// 仓库类别
    /// </summary>
    public ClassifyType? Classify { get; set; }
    
    /// <summary>
    /// Star数量
    /// </summary>
    public int Stars { get; set; }
    
    /// <summary>
    /// Fork数量
    /// </summary>
    public int Forks { get; set; }
    
    /// <summary>
    /// 创建用户id
    /// </summary>
    public string? UserId { get; set; }

    /// <summary>
    /// 是否启用同步
    /// </summary>
    public bool EnableSync { get; set; }
}