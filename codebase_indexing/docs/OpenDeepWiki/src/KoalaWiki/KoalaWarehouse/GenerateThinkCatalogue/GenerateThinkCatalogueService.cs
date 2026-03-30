using KoalaWiki.Agents;
using KoalaWiki.Tools;
using Microsoft.Extensions.AI;
using Newtonsoft.Json;
using ChatMessage = Microsoft.Extensions.AI.ChatMessage;

namespace KoalaWiki.KoalaWarehouse.GenerateThinkCatalogue;

public static partial class GenerateThinkCatalogueService
{
    private const int MaxRetries = 8; // 增加重试次数
    private const int BaseDelayMs = 1000;
    private const double MaxDelayMs = 30000; // 最大延迟30秒
    private const double JitterRange = 0.3; // 抖动范围30%

    // 错误分类
    private enum ErrorType
    {
        NetworkError, // 网络相关错误
        JsonParseError, // JSON解析错误
        ApiRateLimit, // API限流
        ModelError, // 模型响应错误
        UnknownError // 未知错误
    }

    public static async Task<DocumentResultCatalogue?> GenerateCatalogue(string path,
        string catalogue, Warehouse warehouse, ClassifyType? classify)
    {
        var retryCount = 0;
        Exception? lastException = null;
        var consecutiveFailures = 0;

        Log.Logger.Information("开始处理仓库：{path}，处理标题：{name}", path, warehouse.Name);

        while (retryCount < MaxRetries)
        {
            try
            {
                var result =
                    await ExecuteSingleAttempt(path, catalogue, classify).ConfigureAwait(false);

                if (result != null)
                {
                    Log.Logger.Information("成功处理仓库：{path}，处理标题：{name}，尝试次数：{retryCount}",
                        path, warehouse.Name, retryCount + 1);
                    return result;
                }

                // result为null也算失败，继续重试
                Log.Logger.Warning("处理仓库返回空结果：{path}，处理标题：{name}，尝试次数：{retryCount}",
                    path, warehouse.Name, retryCount + 1);
                consecutiveFailures++;
            }
            catch (Exception ex)
            {
                lastException = ex;
                consecutiveFailures++;
                var errorType = ClassifyError(ex);

                Log.Logger.Warning("处理仓库失败：{path}，处理标题：{name}，尝试次数：{retryCount}，错误类型：{errorType}，错误：{error}",
                    path, warehouse.Name, retryCount + 1, errorType, ex.Message);

                // 根据错误类型决定是否继续重试
                if (!ShouldRetry(errorType, retryCount, consecutiveFailures))
                {
                    Log.Logger.Error("错误类型 {errorType} 不适合重试或达到最大重试次数，停止重试", errorType);
                    break;
                }
            }

            retryCount++;

            if (retryCount < MaxRetries)
            {
                var delay = CalculateDelay(retryCount, consecutiveFailures);
                Log.Logger.Information("等待 {delay}ms 后进行第 {nextAttempt} 次尝试", delay, retryCount + 1);
                await Task.Delay(delay);

                // 如果连续失败过多，尝试重置某些状态
                if (consecutiveFailures >= 3)
                {
                    Log.Logger.Information("连续失败 {consecutiveFailures} 次，尝试重置状态", consecutiveFailures);
                    // 可以在这里添加一些重置逻辑，比如清理缓存等
                    await Task.Delay(2000); // 额外等待
                }
            }
        }

        Log.Logger.Error("处理仓库最终失败：{path}，处理标题：{name}，总尝试次数：{totalAttempts}，最后错误：{error}",
            path, warehouse.Name, retryCount, lastException?.Message ?? "未知错误");

        return null;
    }

    private static async Task<DocumentResultCatalogue?> ExecuteSingleAttempt(
        string path, string catalogue, ClassifyType? classify)
    {
        // 根据尝试次数调整提示词策略
        var enhancedPrompt = await GenerateThinkCataloguePromptAsync(classify, catalogue);

        var history = new List<ChatMessage>();

        var contents = new List<AIContent>()
        {
            new Microsoft.Extensions.AI.TextContent(enhancedPrompt),
            new Microsoft.Extensions.AI.TextContent(
                $"""
                 <system-reminder>
                 <catalog_tool_usage_guidelines>
                 **PARALLEL READ OPERATIONS**
                 - MANDATORY: Always perform PARALLEL File.Read calls — batch multiple files in a SINGLE message for maximum efficiency
                 - CRITICAL: Read MULTIPLE files simultaneously in one operation
                 - PROHIBITED: Sequential one-by-one file reads (inefficient and wastes context capacity)

                 **EDITING OPERATION LIMITS**
                 - HARD LIMIT: Maximum of 3 editing operations total (catalog.MultiEdit only)
                 - PRIORITY: Maximize each catalog.MultiEdit operation by bundling ALL related changes across multiple files
                 - STRATEGIC PLANNING: Consolidate all modifications into minimal MultiEdit operations to stay within the limit
                 - Use catalog.Write **only once** for initial creation or full rebuild (counts as initial structure creation, not part of the 3 edits)
                 - Always verify content before further changes using catalog.Read (Reads do NOT count toward limit)

                 **CRITICAL MULTIEDIT BEST PRACTICES**
                 - MAXIMIZE EFFICIENCY: Each MultiEdit should target multiple distinct sections across files
                 - AVOID CONFLICTS: Never edit overlapping or identical content regions within the same MultiEdit operation
                 - UNIQUE TARGETS: Ensure each edit instruction addresses a completely different section or file
                 - BATCH STRATEGY: Group all necessary changes by proximity and relevance, but maintain clear separation between edit targets

                 **RECOMMENDED EDITING SEQUENCE**
                 1. catalog.Write (one-time full structure creation)
                 2. catalog.MultiEdit with maximum parallel changes (counts toward 3-operation limit)
                 3. Use catalog.Read after each MultiEdit to verify success before next operation
                 4. Remaining MultiEdit operations for any missed changes
                 </catalog_tool_usage_guidelines>


                 ## Execution steps requirements:
                 1. Before performing any other operations, you must first invoke the 'agent-think' tool to plan the analytical steps. This is a necessary step for completing each research task.
                 2. Then, the code structure provided in the code_file must be utilized by calling file.Read to read the code for in-depth analysis, and then use catalog.Write to write the results of the analysis into the catalog directory.
                 3. If necessary, some parts that need to be optimized can be edited through catalog.MultiEdit.

                 For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially.
                 The repository's directory structure has been provided in <code_files>. Please utilize the provided structure directly for file navigation and reading operations, rather than relying on glob patterns or filesystem traversal methods.
                 Below is an example of the directory structure of the warehouse, where /D represents a directory and /F represents a file:
                    server/D
                      src/D
                        Main/F
                    web/D
                      components/D
                        Header.tsx/F

                 {Prompt.Language}

                 </system-reminder>
                 """),
            new Microsoft.Extensions.AI.TextContent(Prompt.Language)
        };
        history.Add(new ChatMessage(Microsoft.Extensions.AI.ChatRole.User, contents));

        int retry = 1;
        var inputTokenCount = 0;
        var outputTokenCount = 0;
        var catalogueTool = new CatalogueFunction();

        var agent = AgentFactory.CreateChatClientAgentAsync(OpenAIOptions.AnalysisModel,
            (options =>
            {
                options.Name = "ThinkCatalogueAgent";
                options.Instructions = PromptExtensions.System;
                options.ChatOptions = new ChatOptions()
                {
                    MaxOutputTokens = DocumentsHelper.GetMaxTokens(OpenAIOptions.ChatModel),
                    ToolMode = ChatToolMode.Auto,
                    Tools = new List<AITool>(catalogueTool.Create())
                    {
                        new FileTool(path, null).Create()
                    }
                };
            }));

        var agentThread = agent.GetNewThread();

        retry:
        // 添加超时控制
        var cts = new CancellationTokenSource(TimeSpan.FromMinutes(30));


        try
        {
            // 流式获取响应 - 添加取消令牌和异常处理
            await foreach (var item in agent.RunStreamingAsync(history, agentThread, cancellationToken: cts.Token)
                               .ConfigureAwait(false))
            {
                if (!string.IsNullOrEmpty(item.Text))
                {
                    Console.Write(item.Text);
                }
            }
        }
        catch (OperationCanceledException) when (cts.Token.IsCancellationRequested)
        {
            retry++;
            if (retry <= 3)
            {
                Console.WriteLine($"超时，正在重试 ({retry}/3)...");
                await Task.Delay(2000, CancellationToken.None);

                // 正确地重置超时令牌
                cts.Dispose();
                cts = new CancellationTokenSource(TimeSpan.FromMinutes(5)); // 重新赋值给cts
                goto retry;
            }

            throw new TimeoutException("流式处理超时");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"流式处理错误: {ex.Message}");
            throw;
        }
        finally
        {
            cts?.Dispose(); // 确保资源被释放
        }

        // Prefer tool-stored JSON when available
        if (!string.IsNullOrWhiteSpace(catalogueTool.Content))
        {
            return ExtractAndParseJson(catalogueTool.Content);
        }
        else
        {
            retry++;
            if (retry > 3)
            {
                throw new Exception("AI生成目录的时候重复多次响应空内容");
            }

            goto retry;
        }
    }

    private static DocumentResultCatalogue? ExtractAndParseJson(string responseText)
    {
        var extractedJson = JsonConvert.DeserializeObject<DocumentResultCatalogue>(responseText);

        return extractedJson;
    }

    private static ErrorType ClassifyError(Exception ex)
    {
        return ex switch
        {
            HttpRequestException => ErrorType.NetworkError,
            TaskCanceledException => ErrorType.NetworkError,
            JsonException => ErrorType.JsonParseError,
            InvalidOperationException when ex.Message.Contains("rate") => ErrorType.ApiRateLimit,
            InvalidOperationException when ex.Message.Contains("quota") => ErrorType.ApiRateLimit,
            _ when ex.Message.Contains("model") => ErrorType.ModelError,
            _ => ErrorType.UnknownError
        };
    }

    private static bool ShouldRetry(ErrorType errorType, int retryCount, int consecutiveFailures)
    {
        // 总是允许至少重试几次
        if (retryCount < 3) return true;

        // 根据错误类型决定是否继续重试
        return errorType switch
        {
            ErrorType.NetworkError => retryCount < MaxRetries,
            ErrorType.ApiRateLimit => retryCount < MaxRetries && consecutiveFailures < 5,
            ErrorType.JsonParseError => retryCount < 6, // JSON错误多重试几次
            ErrorType.ModelError => retryCount < 4,
            ErrorType.UnknownError => retryCount < MaxRetries,
            _ => throw new ArgumentOutOfRangeException(nameof(errorType), errorType, null)
        };
    }

    private static int CalculateDelay(int retryCount, int consecutiveFailures)
    {
        // 指数退避 + 抖动 + 连续失败惩罚
        var exponentialDelay = BaseDelayMs * Math.Pow(2, retryCount);
        var consecutiveFailurePenalty = consecutiveFailures * 1000;
        var jitter = Random.Shared.NextDouble() * JitterRange * exponentialDelay;

        var totalDelay = exponentialDelay + consecutiveFailurePenalty + jitter;

        return (int)Math.Min(totalDelay, MaxDelayMs);
    }
}