namespace KoalaWiki.KoalaWarehouse.Pipeline;

/// <summary>
/// 步骤执行策略
/// </summary>
public enum StepExecutionStrategy
{
    /// <summary>
    /// 必须成功 - 如果失败则整个任务失败
    /// </summary>
    Required,
    
    /// <summary>
    /// 最佳努力 - 失败时记录错误但继续执行
    /// </summary>
    BestEffort,
    
    /// <summary>
    /// 可选的 - 失败时跳过，不影响后续步骤
    /// </summary>
    Optional,
    
    /// <summary>
    /// 条件性 - 基于前置条件决定是否执行
    /// </summary>
    Conditional
}

/// <summary>
/// 步骤重试策略
/// </summary>
public enum StepRetryStrategy
{
    /// <summary>
    /// 不重试
    /// </summary>
    None,
    
    /// <summary>
    /// 固定间隔重试
    /// </summary>
    FixedInterval,
    
    /// <summary>
    /// 指数退避重试
    /// </summary>
    ExponentialBackoff,
    
    /// <summary>
    /// 智能重试（根据错误类型调整策略）
    /// </summary>
    Smart
}

/// <summary>
/// 步骤执行配置
/// </summary>
public class StepExecutionConfig
{
    /// <summary>
    /// 执行策略
    /// </summary>
    public StepExecutionStrategy ExecutionStrategy { get; set; } = StepExecutionStrategy.BestEffort;
    
    /// <summary>
    /// 重试策略
    /// </summary>
    public StepRetryStrategy RetryStrategy { get; set; } = StepRetryStrategy.Smart;
    
    /// <summary>
    /// 最大重试次数
    /// </summary>
    public int MaxRetryAttempts { get; set; } = 3;
    
    /// <summary>
    /// 重试延迟
    /// </summary>
    public TimeSpan RetryDelay { get; set; } = TimeSpan.FromSeconds(5);
    
    /// <summary>
    /// 步骤超时时间
    /// </summary>
    public TimeSpan StepTimeout { get; set; } = TimeSpan.FromMinutes(60);
    
    /// <summary>
    /// 失败时是否继续执行后续步骤
    /// </summary>
    public bool ContinueOnFailure { get; set; } = true;
    
    /// <summary>
    /// 可重试的异常类型
    /// </summary>
    public List<Type> RetriableExceptions { get; set; } = new()
    {
        typeof(HttpRequestException),
        typeof(TaskCanceledException),
        typeof(TimeoutException),
        typeof(InvalidOperationException)
    };
    
    /// <summary>
    /// 不可重试的异常类型
    /// </summary>
    public List<Type> NonRetriableExceptions { get; set; } = new()
    {
        typeof(FileNotFoundException),
        typeof(UnauthorizedAccessException),
        typeof(ArgumentException),
        typeof(ArgumentNullException)
    };
}

/// <summary>
/// 步骤执行结果
/// </summary>
public class StepExecutionResult
{
    /// <summary>
    /// 是否成功
    /// </summary>
    public bool Success { get; set; }
    
    /// <summary>
    /// 是否跳过
    /// </summary>
    public bool Skipped { get; set; }
    
    /// <summary>
    /// 尝试次数
    /// </summary>
    public int AttemptCount { get; set; }
    
    /// <summary>
    /// 异常信息
    /// </summary>
    public Exception? Exception { get; set; }
    
    /// <summary>
    /// 错误消息
    /// </summary>
    public string? ErrorMessage { get; set; }
    
    /// <summary>
    /// 执行时间
    /// </summary>
    public TimeSpan ExecutionTime { get; set; }
    
    /// <summary>
    /// 元数据
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();
    
    /// <summary>
    /// 开始时间
    /// </summary>
    public DateTime StartTime { get; set; }
    
    /// <summary>
    /// 结束时间
    /// </summary>
    public DateTime EndTime { get; set; }
    
    /// <summary>
    /// 警告消息列表
    /// </summary>
    public List<string> Warnings { get; set; } = new();
}

/// <summary>
/// 管道执行摘要
/// </summary>
public class PipelineExecutionSummary
{
    /// <summary>
    /// 总步骤数
    /// </summary>
    public int TotalSteps { get; set; }
    
    /// <summary>
    /// 成功步骤数
    /// </summary>
    public int SuccessfulSteps { get; set; }
    
    /// <summary>
    /// 失败步骤数
    /// </summary>
    public int FailedSteps { get; set; }
    
    /// <summary>
    /// 跳过步骤数
    /// </summary>
    public int SkippedSteps { get; set; }
    
    /// <summary>
    /// 总执行时间（毫秒）
    /// </summary>
    public double TotalExecutionTime { get; set; }
    
    /// <summary>
    /// 执行顺序
    /// </summary>
    public string[] ExecutionOrder { get; set; } = Array.Empty<string>();
    
    /// <summary>
    /// 步骤结果详情
    /// </summary>
    public Dictionary<string, StepExecutionResult> StepResults { get; set; } = new();
    
    /// <summary>
    /// 整体是否成功（所有必需步骤都成功）
    /// </summary>
    public bool OverallSuccess { get; set; }
    
    /// <summary>
    /// 执行开始时间
    /// </summary>
    public DateTime StartTime { get; set; }
    
    /// <summary>
    /// 执行结束时间
    /// </summary>
    public DateTime EndTime { get; set; }
}