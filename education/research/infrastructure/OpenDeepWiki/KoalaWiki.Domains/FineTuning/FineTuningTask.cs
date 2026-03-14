using System;
using KoalaWiki.Domains.DocumentFile;

namespace KoalaWiki.Domains.FineTuning;

public class FineTuningTask : Entity<string>
{
    public string WarehouseId { get; set; } = string.Empty; // 仓库ID

    /// <summary>
    /// 训练数据集
    /// </summary>
    public string TrainingDatasetId { get; set; } = string.Empty;
    
    /// <summary>
    /// 数据集目录ID
    /// </summary>
    public string DocumentCatalogId { get; set; } = string.Empty;
    
    public string Name { get; set; }

    public string UserId { get; set; }
    
    /// <summary>
    /// 任务描述
    /// </summary>
    public string Description { get; set; }

    /// <summary>
    /// 任务创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// 任务开始时间
    /// </summary>
    public DateTime? StartedAt { get; set; }

    /// <summary>
    /// 任务完成时间
    /// </summary>
    public DateTime? CompletedAt { get; set; }

    /// <summary>
    /// 任务进度
    /// </summary>
    public FineTuningTaskStatus Status { get; set; } = FineTuningTaskStatus.NotStarted;
    
    /// <summary>
    /// 数据集
    /// </summary>
    public string Dataset { get; set; } = string.Empty;
    
    /// <summary>
    /// Error
    /// </summary>
    public string? Error { get; set; } = string.Empty;
    
    /// <summary>
    /// 原始数据集
    /// </summary>
    public string? OriginalDataset { get; set; } = string.Empty;
    
    public DocumentCatalog DocumentCatalog { get; set; }
}
