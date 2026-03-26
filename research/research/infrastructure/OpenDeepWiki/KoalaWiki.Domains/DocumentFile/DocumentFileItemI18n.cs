using System;

namespace KoalaWiki.Domains.DocumentFile;

/// <summary>
/// 文档文件多语言支持
/// </summary>
public class DocumentFileItemI18n : Entity<string>
{
    /// <summary>
    /// 关联的文档文件ID
    /// </summary>
    public string DocumentFileItemId { get; set; } = string.Empty;
    
    /// <summary>
    /// 语言代码 (如: zh-CN, en-US)
    /// </summary>
    public string LanguageCode { get; set; } = string.Empty;
    
    /// <summary>
    /// 多语言标题
    /// </summary>
    public string Title { get; set; } = string.Empty;
    
    /// <summary>
    /// 多语言描述
    /// </summary>
    public string Description { get; set; } = string.Empty;
    
    /// <summary>
    /// 多语言文档内容
    /// </summary>
    public string Content { get; set; } = string.Empty;
    
    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// 关联的DocumentFileItem导航属性
    /// </summary>
    public virtual DocumentFileItem? DocumentFileItem { get; set; }
} 