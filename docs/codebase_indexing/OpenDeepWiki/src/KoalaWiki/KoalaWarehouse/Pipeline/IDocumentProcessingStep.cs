using System.Diagnostics;
using ILogger = Microsoft.Extensions.Logging.ILogger;

namespace KoalaWiki.KoalaWarehouse.Pipeline;

public interface IDocumentProcessingStep<TInput, TOutput>
{
    string StepName { get; }
    StepExecutionConfig Configuration { get; }
    
    Task<TOutput> ExecuteAsync(TInput input, CancellationToken cancellationToken = default);
    
    Task<bool> CanExecuteAsync(TInput input);
    
    /// <summary>
    /// 错误恢复处理
    /// </summary>
    /// <param name="input">输入上下文</param>
    /// <param name="exception">发生的异常</param>
    /// <param name="attemptCount">当前尝试次数</param>
    /// <returns>恢复后的上下文</returns>
    Task<TOutput> HandleErrorAsync(TInput input, Exception exception, int attemptCount);
    
    /// <summary>
    /// 步骤健康检查
    /// </summary>
    /// <param name="input">输入上下文</param>
    /// <returns>是否健康</returns>
    Task<bool> IsHealthyAsync(TInput input);
    
    /// <summary>
    /// 获取步骤依赖
    /// </summary>
    /// <returns>依赖的步骤名称数组</returns>
    Task<string[]> GetDependenciesAsync();
}

public abstract class DocumentProcessingStepBase<TInput, TOutput>(ILogger logger)
    : IDocumentProcessingStep<TInput, TOutput>
{
    protected readonly ActivitySource ActivitySource = new("KoalaWiki.Warehouse.Pipeline");
    protected readonly ILogger Logger = logger;
    
    public abstract string StepName { get; }
    
    /// <summary>
    /// 步骤执行配置，子类可以重写以提供自定义配置
    /// </summary>
    public virtual StepExecutionConfig Configuration => new()
    {
        ExecutionStrategy = StepExecutionStrategy.BestEffort,
        RetryStrategy = StepRetryStrategy.Smart,
        MaxRetryAttempts = 3,
        RetryDelay = TimeSpan.FromSeconds(5),
        StepTimeout = TimeSpan.FromMinutes(10),
        ContinueOnFailure = true
    };
    
    public abstract Task<TOutput> ExecuteAsync(TInput input,
        CancellationToken cancellationToken = default);
    
    public virtual Task<bool> CanExecuteAsync(TInput input) => Task.FromResult(true);
    
    /// <summary>
    /// 默认错误恢复实现，子类可以重写提供特定的恢复逻辑
    /// </summary>
    public virtual Task<TOutput> HandleErrorAsync(TInput input, Exception exception, int attemptCount)
    {
        Logger.LogWarning("步骤 {StepName} 使用默认错误恢复，异常: {Exception}", 
            StepName, exception.Message);
        
        // 对于大多数步骤，TInput 和 TOutput 是相同的类型（DocumentProcessingContext）
        // 但为了类型安全，我们需要进行转换
        if (input is TOutput output)
        {
            return Task.FromResult(output);
        }
        
        
        // 如果类型不匹配，抛出异常让子类必须重写此方法
        throw new NotImplementedException(
            $"步骤 {StepName} 的输入类型 {typeof(TInput).Name} 与输出类型 {typeof(TOutput).Name} 不匹配，" +
            "必须重写 HandleErrorAsync 方法提供特定的错误恢复逻辑");
    }
    
    /// <summary>
    /// 默认健康检查实现，子类可以重写提供特定的检查逻辑
    /// </summary>
    public virtual Task<bool> IsHealthyAsync(TInput input)
    {
        return Task.FromResult(true); // 默认认为健康
    }
    
    /// <summary>
    /// 默认依赖检查，子类可以重写指定依赖关系
    /// </summary>
    public virtual Task<string[]> GetDependenciesAsync()
    {
        return Task.FromResult(Array.Empty<string>());
    }
    
    protected virtual void SetActivityTags(Activity? activity, TInput input)
    {
        // 基础实现，子类可以重写添加特定的标签
    }
}