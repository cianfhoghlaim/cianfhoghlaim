using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using KoalaWiki.Domains;
using KoalaWiki.Domains.DocumentFile;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.KoalaWarehouse.DocumentPending;
using LibGit2Sharp;
using Microsoft.EntityFrameworkCore;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Newtonsoft.Json;
using Polly;
using JsonSerializer = System.Text.Json.JsonSerializer;

namespace KoalaWiki.BackendService;

public partial class WarehouseProcessingTask
{
    public async Task<string> HandleAnalyseAsync(Warehouse warehouse, Document? document, IKoalaWikiContext dbContext)
    {
        try
        {
            logger.LogInformation("步骤1: 开始更新仓库 {GitPath}", document.GitPath);

            // 1. 更新仓库
            var (commits, commitId) = GitService.PullRepository(document.GitPath, warehouse.Version,
                warehouse.Branch, warehouse.GitUserName, warehouse.GitPassword);

            logger.LogInformation("仓库更新完成，获取到 {CommitCount} 个提交记录", commits?.Count ?? 0);
            if (commits == null || commits.Count == 0)
            {
                logger.LogInformation("没有更新的提交记录");
                return string.Empty;
            }

            // 得到更新内容和更新文件
            var commitPrompt = new StringBuilder();
            if (commits is { Count: > 0 })
            {
                using var repo = new Repository(document.GitPath);

                foreach (var commitItem in commits.Select(commit => repo.Lookup<Commit>(commit.Sha)))
                {
                    commitPrompt.AppendLine($"<commit>\n{commitItem.Message}");
                    // 获取当前更新的文件列表
                    if (commitItem.Parents.Any())
                    {
                        var parent = commitItem.Parents.First();
                        var comparison = repo.Diff.Compare<TreeChanges>(parent.Tree, commitItem.Tree);

                        foreach (var change in comparison)
                        {
                            commitPrompt.AppendLine($" - {change.Status}: {change.Path}");
                        }
                    }

                    commitPrompt.AppendLine("</commit>");
                }
            }
            else
            {
                logger.LogInformation("没有更新的提交记录");

                // 如果没有更新的提交记录，直接返回
                return string.Empty;
            }


            logger.LogInformation("步骤2: 获取文档目录");
            var catalogues = await dbContext.DocumentCatalogs
                .AsNoTracking()
                .Where(x => x.WarehouseId == warehouse.Id)
                .ToListAsync();
            logger.LogInformation("获取到 {CatalogCount} 个目录项", catalogues.Count);

            logger.LogInformation("步骤3: 创建内核并准备分析");

            // 先得到树形结构
            var kernel = await KernelFactory.GetKernel(OpenAIOptions.Endpoint,
                OpenAIOptions.ChatApiKey, document.GitPath, OpenAIOptions.ChatModel, false);

            var chatCompletion = kernel.GetRequiredService<IChatCompletionService>();

            var history = new ChatHistory();

            var prompt = Prompt.AnalyzeNewCatalogue
                .Replace("{{git_repository}}", warehouse.Address.Replace(".git", ""))
                .Replace("{{document_catalogue}}", JsonSerializer.Serialize(catalogues, JsonSerializerOptions.Web))
                .Replace("{{git_commit}}", commitPrompt.ToString())
                .Replace("{{catalogue}}", document.GetCatalogueSmartFilterOptimized());

            history.AddUserMessage(prompt);

            logger.LogInformation("步骤4: 开始执行AI分析");

            var st = new StringBuilder();

            // 使用 Polly 创建重试策略
            var retryPolicy = Policy
                .Handle<Exception>() // 处理所有异常
                .WaitAndRetryAsync(
                    retryCount: 3, // 最大重试次数
                    sleepDurationProvider: retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)), // 指数退避策略
                    onRetry: (exception, timeSpan, retryCount, context) =>
                    {
                        logger.LogWarning("第 {RetryCount} 次重试分析", retryCount);
                        logger.LogError(exception, "AI分析失败 (尝试 {RetryCount}/3): {ErrorMessage}",
                            retryCount, exception.Message);
                        logger.LogInformation("等待 {Delay} 秒后重试", timeSpan.TotalSeconds);
                    }
                );

            // 执行带有重试策略的异步操作
            var result = await retryPolicy.ExecuteAsync(async () =>
            {
                st.Clear();

                await foreach (var item in chatCompletion.GetStreamingChatMessageContentsAsync(history,
                                   new OpenAIPromptExecutionSettings()
                                   {
                                       MaxTokens = DocumentsHelper.GetMaxTokens(OpenAIOptions.AnalysisModel),
                                       Temperature = 0.3,
                                   }, kernel))
                {
                    if (!string.IsNullOrEmpty(item.Content))
                    {
                        st.Append(item.Content);
                    }
                }

                logger.LogInformation("AI分析成功完成");

                // 正则表达式提取<document_structure></document_structure>
                var regex = new Regex(@"<document_structure>(.*?)</document_structure>", RegexOptions.Singleline);
                var match = regex.Match(st.ToString());
                if (match.Success)
                {
                    st.Clear();
                    st.Append(match.Groups[1].Value);
                }

                // 正则表达式提取```json
                var jsonRegex = new Regex(@"```json(.*?)```", RegexOptions.Singleline);
                var jsonMatch = jsonRegex.Match(st.ToString());
                if (jsonMatch.Success)
                {
                    st.Clear();
                    st.Append(jsonMatch.Groups[1].Value);
                }

                // 解析
                var result = JsonConvert.DeserializeObject<WareHouseCatalogue>(st.ToString());

                return result;
            });

            logger.LogInformation("步骤5: 处理分析结果，长度为 {ResultLength} 字符", st.Length);

            // 这里可以继续处理分析结果

            await dbContext.DocumentCatalogs.Where(x => result.delete_id.Contains(x.Id))
                .ExecuteUpdateAsync(x =>
                    x.SetProperty(a => a.IsDeleted, true)
                        .SetProperty(a => a.DeletedTime, DateTime.Now));


            var documents = new List<(WareHouseCatalogueType, DocumentCatalog)>();
            ProcessCatalogueItems(result.items.ToList(), null, warehouse, document, documents);

            logger.LogInformation("步骤6: 更新文档目录");

            foreach (var tuple in documents)
            {
                if (tuple.Item1 == WareHouseCatalogueType.Update)
                {
                    // 需要先删除现有的
                    await dbContext.DocumentCatalogs
                        .Where(x => x.WarehouseId == warehouse.Id && x.Id == tuple.Item2.Id)
                        .ExecuteUpdateAsync(x => x.SetProperty(a => a.IsDeleted, true)
                            .SetProperty(a => a.DeletedTime, DateTime.UtcNow));
                }
            }

            var fileKernel =await  KernelFactory.GetKernel(OpenAIOptions.Endpoint, OpenAIOptions.ChatApiKey, document.GitPath,
                OpenAIOptions.ChatModel, false);

            foreach (var valueTuple in documents)
            {
                if (valueTuple.Item2.Id == null)
                {
                    valueTuple.Item2.Id = Guid.NewGuid().ToString("N") + valueTuple.Item2.Url;
                }
            }

            await DocumentPendingService.HandlePendingDocumentsAsync(documents.Select(x => x.Item2).ToList(),
                fileKernel,
                document.GetCatalogueSmartFilterOptimized(),
                warehouse.Address, warehouse, document.GitPath, dbContext, warehouse.Classify);

            logger.LogInformation("仓库 {WarehouseName} 分析完成", warehouse.Name);

            var readme = await DocumentsHelper.ReadMeFile(document.GitPath);

            var commitResult = await GenerateUpdateLogAsync(document.GitPath, warehouse,
                readme, warehouse.Address, warehouse.Branch, dbContext);

            await dbContext.DocumentCommitRecords.AddRangeAsync(commitResult.Select(x => new DocumentCommitRecord()
            {
                WarehouseId = warehouse.Id,
                CreatedAt = DateTime.Now,
                Author = string.Empty,
                Id = Guid.NewGuid().ToString("N"),
                CommitMessage = x.description,
                Title = x.title,
                LastUpdate = x.date,
            }));

            await dbContext.SaveChangesAsync();


            return commitId;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "仓库分析过程中发生异常: {ErrorMessage}", ex.Message);
            throw;
        }
    }


    private static void ProcessCatalogueItems(List<WareHouseCatalogueItems> items, string? parentId,
        Warehouse warehouse,
        Document document, List<(WareHouseCatalogueType, DocumentCatalog)>? documents)
    {
        int order = 0; // 创建排序计数器
        foreach (var item in items)
        {
            item.title = item.title.Replace(" ", "");
            var documentItem = new DocumentCatalog
            {
                WarehouseId = warehouse.Id,
                Description = item.title,
                Id = item.Id,
                Name = item.name,
                Url = item.title,
                DucumentId = document.Id,
                ParentId = parentId,
                Prompt = item.prompt,
                Order = order++ // 为当前层级的每个项目设置顺序值并递增
            };
            if (item.type == "update")
            {
                documents.Add((WareHouseCatalogueType.Update, documentItem));
            }
            else
            {
                documents.Add((WareHouseCatalogueType.Add, documentItem));
            }

            if (item.children?.Length > 0)
            {
                ProcessCatalogueItems(item.children.ToList(), documentItem.Id, warehouse, document,
                    documents);
            }
        }
    }
}

public class WareHouseCatalogue
{
    public string[] delete_id { get; set; }

    public WareHouseCatalogueItems[] items { get; set; }
}

public class WareHouseCatalogueItems
{
    public string Id { get; set; }

    public string title { get; set; }

    public string name { get; set; }

    public string type { get; set; }

    public string prompt { get; set; }

    public WareHouseCatalogueItems[]? children { get; set; }
}

public enum WareHouseCatalogueType
{
    Update,
    Add
}