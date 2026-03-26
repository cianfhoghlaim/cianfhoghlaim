using System.Diagnostics;
using KoalaWiki.Options;

namespace KoalaWiki.KoalaWarehouse.Pipeline;

public class DocumentProcessingPipeline : IDocumentProcessingPipeline
{
    private readonly IEnumerable<IDocumentProcessingStep<DocumentProcessingContext, DocumentProcessingContext>> _steps;
    private readonly ILogger<DocumentProcessingPipeline> _logger;
    private readonly ActivitySource _activitySource = new("KoalaWiki.Warehouse.Pipeline");

    public DocumentProcessingPipeline(
        IEnumerable<IDocumentProcessingStep<DocumentProcessingContext, DocumentProcessingContext>> steps,
        ILogger<DocumentProcessingPipeline> logger)
    {
        _steps = steps;
        _logger = logger;
    }

    public async Task<DocumentProcessingResult> ExecuteAsync(
        DocumentProcessingCommand command,
        CancellationToken cancellationToken = default)
    {
        using var activity = _activitySource.StartActivity("DocumentProcessingPipeline.Execute");

        try
        {
            var context = new DocumentProcessingContext
            {
                Document = command.Document,
                Warehouse = command.Warehouse,
                GitRepository = command.GitRepository,
                DbContext = command.DbContext
            };

            // 初始化内核实例
            await InitializeKernels(context);

            SetPipelineActivityTags(activity, context);

            _logger.LogInformation("开始执行文档处理管道，仓库: {WarehouseId}, 文档: {DocumentId}",
                context.Warehouse.Id, context.Document.Id);

            var executedSteps = new List<string>();

            foreach (var step in _steps)
            {
                cancellationToken.ThrowIfCancellationRequested();

                try
                {
                    if (await step.CanExecuteAsync(context))
                    {
                        _logger.LogInformation("执行步骤: {StepName}", step.StepName);

                        using var stepActivity = _activitySource.StartActivity($"Step.{step.StepName}");
                        stepActivity?.SetTag("step.name", step.StepName);

                        var stepStartTime = DateTime.UtcNow;
                        context = await step.ExecuteAsync(context, cancellationToken);
                        var stepDuration = DateTime.UtcNow - stepStartTime;

                        stepActivity?.SetTag("step.duration_ms", stepDuration.TotalMilliseconds);
                        stepActivity?.SetTag("step.completed", true);

                        executedSteps.Add(step.StepName);

                        _logger.LogInformation("完成步骤: {StepName}，耗时: {Duration}ms",
                            step.StepName, stepDuration.TotalMilliseconds);
                    }
                    else
                    {
                        _logger.LogInformation("跳过步骤: {StepName}（条件不满足）", step.StepName);
                    }
                }
                catch (Exception stepEx)
                {
                    _logger.LogError(stepEx, "步骤 {StepName} 执行失败", step.StepName);
                    activity?.SetTag("failed_step", step.StepName);
                    activity?.SetTag("error", stepEx.Message);

                    return DocumentProcessingResult.CreateFailure(
                        $"步骤 '{step.StepName}' 执行失败: {stepEx.Message}",
                        stepEx);
                }
            }

            activity?.SetTag("pipeline.completed", true);
            activity?.SetTag("executed_steps", string.Join(",", executedSteps));

            _logger.LogInformation("文档处理管道执行完成，执行的步骤: {Steps}",
                string.Join(", ", executedSteps));

            return DocumentProcessingResult.CreateSuccess(context);
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("文档处理管道被取消");
            activity?.SetTag("cancelled", true);
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "文档处理管道执行失败");
            activity?.SetTag("pipeline.failed", true);
            activity?.SetTag("error", ex.Message);

            return DocumentProcessingResult.CreateFailure(
                $"文档处理管道执行失败: {ex.Message}",
                ex);
        }
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

            _logger.LogDebug("内核实例初始化完成");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "初始化内核实例失败");
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