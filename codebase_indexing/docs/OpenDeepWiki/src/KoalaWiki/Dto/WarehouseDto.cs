using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Entities;

namespace KoalaWiki.Dto;

public class WarehouseDto 
{
    public string Id { get; set; } 
    
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
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; }
    
    /// <summary>
    /// 仓库状态
    /// </summary>
    public WarehouseStatus Status { get; set; }

    /// <summary>
    /// 错误信息
    /// </summary>
    public string? Error { get; set; }

    /// <summary>
    /// 构建提示词
    /// </summary>
    public string? Prompt { get; set; }

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
    /// 优化过的代码目录结构
    /// </summary>
    /// <returns></returns>
    public string? OptimizedDirectoryStructure { get; set; }
    
    /// <summary>
    /// 当前仓库的文档（默认使用仓库，如果没有则动态生成）
    /// </summary>
    public string? Readme { get; set; } 
    
    public int Stars { get; set; }

    public int Forks { get; set; }

    public bool Success { get; set; }

    public string AvatarUrl { get; set; } = string.Empty;

    public string OwnerUrl { get; set; } = string.Empty;

    public string RepoUrl { get; set; } = string.Empty;

    public string? Language { get; set; }

    public string? License { get; set; }
}