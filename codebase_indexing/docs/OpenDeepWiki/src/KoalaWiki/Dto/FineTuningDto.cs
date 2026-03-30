using System.ComponentModel.DataAnnotations;

namespace KoalaWiki.Dto;

/// <summary>
/// 创建数据集输入模型
/// </summary>
public class CreateDatasetInput
{
    /// <summary>
    /// 仓库ID
    /// </summary>
    [Required(ErrorMessage = "仓库ID不能为空")]
    public string WarehouseId { get; set; } = string.Empty;
    
    /// <summary>
    /// 数据集名称
    /// </summary>
    [Required(ErrorMessage = "数据集名称不能为空")]
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// API接口地址
    /// </summary>
    [Required(ErrorMessage = "API接口地址不能为空")]
    public string Endpoint { get; set; } = string.Empty;
    
    /// <summary>
    /// API密钥
    /// </summary>
    [Required(ErrorMessage = "API密钥不能为空")]
    public string ApiKey { get; set; } = string.Empty;
    
    /// <summary>
    /// 提示词
    /// </summary>
    public string Prompt { get; set; } = string.Empty;
    
    public string Model { get; set; } = string.Empty;
}

/// <summary>
/// 更新数据集输入模型
/// </summary>
public class UpdateDatasetInput
{
    /// <summary>
    /// 数据集ID
    /// </summary>
    [Required(ErrorMessage = "数据集ID不能为空")]
    public string DatasetId { get; set; } = string.Empty;
    
    /// <summary>
    /// 数据集名称
    /// </summary>
    [Required(ErrorMessage = "数据集名称不能为空")]
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// API接口地址
    /// </summary>
    [Required(ErrorMessage = "API接口地址不能为空")]
    public string Endpoint { get; set; } = string.Empty;
    
    /// <summary>
    /// API密钥
    /// </summary>
    [Required(ErrorMessage = "API密钥不能为空")]
    public string ApiKey { get; set; } = string.Empty;
    
    /// <summary>
    /// 提示词
    /// </summary>
    public string Prompt { get; set; } = string.Empty;
}

/// <summary>
/// 创建微调任务输入模型
/// </summary>
public class CreateTaskInput
{
    /// <summary>
    /// 训练数据集ID
    /// </summary>
    [Required(ErrorMessage = "训练数据集ID不能为空")]
    public string TrainingDatasetId { get; set; } = string.Empty;
    
    /// <summary>
    /// 文档目录ID
    /// </summary>
    [Required(ErrorMessage = "文档目录ID不能为空")]
    public string DocumentCatalogId { get; set; } = string.Empty;
    
    /// <summary>
    /// 微调任务名称
    /// </summary>
    [Required(ErrorMessage = "微调任务名称不能为空")]
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// 微调任务描述
    /// </summary>
    public string Description { get; set; } = string.Empty;
} 