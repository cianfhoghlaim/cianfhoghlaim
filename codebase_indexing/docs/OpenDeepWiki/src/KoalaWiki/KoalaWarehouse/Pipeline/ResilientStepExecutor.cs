using System.Diagnostics;

namespace KoalaWiki.KoalaWarehouse.Pipeline;

/// <summary>
/// 健壮的步骤执行器，支持重试、超时和错误处理
/// </summary>
public class ResilientStepExecutor
{
    private readonly ILogger<ResilientStepExecutor> _logger;
    private readonly ActivitySource _activitySource = new("KoalaWiki.Warehouse.StepExecutor");

    public ResilientStepExecutor(ILogger<ResilientStepExecutor> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// 执行步骤，支持重试和错误处理
    /// </summary>
    public async Task<StepExecutionResult<TOutput>> ExecuteStepAsync<TInput, TOutput>(
        IDocumentProcessingStep<TInput, TOutput> step,
        TInput input,
        StepConfiguration configuration,
        CancellationToken cancellationToken = default)
    {
        using var activity = _activitySource.StartActivity($"Execute.{step.StepName}");
        activity?.SetTag("step.name", step.StepName);
        activity?.SetTag("step.optional", configuration.IsOptional);
        activity?.SetTag("step.enabled", configuration.IsEnabled);

        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            // 检查步骤是否启用
            if (!configuration.IsEnabled)
            {
                _logger.LogInformation("步骤 {StepName} 已禁用，跳过执行", step.StepName);
                return StepExecutionResult<TOutput>.Skipped("步骤已禁用");
            }

            // 检查执行条件
            if (!await step.CanExecuteAsync(input))
            {
                _logger.LogInformation("步骤 {StepName} 执行条件不满足，跳过执行", step.StepName);
                return StepExecutionResult<TOutput>.Skipped("执行条件不满足");
            }

            // 执行步骤（带重试）
            return await ExecuteWithRetryAsync(step, input, configuration, cancellationToken);
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            activity?.SetTag("execution.failed", true);
            activity?.SetTag("error", ex.Message);
            
            _logger.LogError(ex, "步骤 {StepName} 执行过程中发生未处理异常", step.StepName);
            
            return StepExecutionResult<TOutput>.Failure(ex, stopwatch.Elapsed, 0, configuration.IsOptional);
        }
    }

    private async Task<StepExecutionResult<TOutput>> ExecuteWithRetryAsync<TInput, TOutput>(
        IDocumentProcessingStep<TInput, TOutput> step,
        TInput input,
        StepConfiguration configuration,
        CancellationToken cancellationToken)
    {
        var retryPolicy = configuration.RetryPolicy;
        var stopwatch = Stopwatch.StartNew();
        Exception? lastException = null;
        
        for (int attempt = 1; attempt <= retryPolicy.MaxRetries + 1; attempt++)
        {
            try
            {
                _logger.LogInformation("开始执行步骤 {StepName}，尝试次数: {Attempt}/{MaxAttempts}", 
                    step.StepName, attempt, retryPolicy.MaxRetries + 1);

                // 创建超时取消令牌
                using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
                timeoutCts.CancelAfter(configuration.Timeout);

                // 执行步骤
                var result = await step.ExecuteAsync(input, timeoutCts.Token);
                
                stopwatch.Stop();
                
                _logger.LogInformation("步骤 {StepName} 执行成功，耗时: {Duration}ms，尝试次数: {Attempt}", 
                    step.StepName, stopwatch.ElapsedMilliseconds, attempt);

                return StepExecutionResult<TOutput>.Success(result, stopwatch.Elapsed, attempt);
            }
            catch (OperationCanceledException ex) when (cancellationToken.IsCancellationRequested)
            {
                // 外部取消，不重试
                stopwatch.Stop();
                _logger.LogWarning("步骤 {StepName} 被外部取消", step.StepName);
                throw;
            }
            catch (OperationCanceledException ex)
            {
                // 超时，可以重试
                lastException = new TimeoutException($"步骤 {step.StepName} 执行超时 ({configuration.Timeout})", ex);
                _logger.LogWarning("步骤 {StepName} 执行超时，尝试次数: {Attempt}", step.StepName, attempt);
            }
            catch (Exception ex)
            {
                lastException = ex;
                _logger.LogWarning(ex, "步骤 {StepName} 执行失败，尝试次数: {Attempt}", step.StepName, attempt);
            }

            // 如果不是最后一次尝试，等待后重试
            if (attempt <= retryPolicy.MaxRetries && retryPolicy.IsEnabled)
            {
                var delay = retryPolicy.GetDelay(attempt);
                _logger.LogInformation("步骤 {StepName} 将在 {Delay}ms 后重试", step.StepName, delay.TotalMilliseconds);
                
                await Task.Delay(delay, cancellationToken);
            }
        }

        stopwatch.Stop();
        
        _logger.LogError(lastException, "步骤 {StepName} 重试 {MaxRetries} 次后仍然失败", 
            step.StepName, retryPolicy.MaxRetries);

        return StepExecutionResult<TOutput>.Failure(
            lastException ?? new InvalidOperationException("未知错误"), 
            stopwatch.Elapsed, 
            retryPolicy.MaxRetries + 1,
            configuration.IsOptional);
    }
}