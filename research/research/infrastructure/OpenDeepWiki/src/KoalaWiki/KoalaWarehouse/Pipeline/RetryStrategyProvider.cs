namespace KoalaWiki.KoalaWarehouse.Pipeline;

/// <summary>
/// 重试策略提供器
/// </summary>
public static class RetryStrategyProvider
{
    /// <summary>
    /// 计算重试延迟
    /// </summary>
    /// <param name="strategy">重试策略</param>
    /// <param name="attempt">当前尝试次数</param>
    /// <param name="baseDelay">基础延迟</param>
    /// <returns>计算后的延迟时间</returns>
    public static TimeSpan CalculateDelay(StepRetryStrategy strategy, int attempt, TimeSpan baseDelay)
    {
        return strategy switch
        {
            StepRetryStrategy.None => TimeSpan.Zero,
            StepRetryStrategy.FixedInterval => baseDelay,
            StepRetryStrategy.ExponentialBackoff => TimeSpan.FromMilliseconds(
                baseDelay.TotalMilliseconds * Math.Pow(2, attempt - 1)),
            StepRetryStrategy.Smart => CalculateSmartDelay(attempt, baseDelay),
            _ => baseDelay
        };
    }
    
    /// <summary>
    /// 智能延迟计算：前几次快速重试，后续使用指数退避
    /// </summary>
    private static TimeSpan CalculateSmartDelay(int attempt, TimeSpan baseDelay)
    {
        if (attempt <= 2)
            return TimeSpan.FromSeconds(1); // 快速重试
        else
            return TimeSpan.FromMilliseconds(baseDelay.TotalMilliseconds * Math.Pow(1.5, attempt - 2));
    }
    
    /// <summary>
    /// 判断是否应该重试
    /// </summary>
    /// <param name="exception">发生的异常</param>
    /// <param name="config">步骤配置</param>
    /// <returns>是否应该重试</returns>
    public static bool ShouldRetry(Exception exception, StepExecutionConfig config)
    {
        // 如果明确不可重试，则不重试
        if (config.NonRetriableExceptions.Any(t => t.IsAssignableFrom(exception.GetType())))
            return false;
            
        // 如果明确可重试，则重试
        if (config.RetriableExceptions.Any(t => t.IsAssignableFrom(exception.GetType())))
            return true;
            
        // 默认策略：网络和临时错误可重试
        return exception is HttpRequestException or TaskCanceledException or TimeoutException;
    }
    
    /// <summary>
    /// 获取建议的重试次数
    /// </summary>
    /// <param name="exception">异常</param>
    /// <param name="config">配置</param>
    /// <returns>建议的重试次数</returns>
    public static int GetSuggestedRetryCount(Exception exception, StepExecutionConfig config)
    {
        return exception switch
        {
            HttpRequestException => Math.Min(config.MaxRetryAttempts, 5),
            TaskCanceledException => Math.Min(config.MaxRetryAttempts, 3),
            TimeoutException => Math.Min(config.MaxRetryAttempts, 2),
            InvalidOperationException => Math.Min(config.MaxRetryAttempts, 2),
            _ => config.MaxRetryAttempts
        };
    }
}

/// <summary>
/// 管道执行状态追踪器
/// </summary>
public class PipelineExecutionTracker
{
    private readonly Dictionary<string, StepExecutionResult> _stepResults = new();
    private readonly List<string> _executionOrder = new();
    private readonly DateTime _startTime = DateTime.UtcNow;
    
    /// <summary>
    /// 记录步骤结果
    /// </summary>
    /// <param name="stepName">步骤名称</param>
    /// <param name="result">执行结果</param>
    public void RecordStepResult(string stepName, StepExecutionResult result)
    {
        _stepResults[stepName] = result;
        if (!_executionOrder.Contains(stepName))
        {
            _executionOrder.Add(stepName);
        }
    }
    
    /// <summary>
    /// 获取步骤结果
    /// </summary>
    /// <param name="stepName">步骤名称</param>
    /// <returns>步骤结果</returns>
    public StepExecutionResult? GetStepResult(string stepName)
    {
        return _stepResults.TryGetValue(stepName, out var result) ? result : null;
    }
    
    /// <summary>
    /// 创建执行摘要
    /// </summary>
    /// <returns>执行摘要</returns>
    public PipelineExecutionSummary CreateSummary()
    {
        var endTime = DateTime.UtcNow;
        var successfulSteps = _stepResults.Values.Count(r => r.Success);
        var failedSteps = _stepResults.Values.Count(r => !r.Success && !r.Skipped);
        var skippedSteps = _stepResults.Values.Count(r => r.Skipped);
        
        return new PipelineExecutionSummary
        {
            TotalSteps = _stepResults.Count,
            SuccessfulSteps = successfulSteps,
            FailedSteps = failedSteps,
            SkippedSteps = skippedSteps,
            TotalExecutionTime = _stepResults.Values.Sum(r => r.ExecutionTime.TotalMilliseconds),
            ExecutionOrder = _executionOrder.ToArray(),
            StepResults = _stepResults.ToDictionary(kvp => kvp.Key, kvp => kvp.Value),
            OverallSuccess = failedSteps == 0, // 没有必需步骤失败则认为成功
            StartTime = _startTime,
            EndTime = endTime
        };
    }
    
    /// <summary>
    /// 获取失败步骤的详细信息
    /// </summary>
    /// <returns>失败步骤信息</returns>
    public Dictionary<string, string> GetFailureDetails()
    {
        return _stepResults
            .Where(kvp => !kvp.Value.Success && !kvp.Value.Skipped)
            .ToDictionary(
                kvp => kvp.Key, 
                kvp => kvp.Value.ErrorMessage ?? kvp.Value.Exception?.Message ?? "未知错误"
            );
    }
    
    /// <summary>
    /// 获取警告信息
    /// </summary>
    /// <returns>警告信息</returns>
    public List<string> GetWarnings()
    {
        var warnings = new List<string>();
        foreach (var result in _stepResults.Values)
        {
            warnings.AddRange(result.Warnings);
        }
        return warnings;
    }
}