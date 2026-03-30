namespace KoalaWiki.Dto;

/// <summary>
/// 系统设置输入DTO
/// </summary>
public class SystemSettingInput
{
    /// <summary>
    /// 设置键名
    /// </summary>
    public string Key { get; set; } = string.Empty;

    /// <summary>
    /// 设置值
    /// </summary>
    public string? Value { get; set; }

    /// <summary>
    /// 设置分组
    /// </summary>
    public string Group { get; set; } = string.Empty;

    /// <summary>
    /// 设置类型
    /// </summary>
    public string ValueType { get; set; } = "string";

    /// <summary>
    /// 设置描述
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// 是否敏感信息
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
}

/// <summary>
/// 系统设置输出DTO
/// </summary>
public class SystemSettingOutput
{
    /// <summary>
    /// ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 设置键名
    /// </summary>
    public string Key { get; set; } = string.Empty;

    /// <summary>
    /// 设置值（敏感信息会被掩码）
    /// </summary>
    public string? Value { get; set; }

    /// <summary>
    /// 设置分组
    /// </summary>
    public string Group { get; set; } = string.Empty;

    /// <summary>
    /// 设置类型
    /// </summary>
    public string ValueType { get; set; } = "string";

    /// <summary>
    /// 设置描述
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// 是否敏感信息
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
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; }
}

/// <summary>
/// 批量更新系统设置输入
/// </summary>
public class BatchUpdateSystemSettingsInput
{
    /// <summary>
    /// 设置项列表
    /// </summary>
    public List<SystemSettingUpdateItem> Settings { get; set; } = new();
}

/// <summary>
/// 系统设置更新项
/// </summary>
public class SystemSettingUpdateItem
{
    /// <summary>
    /// 设置键名
    /// </summary>
    public string Key { get; set; } = string.Empty;

    /// <summary>
    /// 设置值
    /// </summary>
    public string? Value { get; set; }
}

/// <summary>
/// 系统设置分组输出
/// </summary>
public class SystemSettingGroupOutput
{
    /// <summary>
    /// 分组名称
    /// </summary>
    public string Group { get; set; } = string.Empty;

    /// <summary>
    /// 分组设置项
    /// </summary>
    public List<SystemSettingOutput> Settings { get; set; } = new();
}

/// <summary>
/// AI API测试请求参数
/// </summary>
public class TestAIApiRequest
{
    /// <summary>
    /// API端点地址
    /// </summary>
    public string Endpoint { get; set; } = string.Empty;

    /// <summary>
    /// API密钥
    /// </summary>
    public string ApiKey { get; set; } = string.Empty;

    /// <summary>
    /// 模型名称
    /// </summary>
    public string? Model { get; set; }
}

/// <summary>
/// 测试结果响应
/// </summary>
public class TestResultResponse
{
    /// <summary>
    /// 是否成功
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// 消息
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// 详细信息
    /// </summary>
    public object? Details { get; set; }
} 