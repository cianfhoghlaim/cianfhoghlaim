using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace KoalaWiki.Domains;

/// <summary>
/// 应用配置实体
/// </summary>
public class AppConfig : Entity<string>
{
    /// <summary>
    /// 应用ID（唯一标识）
    /// </summary>
    [Required]
    [StringLength(64)]
    public string AppId { get; set; } = string.Empty;

    /// <summary>
    /// 应用名称
    /// </summary>
    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 组织名称
    /// </summary>
    [Required]
    [StringLength(100)]
    public string OrganizationName { get; set; } = string.Empty;

    /// <summary>
    /// 仓库名称
    /// </summary>
    [Required]
    [StringLength(100)]
    public string RepositoryName { get; set; } = string.Empty;

    /// <summary>
    /// 允许的域名列表（JSON 格式存储）
    /// </summary>
    public string AllowedDomainsJson { get; set; } = "[]";

    /// <summary>
    /// 是否启用域名验证
    /// </summary>
    public bool EnableDomainValidation { get; set; } = false;

    /// <summary>
    /// 应用描述
    /// </summary>
    [StringLength(500)]
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// 创建用户ID
    /// </summary>
    [Required]
    public string UserId { get; set; } = string.Empty;

    /// <summary>
    /// 是否启用
    /// </summary>
    public bool IsEnabled { get; set; } = true;

    /// <summary>
    /// 最后使用时间
    /// </summary>
    public DateTime? LastUsedAt { get; set; }

    /// <summary>
    /// 默认提示词
    /// </summary>
    public string? Prompt { get; set; }

    /// <summary>
    /// 开场白
    /// </summary>
    /// <returns></returns>
    public string? Introduction { get; set; }

    /// <summary>
    /// 选择模型
    /// </summary>
    public string? Model { get; set; }

    /// <summary>
    /// 设置推荐提问
    /// </summary>
    /// <returns></returns>
    public List<string>? RecommendedQuestions { get; set; }

    public List<AppConfigMcp> Mcps { get; set; } = new();
}

public class AppConfigMcp
{
    public string Url { get; set; }

    public Dictionary<string, string> Headers { get; set; } = new Dictionary<string, string>();
}