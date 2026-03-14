using System.Diagnostics;
using KoalaWiki.KoalaWarehouse.DocumentPending;
using KoalaWiki.Options;

namespace KoalaWiki.KoalaWarehouse.Pipeline.Steps;

public class DocumentContentGenerationStep(ILogger<DocumentContentGenerationStep> logger)
    : DocumentProcessingStepBase<DocumentProcessingContext, DocumentProcessingContext>(logger)
{
    public override string StepName => "生成目录结构中的文档";

    public override async Task<DocumentProcessingContext> ExecuteAsync(DocumentProcessingContext context,
        CancellationToken cancellationToken = default)
    {
        using var activity = ActivitySource.StartActivity(StepName);
        SetActivityTags(activity, context);

        Logger.LogInformation("开始执行 {StepName} 步骤", StepName);

        try
        {
            if (context.DocumentCatalogs == null || !context.DocumentCatalogs.Any())
            {
                Logger.LogWarning("没有文档目录需要生成内容");
                return context;
            }

            // 确保有文件内核实例
            if (context.FileKernelInstance == null)
            {
                context.FileKernelInstance = await KernelFactory.GetKernel(
                    OpenAIOptions.Endpoint,
                    OpenAIOptions.ChatApiKey, 
                    context.Document.GitPath, 
                    OpenAIOptions.ChatModel, 
                    false);
            }

            await DocumentPendingService.HandlePendingDocumentsAsync(
                context.DocumentCatalogs, 
                context.FileKernelInstance, 
                context.Catalogue ?? string.Empty,
                context.GitRepository,
                context.Warehouse, 
                context.Document.GitPath, 
                context.DbContext, 
                context.Classification);

            activity?.SetTag("documents.processed", context.DocumentCatalogs.Count);
            context.SetStepResult(StepName, context.DocumentCatalogs.Count);
            
            Logger.LogInformation("完成 {StepName} 步骤，处理文档数量: {Count}", 
                StepName, context.DocumentCatalogs.Count);
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "执行 {StepName} 步骤时发生错误", StepName);
            activity?.SetTag("error", ex.Message);
            throw;
        }

        return context;
    }

    protected override void SetActivityTags(Activity? activity, DocumentProcessingContext input)
    {
        activity?.SetTag("warehouse.id", input.Warehouse.Id);
        activity?.SetTag("documents.count", input.DocumentCatalogs?.Count ?? 0);
    }
}