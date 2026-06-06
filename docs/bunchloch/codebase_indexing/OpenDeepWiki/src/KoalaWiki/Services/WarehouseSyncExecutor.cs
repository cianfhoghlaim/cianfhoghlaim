using KoalaWiki.BackendService;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains;
using KoalaWiki.Domains.Warehouse;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Services;

/// <summary>
/// 仓库同步执行器 - 负责实际执行同步逻辑
/// </summary>
public interface IWarehouseSyncExecutor
{
    Task<string?> ExecuteSyncAsync(string warehouseId);
}

public class WarehouseSyncExecutor : IWarehouseSyncExecutor
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<WarehouseSyncExecutor> _logger;

    public WarehouseSyncExecutor(
        IServiceProvider serviceProvider,
        ILogger<WarehouseSyncExecutor> logger)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    public async Task<string?> ExecuteSyncAsync(string warehouseId)
    {
        using var scope = _serviceProvider.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<IKoalaWikiContext>();

        // 获取仓库信息
        var warehouse = await dbContext.Warehouses
            .FirstOrDefaultAsync(x => x.Id == warehouseId);

        if (warehouse == null)
        {
            _logger.LogWarning("仓库 {WarehouseId} 不存在", warehouseId);
            return null;
        }

        // 获取文档信息
        var document = await dbContext.Documents
            .FirstOrDefaultAsync(x => x.WarehouseId == warehouseId);

        if (document == null)
        {
            _logger.LogWarning("仓库 {WarehouseId} 的文档不存在", warehouseId);
            return null;
        }

        // 获取WarehouseProcessingTask实例并调用HandleAnalyseAsync
        var processingTask = scope.ServiceProvider.GetRequiredService<WarehouseProcessingTask>();
        var commitId = await processingTask.HandleAnalyseAsync(warehouse, document, dbContext);

        return commitId;
    }
}