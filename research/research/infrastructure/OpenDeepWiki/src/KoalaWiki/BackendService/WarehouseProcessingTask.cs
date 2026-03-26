using KoalaWiki.Domains.Warehouse;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.BackendService;

public partial class WarehouseProcessingTask(IServiceProvider service, ILogger<WarehouseProcessingTask> logger)
    : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await Task.Delay(1000, stoppingToken);

        if (!DocumentOptions.EnableIncrementalUpdate)
        {
            logger.LogWarning("增量更新未启用，跳过增量更新任务");
            return;
        }

        // 读取环境变量，获取更新间隔
        var updateInterval = 5;
        if (int.TryParse(Environment.GetEnvironmentVariable("UPDATE_INTERVAL"), out var interval))
        {
            updateInterval = interval;
        }

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                // 1. 读取现有的仓库状态=2
                await using var scope = service.CreateAsyncScope();

                var dbContext = scope.ServiceProvider.GetService<IKoalaWikiContext>();

                // 读取现有的仓库状态=2，并且启用了同步，并且处理时间满足一星期
                var warehouse = await dbContext!.Warehouses
                    .Where(x => x.Status == WarehouseStatus.Completed && x.EnableSync)
                    .FirstOrDefaultAsync(stoppingToken);

                if (warehouse == null)
                {
                    // 如果没有仓库，等待一段时间后重试
                    await Task.Delay(1000 * 60, stoppingToken);
                    continue;
                }

                var documents = await dbContext.Documents
                    .Where(x => warehouse.Id == x.WarehouseId && x.LastUpdate < DateTime.Now.AddDays(-updateInterval))
                    .ToListAsync(stoppingToken);

                var warehouseIds = documents.Select(x => x.WarehouseId).ToArray();

                // 从这里得到了超过一星期没更新的仓库
                warehouse = await dbContext.Warehouses
                    .Where(x => warehouseIds.Contains(x.Id))
                    .FirstOrDefaultAsync(stoppingToken);

                if (warehouse == null)
                {
                    await Task.Delay(1000 * 60, stoppingToken);
                }
                else
                {
                    var document = documents.FirstOrDefault(x => x.WarehouseId == warehouse.Id);

                    // 创建同步记录
                    var syncRecord = new WarehouseSyncRecord
                    {
                        Id = Guid.NewGuid().ToString(),
                        WarehouseId = warehouse.Id,
                        Status = WarehouseSyncStatus.InProgress,
                        StartTime = DateTime.UtcNow,
                        FromVersion = warehouse.Version,
                        FileCount = documents.Count,
                        Trigger = WarehouseSyncTrigger.Auto
                    };

                    await dbContext.WarehouseSyncRecords.AddAsync(syncRecord, stoppingToken);
                    await dbContext.SaveChangesAsync(stoppingToken);

                    try
                    {
                        var commitId = await HandleAnalyseAsync(warehouse, document, dbContext);

                        if (string.IsNullOrEmpty(commitId))
                        {
                            // 同步失败，更新记录状态
                            syncRecord.Status = WarehouseSyncStatus.Failed;
                            syncRecord.EndTime = DateTime.UtcNow;
                            syncRecord.ErrorMessage = "同步过程中未获取到新的提交ID";

                            // 更新git记录
                            await dbContext.Documents
                                .Where(x => x.WarehouseId == warehouse.Id)
                                .ExecuteUpdateAsync(x => x.SetProperty(a => a.LastUpdate, DateTime.Now), stoppingToken);

                            await dbContext.SaveChangesAsync(stoppingToken);
                            return;
                        }

                        // 同步成功，更新记录状态
                        syncRecord.Status = WarehouseSyncStatus.Success;
                        syncRecord.EndTime = DateTime.UtcNow;
                        syncRecord.ToVersion = commitId;

                        // 更新git记录
                        await dbContext.Documents
                            .Where(x => x.WarehouseId == warehouse.Id)
                            .ExecuteUpdateAsync(x => x.SetProperty(a => a.LastUpdate, DateTime.Now), stoppingToken);

                        await dbContext.Warehouses.Where(x => x.Id == warehouse.Id)
                            .ExecuteUpdateAsync(x => x.SetProperty(a => a.Version, commitId), stoppingToken);

                        await dbContext.SaveChangesAsync(stoppingToken);
                    }
                    catch (Exception ex)
                    {
                        // 同步异常，更新记录状态
                        syncRecord.Status = WarehouseSyncStatus.Failed;
                        syncRecord.EndTime = DateTime.UtcNow;
                        syncRecord.ErrorMessage = ex.Message;
                        await dbContext.SaveChangesAsync(stoppingToken);
                        throw;
                    }
                }
            }
            catch (Exception exception)
            {
                logger.LogError(exception, "处理仓库失败");

                await Task.Delay(1000 * 60, stoppingToken);
            }
        }
    }
}