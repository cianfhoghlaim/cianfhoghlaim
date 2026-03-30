namespace KoalaWiki.KoalaWarehouse.Pipeline;

/// <summary>
/// 步骤执行状态
/// </summary>
public enum StepExecutionStatus
{
    NotStarted,
    Running,
    Completed,
    Failed,
    Skipped,
    Retrying
}

/// <summary>
/// 步骤执行结果
/// </summary>
public class StepExecutionResult<T>
{
    public StepExecutionStatus Status { get; set; }
    public T? Result { get; set; }
    public Exception? Exception { get; set; }
    public string? ErrorMessage { get; set; }
    public int AttemptCount { get; set; }
    public TimeSpan ExecutionTime { get; set; }
    public bool IsSuccessful => Status == StepExecutionStatus.Completed;
    public bool ShouldContinue => Status != StepExecutionStatus.Failed || IsOptional;
    public bool IsOptional { get; set; }

    public static StepExecutionResult<T> Success(T result, TimeSpan executionTime, int attemptCount = 1)
    {
        return new StepExecutionResult<T>
        {
            Status = StepExecutionStatus.Completed,
            Result = result,
            ExecutionTime = executionTime,
            AttemptCount = attemptCount
        };
    }

    public static StepExecutionResult<T> Failure(Exception exception, TimeSpan executionTime, int attemptCount, bool isOptional = false)
    {
        return new StepExecutionResult<T>
        {
            Status = StepExecutionStatus.Failed,
            Exception = exception,
            ErrorMessage = exception.Message,
            ExecutionTime = executionTime,
            AttemptCount = attemptCount,
            IsOptional = isOptional
        };
    }

    public static StepExecutionResult<T> Skipped(string reason)
    {
        return new StepExecutionResult<T>
        {
            Status = StepExecutionStatus.Skipped,
            ErrorMessage = reason,
            ExecutionTime = TimeSpan.Zero
        };
    }
}

/// <summary>
/// 重试策略配置
/// </summary>
public class RetryPolicy
{
    public int MaxRetries { get; set; } = 3;
    public TimeSpan InitialDelay { get; set; } = TimeSpan.FromSeconds(1);
    public TimeSpan MaxDelay { get; set; } = TimeSpan.FromMinutes(1);
    public double BackoffMultiplier { get; set; } = 2.0;
    public bool IsEnabled { get; set; } = true;
    
    /// <summary>
    /// 计算重试延迟时间
    /// </summary>
    public TimeSpan GetDelay(int attempt)
    {
        if (attempt <= 0) return TimeSpan.Zero;
        
        var delay = TimeSpan.FromMilliseconds(InitialDelay.TotalMilliseconds * Math.Pow(BackoffMultiplier, attempt - 1));
        return delay > MaxDelay ? MaxDelay : delay;
    }
}

/// <summary>
/// 步骤配置
/// </summary>
public class StepConfiguration
{
    public string StepName { get; set; } = string.Empty;
    public bool IsOptional { get; set; } = false;
    public bool IsEnabled { get; set; } = true;
    public RetryPolicy RetryPolicy { get; set; } = new();
    public TimeSpan Timeout { get; set; } = TimeSpan.FromMinutes(10);
    public Dictionary<string, object> Parameters { get; set; } = new();
}

/// <summary>
/// 管道配置
/// </summary>
public class PipelineConfiguration
{
    public bool FailFastMode { get; set; } = false;
    public bool ContinueOnOptionalFailures { get; set; } = true;
    public Dictionary<string, StepConfiguration> StepConfigurations { get; set; } = new();
    
    public StepConfiguration GetStepConfiguration(string stepName)
    {
        return StepConfigurations.TryGetValue(stepName, out var config) 
            ? config 
            : new StepConfiguration { StepName = stepName };
    }
}