using System;

namespace KoalaWiki.Domains.FineTuning;

/// <summary>
/// 训练数据集
/// </summary>
public class TrainingDataset : Entity<string>
{
    public string WarehouseId { get; set; } = string.Empty; // 仓库ID
    
    public string UserId { get; set; }
            
    /// <summary>
    /// 数据集生成时间
    /// </summary>
    public DateTime CreatedAt { get; set; }
        
    /// <summary>
    /// 数据集最后更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; }

    /// <summary>
    /// 数据集名称
    /// </summary>
    public TrainingDatasetStatus Status { get; set; } = TrainingDatasetStatus.NotStarted;
    
    public string Name { get; set; } = string.Empty; // 数据集名称
    
    /// <summary>
    /// API接口地址
    /// </summary>
    public string Endpoint { get; set; } = string.Empty; 
    
    /// <summary>
    /// API密钥
    /// </summary>
    public string ApiKey { get; set; } = string.Empty;
    
    /// <summary>
    /// Prompt
    /// </summary>
    public string Prompt { get; set; } = string.Empty;
    
    /// <summary>
    /// 模型名称
    /// </summary>
    public string Model { get; set; } = string.Empty; // 模型名称
}