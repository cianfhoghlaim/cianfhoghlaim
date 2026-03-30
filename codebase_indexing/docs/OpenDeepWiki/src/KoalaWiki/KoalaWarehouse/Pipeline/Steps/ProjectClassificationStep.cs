using System.Diagnostics;

namespace KoalaWiki.KoalaWarehouse.Pipeline.Steps;

public class ProjectClassificationStep(ILogger<ProjectClassificationStep> logger)
    : DocumentProcessingStepBase<DocumentProcessingContext, DocumentProcessingContext>(logger)
{
    public override string StepName => "读取或生成项目类别";

    public override async Task<DocumentProcessingContext> ExecuteAsync(DocumentProcessingContext context,
        CancellationToken cancellationToken = default)
    {
        using var activity = ActivitySource.StartActivity(StepName);
        SetActivityTags(activity, context);

        Logger.LogInformation("开始执行 {StepName} 步骤", StepName);

        try
        {
            ClassifyType? classify;

            if (context.Warehouse.Classify.HasValue)
            {
                classify = context.Warehouse.Classify;
                Logger.LogInformation("使用现有项目分类: {Classify}", classify);
            }
            else
            {
                Logger.LogInformation("生成新的项目分类");

                classify = await WarehouseClassify.ClassifyAsync(
                    context.Catalogue ?? string.Empty,
                    context.Readme ?? string.Empty);
                // 更新数据库
                await context.DbContext.Warehouses.Where(x => x.Id == context.Warehouse.Id)
                    .ExecuteUpdateAsync(x => x.SetProperty(y => y.Classify, classify),
                        cancellationToken: cancellationToken);
            }

            context.Classification = classify;
            activity?.SetTag("classify", classify?.ToString());

            context.SetStepResult(StepName, classify);

            Logger.LogInformation("完成 {StepName} 步骤，分类结果: {Classify}",
                StepName, classify?.ToString());
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
    }
}