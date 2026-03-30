using System.ComponentModel.DataAnnotations;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Entities;

namespace KoalaWiki.Dto;

/// <summary>
/// 仓库创建DTO（Git仓库）
/// </summary>
public class CreateGitRepositoryDto
{
    /// <summary>
    /// 仓库地址
    /// </summary>
    [Required(ErrorMessage = "仓库地址不能为空")]
    public string Address { get; set; } = string.Empty;

    /// <summary>
    /// 分支
    /// </summary>
    public string Branch { get; set; } = string.Empty;

    /// <summary>
    /// 私有化git账号
    /// </summary>
    public string? GitUserName { get; set; }

    /// <summary>
    /// 私有化git密码
    /// </summary>
    public string? GitPassword { get; set; }

    /// <summary>
    /// 私有化git邮箱
    /// </summary>
    public string? Email { get; set; }
}

/// <summary>
/// 仓库创建DTO（上传压缩包）
/// </summary>
public class CreateFileRepositoryDto
{
    /// <summary>
    /// 组织名称
    /// </summary>
    [Required(ErrorMessage = "组织名称不能为空")]
    public string Organization { get; set; } = string.Empty;

    /// <summary>
    /// 仓库名称
    /// </summary>
    [Required(ErrorMessage = "仓库名称不能为空")]
    public string RepositoryName { get; set; } = string.Empty;
}

/// <summary>
/// 仓库信息DTO（返回给前端）
/// </summary>
public class RepositoryInfoDto
{
    /// <summary>
    /// 仓库ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 组织名称
    /// </summary>
    public string OrganizationName { get; set; } = string.Empty;

    /// <summary>
    /// 仓库名称
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 仓库描述
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// 仓库地址
    /// </summary>
    public string Address { get; set; } = string.Empty;

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
    public bool IsRecommended { get; set; }

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; }
}

/// <summary>
/// 仓库更新DTO
/// </summary>
public class UpdateRepositoryDto
{
    /// <summary>
    /// 仓库描述
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// 是否推荐
    /// </summary>
    public bool? IsRecommended { get; set; }

    /// <summary>
    /// 构建提示词
    /// </summary>
    public string? Prompt { get; set; }
}

/// <summary>
/// 仓库统计信息DTO
/// </summary>
public class RepositoryStatsDto
{
    public int TotalDocuments { get; set; }
    public int CompletedDocuments { get; set; }
    public int PendingDocuments { get; set; }
    public int TotalFiles { get; set; }
    public DateTime? LastSyncTime { get; set; }
    public string ProcessingStatus { get; set; } = "Pending";
}

/// <summary>
/// 仓库操作日志DTO
/// </summary>
public class RepositoryLogDto
{
    public string Id { get; set; } = string.Empty;
    public string RepositoryId { get; set; } = string.Empty;
    public string Operation { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string UserName { get; set; } = string.Empty;
    public bool Success { get; set; }
    public string? Error { get; set; }
    public DateTime CreatedAt { get; set; }
}

/// <summary>
/// 批量操作DTO
/// </summary>
public class BatchOperationDto
{
    public List<string> Ids { get; set; } = new List<string>();
    public string Operation { get; set; } = string.Empty;
}

/// <summary>
/// 文档目录DTO
/// </summary>
public class DocumentCatalogDto
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Url { get; set; }
    public string? Prompt { get; set; }
    public string? ParentId { get; set; }
    public int Order { get; set; }
    public string WarehouseId { get; set; } = string.Empty;
    public bool IsCompleted { get; set; }
    public DateTime CreatedAt { get; set; }
}