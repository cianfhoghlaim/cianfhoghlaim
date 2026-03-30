using System.Diagnostics;

namespace KoalaWiki.KoalaWarehouse.Pipeline;

public class DocumentProcessingOrchestrator(
    IDocumentProcessingPipeline pipeline,
    ILogger<DocumentProcessingOrchestrator> logger)
    : IDocumentProcessingOrchestrator
{
    private readonly ActivitySource _activitySource = new("KoalaWiki.Warehouse.Orchestrator");

    public async Task<DocumentProcessingResult> ProcessDocumentAsync(
        Document document,
        Warehouse warehouse,
        IKoalaWikiContext dbContext,
        string gitRepository,
        CancellationToken cancellationToken = default)
    {
        using var activity = _activitySource.StartActivity("ProcessDocument", ActivityKind.Server);
        
        // 设置活动标签
        activity?.SetTag("warehouse.id", warehouse.Id);
        activity?.SetTag("warehouse.name", warehouse.Name);
        activity?.SetTag("document.id", document.Id);
        activity?.SetTag("git.repository", gitRepository);

        logger.LogInformation("开始处理文档，仓库: {WarehouseName} ({WarehouseId}), Git仓库: {GitRepository}", 
            warehouse.Name, warehouse.Id, gitRepository);

        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            // 创建处理命令
            var command = new DocumentProcessingCommand
            {
                Document = document,
                Warehouse = warehouse,
                GitRepository = gitRepository,
                DbContext = dbContext
            };

            // 执行管道处理
            var result = await pipeline.ExecuteAsync(command, cancellationToken);
            
            stopwatch.Stop();
            
            if (result.Success)
            {
                activity?.SetTag("processing.completed", true);
                activity?.SetTag("processing.duration_ms", stopwatch.ElapsedMilliseconds);
                
                logger.LogInformation("文档处理成功完成，仓库: {WarehouseName}，耗时: {Duration}ms", 
                    warehouse.Name, stopwatch.ElapsedMilliseconds);
            }
            else
            {
                activity?.SetTag("processing.failed", true);
                activity?.SetTag("error.message", result.ErrorMessage);
                
                logger.LogError("文档处理失败，仓库: {WarehouseName}，错误: {Error}", 
                    warehouse.Name, result.ErrorMessage);
                
                if (result.Exception != null)
                {
                    logger.LogError(result.Exception, "处理异常详情");
                }
            }

            return result;
        }
        catch (OperationCanceledException)
        {
            stopwatch.Stop();
            activity?.SetTag("processing.cancelled", true);
            
            logger.LogWarning("文档处理被取消，仓库: {WarehouseName}，已运行: {Duration}ms", 
                warehouse.Name, stopwatch.ElapsedMilliseconds);
            
            return DocumentProcessingResult.CreateFailure("处理被取消");
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            activity?.SetTag("processing.exception", true);
            activity?.SetTag("exception.type", ex.GetType().Name);
            activity?.SetTag("exception.message", ex.Message);
            
            logger.LogError(ex, "文档处理过程中发生未处理的异常，仓库: {WarehouseName}", warehouse.Name);
            
            return DocumentProcessingResult.CreateFailure(
                $"处理过程中发生异常: {ex.Message}", 
                ex);
        }
    }
}