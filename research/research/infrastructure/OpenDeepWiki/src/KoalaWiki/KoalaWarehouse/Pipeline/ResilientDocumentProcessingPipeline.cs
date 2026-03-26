using System.Diagnostics;

namespace KoalaWiki.KoalaWarehouse.Pipeline;

/// <summary>
/// 健壮的文档处理管道，支持容错和重试
/// </summary>
public class ResilientDocumentProcessingPipeline(
    IEnumerable<IDocumentProcessingStep<DocumentProcessingContext, DocumentProcessingContext>> steps,
    ILogger<ResilientDocumentProcessingPipeline> logger)
    : IDocumentProcessingPipeline
{
    private readonly ActivitySource _activitySource = new("KoalaWiki.Warehouse.Pipeline.Resilient");

    public async Task<DocumentProcessingResult> ExecuteAsync(
        DocumentProcessingCommand command,
        CancellationToken cancellationToken = default)
    {
        using var activity = _activitySource.StartActivity("ResilientPipeline.Execute");

        var context = CreateContext(command);
        var tracker = new PipelineExecutionTracker();
        var overallSuccess = true;

        SetPipelineActivityTags(activity, context);

        logger.LogInformation("开始执行健壮文档处理管道，仓库: {WarehouseId}, 文档: {DocumentId}",
            context.Warehouse.Id, context.Document.Id);

        try
        {
            // 初始化内核实例
            await InitializeKernels(context);

            foreach (var step in steps)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var result = await ExecuteStepWithResilience(step, context, tracker, cancellationToken);

                // 根据执行策略决定是否继续
                if (!ShouldContinueExecution(result, step))
                {
                    overallSuccess = false;
                    logger.LogError("必需步骤 {StepName} 失败，停止管道执行", step.StepName);
                    break;
                }

                // 如果步骤失败但策略允许继续，记录警告
                if (!result.Success && !result.Skipped)
                {
                    logger.LogWarning("步骤 {StepName} 失败但管道继续执行", step.StepName);
                }
            }

            var summary = tracker.CreateSummary();
            activity?.SetTag("pipeline.completed", true);
            activity?.SetTag("pipeline.overall_success", overallSuccess);
            activity?.SetTag("pipeline.successful_steps", summary.SuccessfulSteps);
            activity?.SetTag("pipeline.failed_steps", summary.FailedSteps);
            activity?.SetTag("pipeline.skipped_steps", summary.SkippedSteps);

            logger.LogInformation(
                "文档处理管道执行完成，成功: {Success}, 成功步骤: {SuccessfulSteps}, 失败步骤: {FailedSteps}, 跳过步骤: {SkippedSteps}",
                overallSuccess, summary.SuccessfulSteps, summary.FailedSteps, summary.SkippedSteps);

            var processingResult = new DocumentProcessingResult
            {
                Success = overallSuccess,
                Context = context
            };

            processingResult.Context?.SetMetadata("ExecutionSummary", summary);

            return processingResult;
        }
        catch (OperationCanceledException)
        {
            logger.LogWarning("文档处理管道被取消");
            activity?.SetTag("cancelled", true);
            throw;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "文档处理管道执行失败");
            activity?.SetTag("pipeline.failed", true);
            activity?.SetTag("error", ex.Message);

            return DocumentProcessingResult.CreateFailure(
                $"文档处理管道执行失败: {ex.Message}",
                ex);
        }
    }

    private async Task<StepExecutionResult> ExecuteStepWithResilience(
        IDocumentProcessingStep<DocumentProcessingContext, DocumentProcessingContext> step,
        DocumentProcessingContext context,
        PipelineExecutionTracker tracker,
        CancellationToken cancellationToken)
    {
        var config = step.Configuration;
        var result = new StepExecutionResult
        {
            StartTime = DateTime.UtcNow
        };

        using var activity = _activitySource.StartActivity($"Step.{step.StepName}.Resilient");
        activity?.SetTag("step.name", step.StepName);
        activity?.SetTag("step.strategy", config.ExecutionStrategy.ToString());
        activity?.SetTag("step.retry_strategy", config.RetryStrategy.ToString());

        try
        {
            // 检查是否应该执行此步骤
            if (!await ShouldExecuteStep(step, context))
            {
                result.Skipped = true;
                result.EndTime = DateTime.UtcNow;
                result.ExecutionTime = result.EndTime - result.StartTime;

                logger.LogInformation("跳过步骤: {StepName}（条件不满足）", step.StepName);
                activity?.SetTag("step.skipped", true);

                tracker.RecordStepResult(step.StepName, result);
                return result;
            }

            // 健康检查
            if (!await step.IsHealthyAsync(context))
            {
                logger.LogWarning("步骤 {StepName} 健康检查失败，但仍尝试执行", step.StepName);
                result.Warnings.Add("健康检查失败");
            }

            var attempts = 0;
            var maxAttempts = config.MaxRetryAttempts + 1; // +1 for initial attempt

            while (attempts < maxAttempts)
            {
                attempts++;
                result.AttemptCount = attempts;

                try
                {
                    using var cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
                    cts.CancelAfter(config.StepTimeout);

                    var stopwatch = Stopwatch.StartNew();

                    // 执行步骤
                    logger.LogDebug("执行步骤: {StepName}，尝试次数: {Attempt}/{MaxAttempts}",
                        step.StepName, attempts, maxAttempts);

                    context = await step.ExecuteAsync(context, cts.Token);

                    stopwatch.Stop();
                    result.ExecutionTime = stopwatch.Elapsed;
                    result.Success = true;
                    result.EndTime = DateTime.UtcNow;

                    activity?.SetTag("step.success", true);
                    activity?.SetTag("step.attempts", attempts);
                    activity?.SetTag("step.duration_ms", result.ExecutionTime.TotalMilliseconds);

                    logger.LogInformation("步骤 {StepName} 执行成功，尝试次数: {Attempts}, 耗时: {Duration}ms",
                        step.StepName, attempts, result.ExecutionTime.TotalMilliseconds);

                    break; // 成功，退出重试循环
                }
                catch (Exception ex)
                {
                    result.Exception = ex;
                    result.ErrorMessage = ex.Message;

                    activity?.SetTag("step.error", ex.Message);
                    activity?.SetTag("step.attempt", attempts);

                    logger.LogWarning(ex, "步骤 {StepName} 执行失败，尝试次数: {Attempts}/{MaxAttempts}",
                        step.StepName, attempts, maxAttempts);

                    // 检查是否应该重试
                    if (!ShouldRetry(ex, config, attempts, maxAttempts))
                    {
                        logger.LogError("步骤 {StepName} 不可重试或已达到最大重试次数", step.StepName);
                        break;
                    }

                    // 尝试错误恢复
                    try
                    {
                        logger.LogInformation("尝试对步骤 {StepName} 进行错误恢复", step.StepName);
                        context = await step.HandleErrorAsync(context, ex, attempts);
                        logger.LogInformation("步骤 {StepName} 错误恢复成功，准备重试", step.StepName);
                        result.Warnings.Add($"第{attempts}次尝试失败，已恢复: {ex.Message}");
                    }
                    catch (Exception recoveryEx)
                    {
                        logger.LogWarning(recoveryEx, "步骤 {StepName} 错误恢复失败", step.StepName);
                        result.Warnings.Add($"错误恢复失败: {recoveryEx.Message}");
                    }

                    // 计算重试延迟
                    var delay = RetryStrategyProvider.CalculateDelay(config.RetryStrategy, attempts, config.RetryDelay);
                    if (delay > TimeSpan.Zero)
                    {
                        logger.LogInformation("步骤 {StepName} 将在 {Delay}ms 后重试",
                            step.StepName, delay.TotalMilliseconds);
                        await Task.Delay(delay, cancellationToken);
                    }
                }
            }

            result.EndTime = DateTime.UtcNow;
            if (result.ExecutionTime == TimeSpan.Zero)
            {
                result.ExecutionTime = result.EndTime - result.StartTime;
            }
        }
        catch (Exception ex)
        {
            result.Exception = ex;
            result.ErrorMessage = ex.Message;
            result.EndTime = DateTime.UtcNow;
            result.ExecutionTime = result.EndTime - result.StartTime;

            logger.LogError(ex, "步骤 {StepName} 执行过程中发生未处理异常", step.StepName);
            activity?.SetTag("step.unhandled_error", ex.Message);
        }

        tracker.RecordStepResult(step.StepName, result);
        return result;
    }

    private static async Task<bool> ShouldExecuteStep(
        IDocumentProcessingStep<DocumentProcessingContext, DocumentProcessingContext> step,
        DocumentProcessingContext context)
    {
        try
        {
            return await step.CanExecuteAsync(context);
        }
        catch (Exception ex)
        {
            // 如果检查条件时出错，默认执行
            return true;
        }
    }

    private static bool ShouldRetry(Exception exception, StepExecutionConfig config, int currentAttempt,
        int maxAttempts)
    {
        // 检查是否已达到最大重试次数
        if (currentAttempt >= maxAttempts)
            return false;

        // 使用重试策略提供器判断
        return RetryStrategyProvider.ShouldRetry(exception, config);
    }

    private static bool ShouldContinueExecution(
        StepExecutionResult result,
        IDocumentProcessingStep<DocumentProcessingContext, DocumentProcessingContext> step)
    {
        // 如果步骤成功或被跳过，继续执行
        if (result.Success || result.Skipped)
            return true;

        // 如果是必需步骤且失败，停止执行
        if (step.Configuration.ExecutionStrategy == StepExecutionStrategy.Required)
            return false;

        // 其他情况根据配置决定
        return step.Configuration.ContinueOnFailure;
    }

    private DocumentProcessingContext CreateContext(DocumentProcessingCommand command)
    {
        return new DocumentProcessingContext
        {
            Document = command.Document,
            Warehouse = command.Warehouse,
            GitRepository = command.GitRepository,
            DbContext = command.DbContext
        };
    }

    private async Task InitializeKernels(DocumentProcessingContext context)
    {
        try
        {
            // 初始化主内核（带插件）
            context.KernelInstance = await KernelFactory.GetKernel(
                OpenAIOptions.Endpoint,
                OpenAIOptions.ChatApiKey,
                context.Document.GitPath,
                OpenAIOptions.ChatModel);

            // 初始化文件内核（不带插件）
            context.FileKernelInstance = await KernelFactory.GetKernel(
                OpenAIOptions.Endpoint,
                OpenAIOptions.ChatApiKey,
                context.Document.GitPath,
                OpenAIOptions.ChatModel,
                false);

            logger.LogDebug("内核实例初始化完成");
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "初始化内核实例失败");
            throw;
        }
    }

    private static void SetPipelineActivityTags(Activity? activity, DocumentProcessingContext context)
    {
        activity?.SetTag("warehouse.id", context.Warehouse.Id);
        activity?.SetTag("warehouse.name", context.Warehouse.Name);
        activity?.SetTag("warehouse.type", context.Warehouse.Type);
        activity?.SetTag("document.id", context.Document.Id);
        activity?.SetTag("git.repository", context.GitRepository);
        activity?.SetTag("git.path", context.Document.GitPath);
    }
}