using System;
using System.Collections.Generic;

namespace KoalaWiki.Domains.DocumentFile;

public class DocumentCatalog : Entity<string>
{
    /// <summary>
    /// 目录名称
    /// </summary>
    public string Name { get; set; } = string.Empty;
    
    public string Url { get; set; } = string.Empty;

    /// <summary>
    /// 目录描述
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// 目录父级Id
    /// </summary>
    /// <returns></returns>
    public string? ParentId { get; set; } = string.Empty;
    
    /// <summary>
    /// 当前目录排序
    /// </summary>
    public int Order { get; set; } = 0;
    
    /// <summary>
    /// 文档id
    /// </summary>
    public string DucumentId { get; set; } = string.Empty;
    
    public string WarehouseId { get; set; } = string.Empty;
    
    /// <summary>
    /// 是否处理完成
    /// </summary>
    public bool IsCompleted { get; set; } = false;
    
    public string Prompt { get; set; } = string.Empty;
    
    /// <summary>
    /// 是否删除
    /// </summary>
    public bool IsDeleted { get; set; } = false;
    
    public DateTime? DeletedTime { get; set; } = null;
    
    /// <summary>
    /// i18n多语言支持导航属性
    /// </summary>
    public virtual ICollection<DocumentCatalogI18n>? I18nTranslations { get; set; }
}