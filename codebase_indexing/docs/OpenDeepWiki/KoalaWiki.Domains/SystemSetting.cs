using System;
using System.ComponentModel.DataAnnotations;

namespace KoalaWiki.Domains;

/// <summary>
/// 系统设置实体 - 用于存储系统级配置
/// </summary>
public class SystemSetting : Entity<string>
{
    /// <summary>
    /// 设置键名（唯一标识）
    /// </summary>
    [Required]
    [StringLength(100)]
    public string Key { get; set; } = string.Empty;

    /// <summary>
    /// 设置值
    /// </summary>
    public string? Value { get; set; }

    /// <summary>
    /// 设置分组（如：OpenAI、Document、JWT等）
    /// </summary>
    [Required]
    [StringLength(50)]
    public string Group { get; set; } = string.Empty;

    /// <summary>
    /// 设置类型（用于前端渲染）
    /// </summary>
    [Required]
    [StringLength(20)]
    public string ValueType { get; set; } = "string"; // string, bool, int, array, json

    /// <summary>
    /// 设置描述
    /// </summary>
    [StringLength(500)]
    public string? Description { get; set; }

    /// <summary>
    /// 是否敏感信息（如密码、密钥等）
    /// </summary>
    public bool IsSensitive { get; set; } = false;

    /// <summary>
    /// 是否需要重启生效
    /// </summary>
    public bool RequiresRestart { get; set; } = false;

    /// <summary>
    /// 默认值
    /// </summary>
    public string? DefaultValue { get; set; }

    /// <summary>
    /// 排序顺序
    /// </summary>
    public int Order { get; set; } = 0;

    /// <summary>
    /// 是否启用
    /// </summary>
    public bool IsEnabled { get; set; } = true;

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
} 