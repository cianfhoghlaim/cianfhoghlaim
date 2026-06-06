using System.ClientModel.Primitives;
using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Web;
using FastService;
using KoalaWiki.Dto;
using KoalaWiki.Tools;
using Microsoft.AspNetCore.Mvc;

#pragma warning disable SKEXP0001

namespace KoalaWiki.Services.AI;

[Tags("Responese")]
[FastService.Route("")]
public class ResponsesService(IKoalaWikiContext koala) : FastApi
{
    [HttpPost("/api/Responses")]
    public async Task ExecuteAsync(HttpContext context, ResponsesInput input)
    {
        using var activity = Activity.Current?.Source.StartActivity("AI.ResponsesService.Execute");
        activity?.SetTag("repository.organization", input.OrganizationName);
        activity?.SetTag("repository.name", input.Name);
        activity?.SetTag("message.count", input.Messages?.Count ?? 0);
        activity?.SetTag("model.provider", OpenAIOptions.ModelProvider);
        activity?.SetTag("model.name", OpenAIOptions.ChatModel);

        // URL decode parameters
        var decodedOrganizationName = HttpUtility.UrlDecode(input.OrganizationName);
        var decodedName = HttpUtility.UrlDecode(input.Name);

        var warehouse = await koala.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(x =>
                x.OrganizationName.ToLower() == decodedOrganizationName.ToLower() &&
                x.Name.ToLower() == decodedName.ToLower());

        if (warehouse == null)
        {
            activity?.SetStatus(ActivityStatusCode.Error, "Warehouse not found");
            activity?.SetTag("error.reason", "warehouse_not_found");
            context.Response.StatusCode = 404;
            await context.Response.WriteAsJsonAsync(new
            {
                message = "Warehouse not found",
                code = 404,
            });
            return;
        }


        activity?.SetTag("warehouse.id", warehouse.Id);
        activity?.SetTag("warehouse.address", warehouse.Address);
        activity?.SetTag("warehouse.branch", warehouse.Branch);


        var document = await koala.Documents
            .AsNoTracking()
            .Where(x => x.WarehouseId == warehouse.Id)
            .FirstOrDefaultAsync();

        if (document == null)
        {
            activity?.SetStatus(ActivityStatusCode.Error, "Document not found");
            activity?.SetTag("error.reason", "document_not_found");
            context.Response.StatusCode = 404;
            await context.Response.WriteAsJsonAsync(new
            {
                message = "document not found",
                code = 404,
            });
            return;
        }

        activity?.SetTag("document.id", document.Id);
        activity?.SetTag("document.git_path", document.GitPath);

        // 解析仓库的目录结构
        var path = document.GitPath;

        using var kernelCreateActivity = Activity.Current.Source.StartActivity("AI.KernelCreation");
        kernelCreateActivity?.SetTag("kernel.path", path);
        kernelCreateActivity?.SetTag("kernel.model", OpenAIOptions.ChatModel);

        var kernel =await  KernelFactory.GetKernel(OpenAIOptions.Endpoint,
            OpenAIOptions.ChatApiKey, path, OpenAIOptions.ChatModel, false);

        kernelCreateActivity?.SetStatus(ActivityStatusCode.Ok);

        if (OpenAIOptions.EnableMem0)
        {
            kernel.Plugins.AddFromObject(new RagTool(warehouse!.Id));
        }

        if (warehouse.Address.Contains("github.com"))
        {
            kernel.Plugins.AddFromObject(new GithubTool(warehouse.OrganizationName, warehouse.Name,
                warehouse.Branch), "Github");
        }
        else if (warehouse.Address.Contains("gitee.com") && !string.IsNullOrWhiteSpace(GiteeOptions.Token))
        {
            kernel.Plugins.AddFromObject(new GiteeTool(warehouse.OrganizationName, warehouse.Name,
                warehouse.Branch), "Gitee");
        }

        DocumentContext.DocumentStore = new DocumentStore();


        var chat = kernel.GetRequiredService<IChatCompletionService>();

        var history = new ChatHistory();
        history.AddSystemEnhance();

        string tree = document.GetCatalogueSmartFilterOptimized();

        if (input.DeepResearch)
        {
            history.AddUserMessage(await PromptContext.Chat(nameof(PromptConstant.Chat.ResponsesDeepResearch),
                new KernelArguments()
                {
                    ["catalogue"] = tree,
                    ["repository"] = warehouse.Address.Replace(".git", ""),
                    ["repository_name"] = warehouse.Name,
                    ["branch"] = warehouse.Branch
                }, OpenAIOptions.DeepResearchModel));
        }
        else
        {
            history.AddUserMessage(await PromptContext.Chat(nameof(PromptConstant.Chat.Responses),
                new KernelArguments()
                {
                    ["catalogue"] = tree,
                    ["repository"] = warehouse.Address.Replace(".git", ""),
                    ["repository_name"] = warehouse.Name,
                    ["branch"] = warehouse.Branch
                }, OpenAIOptions.DeepResearchModel));
        }

        if (!string.IsNullOrEmpty(input.AppId))
        {
            var appConfig = await koala.AppConfigs
                .AsNoTracking()
                .FirstOrDefaultAsync(x => x.AppId == input.AppId);

            if (appConfig == null)
            {
                throw new Exception(
                    "AppConfig is not supported in this endpoint. Please use the appropriate API for app configurations.");
            }


            if (!string.IsNullOrEmpty(appConfig?.Prompt))
            {
                history.AddUserMessage($"<system>\n{appConfig?.Prompt}\n</system>");
            }
        }

        // 添加消息历史记录
        foreach (var msg in input.Messages)
        {
            if (msg.Role.ToLower() == "user")
            {
                if (msg.Content?.Count == 1 && msg.Content.Any(x => x.Type == ResponsesMessageContentType.Text))
                {
                    history.AddUserMessage(msg.Content.First().Content);
                    continue;
                }

                var contents = new ChatMessageContentItemCollection();

                foreach (var messageContentInput in msg.Content)
                {
                    if (messageContentInput.Type == ResponsesMessageContentType.Text)
                    {
                        contents.Add(new TextContent(messageContentInput.Content));
                    }
                    else if (messageContentInput is { Type: ResponsesMessageContentType.Image, ImageContents: not null })
                    {
                        foreach (var imageContent in messageContentInput.ImageContents)
                        {
                            contents.Add(new BinaryContent(
                                $"data:{imageContent.MimeType};base64,{imageContent.Data}"));
                        }
                    }
                }
            }
            else if (msg.Role.ToLower() == "assistant")
            {
                // 判断，如果当前消息是最后一条，并且content=空则跳过
                if (msg.Content == null ||
                    msg.Content.Count > 0 && msg.Content.All(x => string.IsNullOrEmpty(x.Content)))
                {
                    continue;
                }

                if (msg.Content?.Count == 1 && msg.Content.Any(x => x.Type == ResponsesMessageContentType.Text))
                {
                    history.AddUserMessage(msg.Content.First().Content);
                    continue;
                }

                var contents = new ChatMessageContentItemCollection();
                foreach (var messageContentInput in msg.Content)
                {
                    if (messageContentInput.Type == ResponsesMessageContentType.Text)
                    {
                        contents.Add(new TextContent(messageContentInput.Content));
                    }
                    else if (messageContentInput.Type == ResponsesMessageContentType.Image)
                    {
                        // 图片内容
                        var imageContent = new ImageContent(messageContentInput.Content);
                        contents.Add(new BinaryContent(
                            $"data:{imageContent.MimeType};base64,{imageContent.Data}"));
                    }
                    else
                    {
                    }
                }
            }
            else if (msg.Role.ToLower() == "system")
            {
                if (msg.Content?.Count == 1 && msg.Content.Any(x => x.Type == ResponsesMessageContentType.Text))
                {
                    history.AddUserMessage(msg.Content.First().Content);
                    continue;
                }
            }
        }

        // sse
        context.Response.Headers.ContentType = "text/event-stream";
        context.Response.Headers.CacheControl = "no-cache";

        // 是否推理中
        var isReasoning = false;

        // 是否普通消息
        var isMessage = false;

        using var chatActivity = Activity.Current?.Source.StartActivity("AI.StreamingChatCompletion");
        chatActivity?.SetTag("chat.max_tokens", DocumentsHelper.GetMaxTokens(OpenAIOptions.DeepResearchModel));
        chatActivity?.SetTag("chat.temperature", 0.5);
        chatActivity?.SetTag("chat.tool_behavior", "AutoInvokeKernelFunctions");
        chatActivity?.SetTag("chat.history_count", history.Count);

        var messageCount = 0;
        var toolCallCount = 0;
        var reasoningTokens = 0;

        await foreach (var chatItem in chat.GetStreamingChatMessageContentsAsync(history,
                           new OpenAIPromptExecutionSettings()
                           {
                               ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions,
                               MaxTokens = DocumentsHelper.GetMaxTokens(OpenAIOptions.DeepResearchModel),
                               Temperature = 0.5,
                           }, kernel))
        {
            // 发送数据
            if (chatItem.InnerContent is not StreamingChatCompletionUpdate message) continue;

            if (DocumentContext.DocumentStore != null && DocumentContext.DocumentStore.GitIssus.Count > 0)
            {
                await context.Response.WriteAsync(
                    $"data: {{\"type\": \"git_issues\", \"content\": {JsonSerializer.Serialize(DocumentContext.DocumentStore.GitIssus, JsonSerializerOptions.Web)}}}\n\n");

                await context.Response.Body.FlushAsync();

                DocumentContext.DocumentStore.GitIssus.Clear();
            }


            var jsonContent = JsonNode.Parse(ModelReaderWriter.Write(chatItem.InnerContent!));

            var choices = jsonContent!["choices"] as JsonArray;
            if (choices?.Count > 0)
            {
                if (choices[0]!["delta"]!["reasoning_content"] != null)
                {
                    // 推理内容
                    var reasoningContent = choices![0]!["delta"]!["reasoning_content"].ToString();
                    if (!string.IsNullOrEmpty(reasoningContent))
                    {
                        if (isReasoning == false)
                        {
                            // 结束普通消息
                            if (isMessage)
                            {
                                isMessage = false;

                                await context.Response.WriteAsync($"data: {{\"type\": \"message_end\"}}\n\n");
                            }

                            isReasoning = true;

                            // 发送开启推理事件
                            await context.Response.WriteAsync($"data: {{\"type\": \"reasoning_start\"}}\n\n");
                        }

                        await context.Response.WriteAsync(
                            $"data: {{\"type\": \"reasoning_content\", \"content\": {JsonSerializer.Serialize(reasoningContent)}}}\n\n");
                        await context.Response.Body.FlushAsync();
                        reasoningTokens += reasoningContent.Length / 4; // 粗略估算令牌数
                        continue;
                    }
                }
            }

            if (isReasoning)
            {
                // 结束推理
                isReasoning = false;
                await context.Response.WriteAsync($"data: {{\"type\": \"reasoning_end\"}}\n\n");

                isMessage = true;
                // 开启普通消息
                await context.Response.WriteAsync($"data: {{\"type\": \"message_start\"}}\n\n");
            }

            if (message.ToolCallUpdates.Count > 0)
            {
                // 工具调用更新
                foreach (var toolCallUpdate in message.ToolCallUpdates)
                {
                    var toolCallData = new
                    {
                        type = "tool_call",
                        tool_call_id = toolCallUpdate.ToolCallId,
                        function_name = toolCallUpdate.FunctionName,
                        function_arguments = Encoding.UTF8.GetString(toolCallUpdate.FunctionArgumentsUpdate),
                    };

                    await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(toolCallData)}\n\n");
                    await context.Response.Body.FlushAsync();
                }

                toolCallCount++;
                continue;
            }

            // 普通消息内容
            if (!string.IsNullOrEmpty(chatItem.Content))
            {
                if (!isMessage)
                {
                    isMessage = true;
                    // 开启普通消息
                    await context.Response.WriteAsync($"data: {{\"type\": \"message_start\"}}\n\n");
                }

                var messageData = new
                {
                    type = "message_content",
                    content = chatItem.Content
                };

                await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(messageData)}\n\n");
                await context.Response.Body.FlushAsync();
                messageCount++;
            }
        }

        // 确保最后结束消息
        if (isMessage)
        {
            await context.Response.WriteAsync($"data: {{\"type\": \"message_end\"}}\n\n");
        }

        if (isReasoning)
        {
            await context.Response.WriteAsync($"data: {{\"type\": \"reasoning_end\"}}\n\n");
        }

        // 发送结束事件
        await context.Response.WriteAsync($"data: {{\"type\": \"done\"}}\n\n");
        await context.Response.Body.FlushAsync();

        // 设置聊天活动的统计信息
        chatActivity?.SetTag("chat.message_count", messageCount);
        chatActivity?.SetTag("chat.tool_call_count", toolCallCount);
        chatActivity?.SetTag("chat.reasoning_tokens", reasoningTokens);
        chatActivity?.SetStatus(ActivityStatusCode.Ok);

        // 设置主活动状态
        activity?.SetStatus(ActivityStatusCode.Ok);
        activity?.SetTag("response.completed", true);
    }
}