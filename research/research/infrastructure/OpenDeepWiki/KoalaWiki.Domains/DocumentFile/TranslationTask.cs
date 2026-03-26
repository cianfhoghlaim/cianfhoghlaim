using System;

namespace KoalaWiki.Domains.DocumentFile;

/// <summary>
/// 翻译任务 - 用于管理翻译状态和防重复提交
/// </summary>
public class TranslationTask : Entity<string>
{
    /// <summary>
    /// 仓库ID
    /// </summary>
    public string WarehouseId { get; set; } = string.Empty;
    
    /// <summary>
    /// 目标语言代码
    /// </summary>
    public string TargetLanguage { get; set; } = string.Empty;
    
    /// <summary>
    /// 源语言代码
    /// </summary>
    public string SourceLanguage { get; set; } = string.Empty;
    
    /// <summary>
    /// 任务状态: Pending, Running, Completed, Failed
    /// </summary>
    public TranslationTaskStatus Status { get; set; } = TranslationTaskStatus.Pending;
    
    /// <summary>
    /// 任务类型: Repository, Catalog
    /// </summary>
    public TranslationTaskType TaskType { get; set; } = TranslationTaskType.Repository;
    
    /// <summary>
    /// 目标ID (仓库ID或目录ID)
    /// </summary>
    public string TargetId { get; set; } = string.Empty;
    
    /// <summary>
    /// 错误信息
    /// </summary>
    public string? ErrorMessage { get; set; }
    
    /// <summary>
    /// 已翻译的目录数量
    /// </summary>
    public int CatalogsTranslated { get; set; }
    
    /// <summary>
    /// 已翻译的文件数量
    /// </summary>
    public int FilesTranslated { get; set; }
    
    /// <summary>
    /// 总目录数量
    /// </summary>
    public int TotalCatalogs { get; set; }
    
    /// <summary>
    /// 总文件数量
    /// </summary>
    public int TotalFiles { get; set; }
    
    /// <summary>
    /// 开始时间
    /// </summary>
    public DateTime StartedAt { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// 完成时间
    /// </summary>
    public DateTime? CompletedAt { get; set; }
    
    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// 进度百分比
    /// </summary>
    public int Progress => TotalCatalogs + TotalFiles > 0 
        ? (int)((CatalogsTranslated + FilesTranslated) * 100.0 / (TotalCatalogs + TotalFiles))
        : 0;
    
    /// <summary>
    /// 任务持续时间
    /// </summary>
    public TimeSpan Duration => CompletedAt.HasValue ? CompletedAt.Value - StartedAt : DateTime.UtcNow - StartedAt;
}

/// <summary>
/// 翻译任务状态
/// </summary>
public enum TranslationTaskStatus
{
    /// <summary>
    /// 等待中
    /// </summary>
    Pending = 0,
    
    /// <summary>
    /// 运行中
    /// </summary>
    Running = 1,
    
    /// <summary>
    /// 已完成
    /// </summary>
    Completed = 2,
    
    /// <summary>
    /// 已失败
    /// </summary>
    Failed = 3,
    
    /// <summary>
    /// 已取消
    /// </summary>
    Cancelled = 4
}

/// <summary>
/// 翻译任务类型
/// </summary>
public enum TranslationTaskType
{
    /// <summary>
    /// 仓库翻译
    /// </summary>
    Repository = 0,
    
    /// <summary>
    /// 单个目录翻译
    /// </summary>
    Catalog = 1
}