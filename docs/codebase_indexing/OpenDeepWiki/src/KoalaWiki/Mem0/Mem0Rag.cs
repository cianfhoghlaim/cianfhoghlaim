using System.Net.Http.Headers;
using KoalaWiki.Core.Extensions;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Prompts;
using Mem0.NET;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Mem0;

public class Mem0Rag(IServiceProvider service, ILogger<Mem0Rag> logger) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await Task.Delay(100, stoppingToken);

        if (OpenAIOptions.EnableMem0 == false)
        {
            logger.LogWarning("Mem0功能未启用,");
            return;
        }


        while (!stoppingToken.IsCancellationRequested)
        {
            // 读取现有的仓库
            await using var scope = service.CreateAsyncScope();
            var dbContext = scope.ServiceProvider.GetService<IKoalaWikiContext>();

            var warehouse = await dbContext!.Warehouses
                .Where(x => x.Status == WarehouseStatus.Completed && x.IsEmbedded == false)
                .FirstOrDefaultAsync(stoppingToken);

            if (warehouse == null)
            {
                logger.LogInformation("暂时无需处理文档，等待30s");
                // 如果没有仓库，等待一段时间
                await Task.Delay(1000 * 30, stoppingToken);
                continue;
            }

            var documents = await dbContext.Documents
                .Where(x => x.WarehouseId == warehouse.Id)
                .FirstOrDefaultAsync(stoppingToken);

            var files = DocumentsHelper.GetCatalogueFiles(documents.GitPath);

            var client = new Mem0Client(OpenAIOptions.Mem0ApiKey, OpenAIOptions.Mem0Endpoint, null, null,
                new HttpClient()
                {
                    Timeout = TimeSpan.FromMinutes(600),
                    DefaultRequestHeaders =
                    {
                        UserAgent = { new ProductInfoHeaderValue("KoalaWiki", "1.0") }
                    }
                });

            var catalogs = await dbContext.DocumentCatalogs
                .Where(x => x.DucumentId == documents.Id && x.IsCompleted == true && x.IsDeleted == false)
                .ToListAsync(stoppingToken);

            var parallelOptions = new ParallelOptions
            {
                CancellationToken = stoppingToken,
                MaxDegreeOfParallelism = 3 // 可根据需要调整并发数
            };

            await Parallel.ForEachAsync(catalogs, parallelOptions, async (catalog, ct) =>
            {
                await using var innerScope = service.CreateAsyncScope();
                var innerDbContext = innerScope.ServiceProvider.GetService<IKoalaWikiContext>();

                int retryCount = 0;
                const int maxRetries = 3;
                while (retryCount < maxRetries)
                {
                    try
                    {
                        var content = await innerDbContext!.DocumentFileItems
                            .Where(x => x.DocumentCatalogId == catalog.Id)
                            .FirstOrDefaultAsync(cancellationToken: ct);

                        if (content == null || string.IsNullOrWhiteSpace(content.Content))
                        {
                            logger.LogWarning("目录 {Catalog} 内容为空，跳过", catalog);
                            return;
                        }

                        // 获取依赖文件
                        var dependentFiles = await innerDbContext.DocumentFileItemSources
                            .Where(x => x.DocumentFileItemId == content.Id)
                            .Select(x => new
                            {
                                x.DocumentFileItemId,
                                x.Address,
                                x.Name,
                                x.Id,
                                x.CreatedAt
                            })
                            .ToListAsync(cancellationToken: ct);

                        // 处理目录内容
                        await client.AddAsync([
                                new Message
                                {
                                    Role = "system",
                                    Content = await PromptContext.Mem0(nameof(PromptConstant.Mem0.DocsSystem),
                                        new KernelArguments(), OpenAIOptions.ChatModel)
                                },
                                new Message
                                {
                                    Role = "user",
                                    Content = $"""
                                               # {catalog.Name}
                                               <file name="{catalog.Url}">
                                               {content.Content}
                                               </file>
                                               """
                                }
                            ], userId: warehouse.Id, metadata: new Dictionary<string, object>()
                            {
                                { "id", catalog.Id },
                                { "name", catalog.Name },
                                { "url", catalog.Url },
                                { "documentId", documents.Id },
                                { "type", "docs" },
                                { "reference", dependentFiles }
                            },
                            memoryType: "procedural_memory", cancellationToken: ct);
                        break; // 成功则跳出重试循环
                    }
                    catch (Exception ex)
                    {
                        retryCount++;
                        if (retryCount >= maxRetries)
                        {
                            logger.LogError(ex, "处理目录 {Catalog} 时发生错误，已重试 {RetryCount} 次", catalog, retryCount);
                        }
                        else
                        {
                            logger.LogWarning(ex, "处理目录 {Catalog} 时发生错误，重试第 {RetryCount} 次", catalog, retryCount);
                            await Task.Delay(1000 * retryCount, ct); // 指数退避
                        }
                    }
                }
            });

            var fileParallelOptions = new ParallelOptions
            {
                CancellationToken = stoppingToken,
                MaxDegreeOfParallelism = 3 // 可根据需要调整并发数
            };

            int fileFailureCount = 0;
            const int fileFailureThreshold = 5; // 熔断阈值
            bool circuitBroken = false;

            await Parallel.ForEachAsync(files, fileParallelOptions, async (file, ct) =>
            {
                if (circuitBroken)
                    return;

                try
                {
                    // 读取文件内容
                    var content = await File.ReadAllTextAsync(file.Path, ct);

                    if (string.IsNullOrWhiteSpace(content))
                    {
                        logger.LogWarning("文件 {File} 内容为空，跳过", file.Path);
                        return;
                    }

                    // 处理文件内容
                    await client.AddAsync([
                        new Message()
                        {
                            Role = "system",
                            Content = await PromptContext.Mem0(nameof(PromptConstant.Mem0.CodeSystem),
                                new KernelArguments(), OpenAIOptions.ChatModel)
                        },
                        new Message
                        {
                            Role = "user",
                            Content = $"""
                                       ```{file.Path.Replace(documents.GitPath, "").TrimStart("/").TrimStart('\\')}
                                       {content}
                                       ```
                                       """
                        }
                    ], userId: warehouse.Id, memoryType: "procedural_memory", metadata: new Dictionary<string, object>()
                    {
                        { "fileName", file.Name },
                        { "filePath", file.Path },
                        { "fileType", file.Type },
                        { "type", "code" },
                        { "documentId", documents.Id },
                    }, cancellationToken: ct);
                }
                catch (Exception ex)
                {
                    Interlocked.Increment(ref fileFailureCount);
                    logger.LogError(ex, "处理文件 {File} 时发生错误", file);

                    if (fileFailureCount >= fileFailureThreshold)
                    {
                        logger.LogError("文件处理连续失败超过阈值，触发熔断，停止后续处理。");
                        circuitBroken = true;
                    }
                }
            });

            await dbContext.Warehouses
                .Where(x => x.Id == warehouse.Id)
                .ExecuteUpdateAsync(x => x.SetProperty(a => a.IsEmbedded, true), stoppingToken);
        }
    }
}