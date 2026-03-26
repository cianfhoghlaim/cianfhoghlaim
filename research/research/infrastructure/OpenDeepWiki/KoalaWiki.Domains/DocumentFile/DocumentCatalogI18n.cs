using System;

namespace KoalaWiki.Domains.DocumentFile;

/// <summary>
/// 文档目录多语言支持
/// </summary>
public class DocumentCatalogI18n : Entity<string>
{
    /// <summary>
    /// 关联的文档目录ID
    /// </summary>
    public string DocumentCatalogId { get; set; } = string.Empty;
    
    /// <summary>
    /// 语言代码 (如: zh-CN, en-US)
    /// </summary>
    public string LanguageCode { get; set; } = string.Empty;
    
    /// <summary>
    /// 多语言目录名称
    /// </summary>
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// 多语言目录描述
    /// </summary>
    public string Description { get; set; } = string.Empty;
    
    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// 关联的DocumentCatalog导航属性
    /// </summary>
    public virtual DocumentCatalog? DocumentCatalog { get; set; }
} 