using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Infrastructure;
using Microsoft.EntityFrameworkCore;
using LibGit2Sharp;

namespace KoalaWiki.Services;

/// <summary>
/// 仓库同步服务
/// </summary>
public interface IWarehouseSyncService
{
    Task<bool> SyncWarehouseAsync(string warehouseId, WarehouseSyncTrigger trigger);
}

public class WarehouseSyncService : IWarehouseSyncService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<WarehouseSyncService> _logger;
    private readonly IWarehouseSyncExecutor _syncExecutor;

    public WarehouseSyncService(
        IServiceProvider serviceProvider,
        ILogger<WarehouseSyncService> logger,
        IWarehouseSyncExecutor syncExecutor)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
        _syncExecutor = syncExecutor;
    }

    public async Task<bool> SyncWarehouseAsync(string warehouseId, WarehouseSyncTrigger trigger)
    {
        using var scope = _serviceProvider.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<IKoalaWikiContext>();

        // 检查仓库是否存在
        var warehouse = await dbContext.Warehouses
            .FirstOrDefaultAsync(x => x.Id == warehouseId);

        if (warehouse == null)
        {
            _logger.LogWarning("仓库 {WarehouseId} 不存在", warehouseId);
            return false;
        }

        // 检查文档是否存在
        var document = await dbContext.Documents
            .FirstOrDefaultAsync(x => x.WarehouseId == warehouseId);

        if (document == null)
        {
            _logger.LogWarning("仓库 {WarehouseId} 的文档不存在", warehouseId);
            return false;
        }

        // 创建同步记录
        var syncRecord = new WarehouseSyncRecord
        {
            Id = Guid.NewGuid().ToString(),
            WarehouseId = warehouseId,
            Status = WarehouseSyncStatus.InProgress,
            StartTime = DateTime.UtcNow,
            FromVersion = warehouse.Version,
            FileCount = 0,
            UpdatedFileCount = 0,
            AddedFileCount = 0,
            DeletedFileCount = 0,
            Trigger = trigger,
            CreatedAt = DateTime.UtcNow
        };

        await dbContext.WarehouseSyncRecords.AddAsync(syncRecord);
        await dbContext.SaveChangesAsync();

        _logger.LogInformation("开始同步仓库 {WarehouseId}，触发方式: {Trigger}", warehouseId, trigger);

        // 异步执行同步任务
        _ = Task.Run(async () =>
        {
            using var taskScope = _serviceProvider.CreateScope();
            var taskDbContext = taskScope.ServiceProvider.GetRequiredService<IKoalaWikiContext>();

            try
            {
                // 执行同步逻辑
                var commitId = await _syncExecutor.ExecuteSyncAsync(warehouseId);

                if (string.IsNullOrEmpty(commitId))
                {
                    // 没有新的提交
                    _logger.LogInformation("仓库 {WarehouseId} 没有新的提交需要同步", warehouseId);

                    syncRecord.Status = WarehouseSyncStatus.Success;
                    syncRecord.EndTime = DateTime.UtcNow;
                    syncRecord.ErrorMessage = "没有新的提交需要同步";
                }
                else
                {
                    // 同步成功
                    _logger.LogInformation("仓库 {WarehouseId} 同步成功，新版本: {CommitId}", warehouseId, commitId);

                    syncRecord.Status = WarehouseSyncStatus.Success;
                    syncRecord.EndTime = DateTime.UtcNow;
                    syncRecord.ToVersion = commitId;

                    // 计算文件变更统计（这里需要根据实际情况完善）
                    syncRecord.FileCount = 1; // TODO: 实际统计
                    syncRecord.UpdatedFileCount = 1;
                }

                // 更新同步记录
                taskDbContext.WarehouseSyncRecords.Update(syncRecord);

                // 更新文档最后更新时间
                await taskDbContext.Documents
                    .Where(x => x.WarehouseId == warehouseId)
                    .ExecuteUpdateAsync(x => x.SetProperty(a => a.LastUpdate, DateTime.Now));

                // 如果有新版本，更新仓库版本
                if (!string.IsNullOrEmpty(commitId))
                {
                    await taskDbContext.Warehouses
                        .Where(x => x.Id == warehouseId)
                        .ExecuteUpdateAsync(x => x.SetProperty(a => a.Version, commitId));
                }

                await taskDbContext.SaveChangesAsync();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "同步仓库 {WarehouseId} 失败", warehouseId);

                // 更新失败状态
                syncRecord.Status = WarehouseSyncStatus.Failed;
                syncRecord.EndTime = DateTime.UtcNow;
                syncRecord.ErrorMessage = ex.Message;

                taskDbContext.WarehouseSyncRecords.Update(syncRecord);
                await taskDbContext.SaveChangesAsync();
            }
        });

        return true;
    }
}