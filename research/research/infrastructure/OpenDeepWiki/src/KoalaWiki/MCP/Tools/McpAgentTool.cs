using System.Diagnostics;
using System.Text;
using KoalaWiki.Domains.MCP;
using KoalaWiki.Tools;
using ModelContextProtocol.Server;

namespace KoalaWiki.MCP.Tools;

public class McpAgentTool
{
    /// <summary>
    /// 生成仓库文档
    /// </summary>
    /// <param name="server"></param>
    /// <param name="question"></param>
    /// <returns></returns>
    /// <exception cref="Exception"></exception>
    [McpServerTool(Name = "GenerateWiki")]
    public static async Task<string> GenerateDocumentAsync(
        McpServer server,
        string question)
    {
        await using var scope = server.Services.CreateAsyncScope();

        var koala = scope.ServiceProvider.GetRequiredService<IKoalaWikiContext>();

        var name = server.ServerOptions.Capabilities!.Experimental["name"].ToString();
        var owner = server.ServerOptions.Capabilities!.Experimental["owner"].ToString();

        var warehouse = await koala.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.OrganizationName == owner && x.Name == name);

        if (warehouse == null)
        {
            throw new Exception($"抱歉，您的仓库 {owner}/{name} 不存在或已被删除。");
        }

        var document = await koala.Documents
            .AsNoTracking()
            .Where(x => x.WarehouseId == warehouse.Id)
            .FirstOrDefaultAsync();

        if (document == null)
        {
            throw new Exception("抱歉，您的仓库没有文档，请先生成仓库文档。");
        }

        // 找到是否有相似的提问
        var similarQuestion = await koala.MCPHistories
            .AsNoTracking()
            .Where(x => x.WarehouseId == warehouse.Id && x.Question.ToLower() == question.ToLower())
            .OrderByDescending(x => x.CreatedAt)
            .FirstOrDefaultAsync();

        // 如果是3天内的提问，直接返回
        if (similarQuestion != null && (DateTime.Now - similarQuestion.CreatedAt).TotalDays < 3)
        {
            return similarQuestion.Answer;
        }


        var kernel =await  KernelFactory.GetKernel(OpenAIOptions.Endpoint,
            OpenAIOptions.ChatApiKey, document.GitPath, OpenAIOptions.DeepResearchModel, false);

        var chat = kernel.GetRequiredService<IChatCompletionService>();

        // 解析仓库的目录结构
        var path = document.GitPath;

        var complete = string.Empty;

        var token = new CancellationTokenSource();

        var fileKernel = await KernelFactory.GetKernel(OpenAIOptions.Endpoint,
            OpenAIOptions.ChatApiKey, path, OpenAIOptions.DeepResearchModel, false, kernelBuilderAction: (builder =>
            {
                builder.Plugins.AddFromObject(new CompleteTool((async value =>
                {
                    if (!string.IsNullOrEmpty(value))
                    {
                        complete = value;

                        await token.CancelAsync().ConfigureAwait(false);
                    }
                })));
            }));

        var history = new ChatHistory();
        history.AddSystemEnhance();

        var catalogue = document.GetCatalogueSmartFilterOptimized();

        history.AddUserMessage(await PromptContext.Chat(nameof(PromptConstant.Chat.Responses),
            new KernelArguments()
            {
                ["catalogue"] = catalogue,
                ["repository_url"] = warehouse.Address,
            }, OpenAIOptions.ChatModel));

        history.AddUserMessage([
            new TextContent(question),
            new TextContent("""
                            <system-reminder>
                            Note:
                            - What the user needs is a detailed and professional response based on the contents of the aforementioned warehouse.
                            - Answer the user's questions as detailedly and promptly as possible.
                            </system-reminder>
                            """)
        ]);

        var first = true;

        DocumentContext.DocumentStore = new DocumentStore();

        var sw = Stopwatch.StartNew();
        var sb = new StringBuilder();

        try
        {
            await foreach (var chatItem in chat.GetStreamingChatMessageContentsAsync(history,
                               new OpenAIPromptExecutionSettings()
                               {
                                   ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions,
                                   MaxTokens = DocumentsHelper.GetMaxTokens(OpenAIOptions.ChatModel)
                               }, fileKernel, token.Token))
            {
                token.Token.ThrowIfCancellationRequested();

                // 发送数据
                if (chatItem.InnerContent is StreamingChatCompletionUpdate message)
                {
                    if (string.IsNullOrEmpty(chatItem.Content))
                    {
                        continue;
                    }

                    if (!string.IsNullOrEmpty(chatItem.Content))
                    {
                        sb.Append(chatItem.Content);
                    }
                }
            }

            sw.Stop();

            if (!string.IsNullOrEmpty(complete))
            {
                sb.Clear();
                sb.Append(complete);
            }

            var mcpHistory = new MCPHistory()
            {
                Id = Guid.NewGuid().ToString(),
                CostTime = (int)sw.ElapsedMilliseconds,
                CreatedAt = DateTime.Now,
                Question = question,
                Answer = sb.ToString(),
                WarehouseId = warehouse.Id,
                UserAgent = string.Empty,
                Ip = string.Empty,
                UserId = string.Empty
            };

            await koala.MCPHistories.AddAsync(mcpHistory);
            await koala.SaveChangesAsync();

            return sb.ToString();
        }
        // 如果是取消异常
        catch (OperationCanceledException)
        {
            return complete;
        }
        catch (Exception e)
        {
            return "抱歉，发生了错误: " + e.Message;
        }
    }
}