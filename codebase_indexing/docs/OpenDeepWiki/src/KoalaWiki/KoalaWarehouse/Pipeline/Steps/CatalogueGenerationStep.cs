using System.Diagnostics;
using KoalaWiki.Options;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.KoalaWarehouse.Pipeline.Steps;

public class CatalogueGenerationStep(ILogger<CatalogueGenerationStep> logger)
    : DocumentProcessingStepBase<DocumentProcessingContext, DocumentProcessingContext>(logger)
{
    public override string StepName => "读取并生成目录结构";

    public override StepExecutionConfig Configuration => new()
    {
        ExecutionStrategy = StepExecutionStrategy.BestEffort, // 目录结构生成失败时使用基础版本
        RetryStrategy = StepRetryStrategy.Smart,
        MaxRetryAttempts = 3,
        RetryDelay = TimeSpan.FromSeconds(5),
        StepTimeout = TimeSpan.FromMinutes(60), // 目录分析可能需要更长时间
        ContinueOnFailure = true,
        RetriableExceptions =
        [
            typeof(HttpRequestException),
            typeof(TaskCanceledException),
            typeof(InvalidOperationException),
            typeof(TimeoutException)
        ],
        NonRetriableExceptions =
        [
            typeof(DirectoryNotFoundException),
            typeof(UnauthorizedAccessException)
        ]
    };

    public override async Task<DocumentProcessingContext> ExecuteAsync(
        DocumentProcessingContext context,
        CancellationToken cancellationToken = default)
    {
        using var activity = ActivitySource.StartActivity(StepName);
        SetActivityTags(activity, context);

        Logger.LogInformation("开始执行 {StepName} 步骤", StepName);

        try
        {
            var catalogue = context.Document.GetCatalogueSmartFilterOptimized();

            activity?.SetTag("catalogue.length", catalogue?.Length ?? 0);
            context.SetStepResult(StepName, catalogue);
            context.Catalogue = catalogue;

            Logger.LogInformation("完成 {StepName} 步骤，目录结构长度: {Length}",
                StepName, catalogue?.Length ?? 0);
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "执行 {StepName} 步骤时发生错误", StepName);
            activity?.SetTag("error", ex.Message);
            throw;
        }

        return await Task.FromResult(context);
    }

    public override async Task<DocumentProcessingContext> HandleErrorAsync(
        DocumentProcessingContext input,
        Exception exception,
        int attemptCount)
    {
        Logger.LogWarning("目录结构生成失败，使用基础目录结构，异常: {Exception}", exception.Message);

        // 目录结构生成失败时，生成基础的目录结构
        if (string.IsNullOrEmpty(input.Catalogue))
        {
            try
            {
                // 尝试使用基础的目录扫描
                input.Catalogue = DocumentsHelper.GetCatalogue(input.Document.GitPath);
                Logger.LogInformation("使用基础目录结构，长度: {Length}", input.Catalogue?.Length ?? 0);
            }
            catch (Exception ex)
            {
                Logger.LogWarning(ex, "基础目录结构生成也失败，使用空目录结构");
                input.Catalogue = "项目目录结构暂时无法生成";
            }
        }

        return await Task.FromResult(input);
    }

    public override async Task<bool> IsHealthyAsync(DocumentProcessingContext input)
    {
        try
        {
            // 检查目录是否存在且可访问
            if (!Directory.Exists(input.Document.GitPath))
            {
                Logger.LogWarning("目录不存在: {Path}", input.Document.GitPath);
                return false;
            }

            // 检查是否有读取权限
            try
            {
                _ = Directory.GetDirectories(input.Document.GitPath);
                _ = Directory.GetFiles(input.Document.GitPath);
                return await Task.FromResult(true);
            }
            catch (UnauthorizedAccessException)
            {
                Logger.LogWarning("目录访问权限不足: {Path}", input.Document.GitPath);
                return false;
            }
        }
        catch (Exception ex)
        {
            Logger.LogWarning(ex, "目录结构生成步骤健康检查失败");
            return false;
        }
    }

    public override async Task<string[]> GetDependenciesAsync()
    {
        // 目录结构生成依赖README内容
        return new[] { "读取生成README" };
    }

    protected override void SetActivityTags(Activity? activity, DocumentProcessingContext input)
    {
        activity?.SetTag("warehouse.id", input.Warehouse.Id);
    }
}