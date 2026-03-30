using System.Diagnostics;
using KoalaWiki.Domains;
using KoalaWiki.Domains.Warehouse;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.BackendService;

public class WarehouseTask(
    ILogger<WarehouseTask> logger,
    IServiceProvider service)
    : BackgroundService
{
    private static readonly ActivitySource SActivitySource = new("KoalaWiki.Warehouse");

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        if (!DocumentOptions.EnableWiki)
        {
            logger.LogInformation("Wiki功能未启用，仓库处理任务停止运行。");
            return;
        }

        // 读取现有的仓库
        await Task.Delay(1000, stoppingToken);

        await using var scope = service.CreateAsyncScope();
        var dbContext = scope.ServiceProvider.GetService<IKoalaWikiContext>();
        var documentsService = scope.ServiceProvider.GetService<DocumentsService>();
        while (!stoppingToken.IsCancellationRequested)
        {
            var value = await dbContext!.Warehouses
                .Where(x => x.Status == WarehouseStatus.Pending || x.Status == WarehouseStatus.Processing)
                // 处理中优先
                .OrderByDescending(x => x.Status == WarehouseStatus.Processing)
                .FirstOrDefaultAsync(stoppingToken);

            if (value == null)
            {
                // 如果没有仓库，等待一段时间
                await Task.Delay(1000 * 5, stoppingToken);
                continue;
            }

            using var activity = SActivitySource.CreateActivity("仓库处理任务", ActivityKind.Server);
            activity?.SetTag("warehouse.id", value.Id);
            activity?.SetTag("warehouse.name", value.Name);
            activity?.SetTag("warehouse.type", value.Type);
            activity?.SetTag("warehouse.address", value.Address);
            activity?.SetTag("warehouse.status", value.Status.ToString());

            try
            {
                Document document;

                if (value?.Type?.Equals("git", StringComparison.OrdinalIgnoreCase) == true)
                {
                    activity?.SetTag("git.address", value.Address);
                    activity?.SetTag("git.branch", value?.Branch);
                    activity?.SetTag("git.has_username", !string.IsNullOrEmpty(value?.GitUserName));
                    activity?.SetTag("git.has_password", !string.IsNullOrEmpty(value?.GitPassword));

                    // 先拉取仓库
                    logger.LogInformation("开始拉取仓库：{Address}", value.Address);
                    var info = GitService.CloneRepository(value.Address, value?.GitUserName ?? string.Empty,
                        value?.GitPassword ?? string.Empty, value?.Branch);

                    logger.LogInformation("仓库拉取完成：{RepositoryName}, 分支：{BranchName}", info.RepositoryName,
                        info.BranchName);

                    activity?.SetTag("git.repository_name", info.RepositoryName);
                    activity?.SetTag("git.branch_name", info.BranchName);
                    activity?.SetTag("git.organization", info.Organization);
                    activity?.SetTag("git.version", info.Version);
                    activity?.SetTag("git.local_path", info.LocalPath);

                    // 判断是否组织名称和项目名称为空
                    if (string.IsNullOrEmpty(value.OrganizationName) && string.IsNullOrEmpty(value.Name))
                    {
                        await dbContext!.Warehouses.Where(x => x.Id == value.Id)
                            .ExecuteUpdateAsync(x =>
                                x.SetProperty(a => a.Name, info.RepositoryName)
                                    .SetProperty(x => x.Branch, info.BranchName)
                                    .SetProperty(x => x.Version, info.Version)
                                    .SetProperty(x => x.Status, WarehouseStatus.Processing)
                                    .SetProperty(x => x.OrganizationName, info.Organization), stoppingToken);
                    }
                    else
                    {
                        await dbContext!.Warehouses.Where(x => x.Id == value.Id)
                            .ExecuteUpdateAsync(x =>
                                x.SetProperty(x => x.Version, info.Version)
                                    .SetProperty(x => x.Status, WarehouseStatus.Processing), stoppingToken);
                    }

                    logger.LogInformation("更新仓库信息到数据库完成，仓库ID：{Id}", value.Id);

                    if (await dbContext.Documents.AnyAsync(x => x.WarehouseId == value.Id, stoppingToken))
                    {
                        document = await dbContext.Documents.FirstAsync(x => x.WarehouseId == value.Id,
                            stoppingToken);
                        
                        document.GitPath = info.LocalPath;
                        document.LastUpdate = DateTime.UtcNow;
                        document.Status = WarehouseStatus.Processing;
                        logger.LogInformation("获取现有文档记录，文档ID：{Id}", document.Id);
                    }
                    else
                    {
                        document = new Document
                        {
                            Id = Guid.NewGuid().ToString(),
                            WarehouseId = value.Id,
                            CreatedAt = DateTime.UtcNow,
                            LastUpdate = DateTime.UtcNow,
                            GitPath = info.LocalPath,
                            Status = WarehouseStatus.Pending
                        };
                        logger.LogInformation("创建文档记录，文档ID：{Id}", document.Id);
                        await dbContext.Documents.AddAsync(document, stoppingToken);
                        logger.LogInformation("添加新文档记录完成，文档ID：{Id}", document.Id);

                        await dbContext.SaveChangesAsync(stoppingToken);
                    }

                    logger.LogInformation("数据库更改保存完成，开始处理文档。");

                    // 调用文档处理服务，其Activity将作为当前Activity的子Activity
                    await documentsService.HandleAsync(document, value, dbContext,
                        value.Address.Replace(".git", string.Empty)).ConfigureAwait(false);
                }
                else if (value?.Type?.Equals("file", StringComparison.OrdinalIgnoreCase) == true)
                {
                    activity?.SetTag("file.address", value.Address);

                    await dbContext!.Warehouses.Where(x => x.Id == value.Id)
                        .ExecuteUpdateAsync(x => x.SetProperty(x => x.Status, WarehouseStatus.Processing),
                            stoppingToken);

                    logger.LogInformation("更新仓库信息到数据库完成，仓库ID：{Id}", value.Id);

                    if (await dbContext.Documents.AnyAsync(x => x.WarehouseId == value.Id, stoppingToken))
                    {
                        document = await dbContext.Documents.FirstAsync(x => x.WarehouseId == value.Id,
                            stoppingToken);
                        logger.LogInformation("获取现有文档记录，文档ID：{Id}", document.Id);
                    }
                    else
                    {
                        document = new Document
                        {
                            Id = Guid.NewGuid().ToString(),
                            WarehouseId = value.Id,
                            CreatedAt = DateTime.UtcNow,
                            LastUpdate = DateTime.UtcNow,
                            GitPath = value.Address,
                            Status = WarehouseStatus.Pending
                        };
                        logger.LogInformation("创建文档记录，文档ID：{Id}", document.Id);
                        await dbContext.Documents.AddAsync(document, stoppingToken);
                        logger.LogInformation("添加新文档记录完成，文档ID：{Id}", document.Id);

                        await dbContext.SaveChangesAsync(stoppingToken);
                    }

                    logger.LogInformation("数据库更改保存完成，开始处理文档。");

                    // 调用文档处理服务，其Activity将作为当前Activity的子Activity
                    await documentsService.HandleAsync(document, value, dbContext,
                        value.Address.Replace(".git", string.Empty)).ConfigureAwait(false);
                }
                else
                {
                    activity?.SetTag("error", "不支持的仓库类型");
                    logger.LogError("不支持的仓库类型：{Type}", value.Type);
                    await dbContext.Warehouses.Where(x => x.Id == value.Id)
                        .ExecuteUpdateAsync(x => x.SetProperty(a => a.Status, WarehouseStatus.Failed)
                            .SetProperty(x => x.Error, "不支持的仓库类型"), stoppingToken);

                    logger.LogInformation("更新仓库状态为失败，仓库地址：{address}", value.Address);
                    activity?.SetTag("warehouse.final_status", "failed");
                    return;
                }

                logger.LogInformation("文档处理完成，仓库地址：{address}", value.Address);

                // 更新仓库状态为完成
                activity?.SetTag("document.id", document.Id);

                await dbContext.Warehouses.Where(x => x.Id == value.Id)
                    .ExecuteUpdateAsync(x => x.SetProperty(a => a.Status, WarehouseStatus.Completed)
                        .SetProperty(x => x.Error, string.Empty), stoppingToken);

                logger.LogInformation("更新仓库状态为完成，仓库地址：{address}", value.Address);

                // 提交更改
                await dbContext.Documents.Where(x => x.Id == document.Id)
                    .ExecuteUpdateAsync(x => x.SetProperty(a => a.LastUpdate, DateTime.UtcNow)
                        .SetProperty(a => a.Status, WarehouseStatus.Completed), stoppingToken);

                logger.LogInformation("文档状态更新为完成，仓库地址：{address}", value.Address);

                activity?.SetTag("processing.success", true);
                activity?.SetTag("warehouse.final_status", "completed");
            }
            catch (Exception e)
            {
                activity?.SetTag("error.message", e.Message);
                activity?.SetTag("error.type", e.GetType().Name);
                activity?.SetTag("error.occurred", true);
                activity?.SetTag("warehouse.final_status", "failed");

                logger.LogError("发生错误：{e}", e);
                await Task.Delay(1000 * 5, stoppingToken);

                await dbContext.Warehouses.Where(x => x.Id == value.Id)
                    .ExecuteUpdateAsync(x => x.SetProperty(a => a.Status, WarehouseStatus.Failed)
                        .SetProperty(x => x.Error, e.ToString()), stoppingToken);
            }
        }
    }
}