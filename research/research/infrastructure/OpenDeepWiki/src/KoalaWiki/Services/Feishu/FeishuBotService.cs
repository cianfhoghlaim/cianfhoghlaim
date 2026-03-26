using System.ClientModel.Primitives;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using System.Web;
using FastService;
using ImageAgent.Feishu;
using KoalaWiki.Dto;
using KoalaWiki.Prompts;
using KoalaWiki.Services.Feishu.Dto;
using KoalaWiki.Services.Feishu.Feishu;
using KoalaWiki.Tools;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using OpenAI.Chat;

namespace KoalaWiki.Services.Feishu;

[Tags("飞书Bot")]
[FastService.Route("/api/feishu-bot")]
public class FeishuBotService(
    ILogger<FeishuBotService> logger,
    IMemoryCache memoryCache,
    FeiShuClient feiShuClient,
    IKoalaWikiContext koala)
    : FastApi
{
    [HttpPost("/{owner}/{name}")]
    [AllowAnonymous]
    public async Task CreateAsync(string owner, string name, HttpContext context, FeishuInput input)
    {
        logger.LogInformation("开始处理飞书事件回调，事件类型: {EventType}", input.type);

        if (!string.IsNullOrEmpty(input.encrypt))
        {
            logger.LogWarning("用户启用了加密密钥，拒绝处理");

            await context.Response.WriteAsJsonAsync(new
            {
                code = 1,
                message = new
                {
                    zh_CN = "你配置了 Encrypt Key，请关闭该功���。",
                    en_US = "You have open Encrypt Key Feature, please close it.",
                }
            });
            return;
        }


        // 处理飞书开放平台的服务端校验
        if (input.type == "url_verification")
        {
            logger.LogInformation("处理URL验证请求，challenge: {Challenge}", input.challenge);
            await context.Response.WriteAsJsonAsync(new
            {
                input.challenge,
            });
            return;
        }

        // 处理飞书开放平台的事件回调
        if (input.header.event_type == "im.message.receive_v1")
        {
            var eventId = input.header.event_id; // 事件id
            var messageId = input.Event.message.message_id; // 消息id
            var chatId = input.Event.message.chat_id; // 群聊id
            var senderId = input.Event.sender.sender_id.user_id; // 发送人id
            var sessionId = input.Event.sender.sender_id.open_id; // 发送人openid

            logger.LogInformation(
                "收到消息事件 - EventId: {EventId}, MessageId: {MessageId}, ChatId: {ChatId}, SenderId: {SenderId}, SessionId: {SessionId}",
                eventId, messageId, chatId, senderId, sessionId);

            // 对于同一个事件，只处理一次
            string cacheKey = $"event_{input.Event.message.message_id}";
            if (memoryCache.TryGetValue(cacheKey, out _))
            {
                logger.LogInformation("跳过重复事件，CacheKey: {CacheKey}", cacheKey);
                await context.Response.WriteAsJsonAsync(new
                {
                    code = 0,
                });
                return;
            }

            // 将事件ID存储到缓存中，设置过期时间为1小时
            memoryCache.Set(cacheKey, true, TimeSpan.FromHours(1));
            logger.LogDebug("事件已缓存，CacheKey: {CacheKey}", cacheKey);

            if (input.Event.message.chat_type is "p2p" or "group")
            {
                // URL decode parameters
                var decodedOrganizationName = HttpUtility.UrlDecode(owner);
                var decodedName = HttpUtility.UrlDecode(name);

                var warehouse = await koala.Warehouses
                    .AsNoTracking()
                    .FirstOrDefaultAsync(x =>
                        x.OrganizationName.ToLower() == decodedOrganizationName.ToLower() &&
                        x.Name.ToLower() == decodedName.ToLower());

                if (warehouse == null)
                {
                    context.Response.StatusCode = 404;
                    await context.Response.WriteAsJsonAsync(new
                    {
                        message = "Warehouse not found",
                        code = 404,
                    });
                    return;
                }


                var document = await koala.Documents
                    .AsNoTracking()
                    .Where(x => x.WarehouseId == warehouse.Id)
                    .FirstOrDefaultAsync();

                if (document == null)
                {
                    await context.Response.WriteAsJsonAsync(new
                    {
                        message = "document not found",
                        code = 404,
                    });
                    return;
                }


                // 私聊直接回复
                if (input.Event.message.chat_type == "p2p")
                {
                    logger.LogInformation("处理私聊消息，消息类型: {MessageType}", input.Event.message.message_type);

                    // 不是文本消息，不处理
                    if (input.Event.message.message_type != "text")
                    {
                        // TODO: 需要注入chatAiService服务
                        // await chatAiService.SendMessages(messageId, "暂不支持其他类型的提问");
                        logger.LogWarning("暂不支持其他类型的提问，消息类型: {MessageType}", input.Event.message.message_type);
                        await context.Response.WriteAsJsonAsync(new
                        {
                            code = 0,
                        });
                        return;
                    }

                    // 是文本消息，直接回复
                    var userInput = JsonSerializer.Deserialize<FeishuUserInput>(input.Event.message.content);
                    logger.LogInformation("解析私聊文本消息成功，内容: {Text}", userInput?.text);
                    await context.Response.WriteAsJsonAsync(new
                    {
                        code = 0,
                    });

                    logger.LogInformation("启动异步任务处理私聊消息");
                    await Task.Factory.StartNew(() =>
                        Handler(input.Event.message.message_id, input.Event.message.content, sessionId, warehouse,
                            document));
                    return;
                }

                // 群聊，需要 @ 机器人
                if (input.Event.message.chat_type == "group")
                {
                    logger.LogInformation("处理群聊消息，ChatId: {ChatId}", chatId);

                    if (input.Event.message.mentions == null || input.Event.message.mentions.Length == 0)
                    {
                        logger.LogWarning("群聊消息没有@任何人，跳过处理");
                        await context.Response.WriteAsJsonAsync(new
                        {
                            code = 0,
                        });
                        return;
                    }

                    // 没有 mention 机器人，则退出。
                    if (input.Event.message.mentions[0].name != FeishuOptions.FeishuBotName)
                    {
                        logger.LogWarning("群聊消息@的不是机器人，被@的用户: {MentionName}", input.Event.message.mentions[0].name);
                        await context.Response.WriteAsJsonAsync(new
                        {
                            code = 0,
                        });
                        return;
                    }

                    logger.LogInformation("已发送群聊回复消息到群: {ChatId}", chatId);

                    await context.Response.WriteAsJsonAsync(new
                    {
                        code = 0,
                    });

                    logger.LogInformation("启动异步任务处理群聊消息");
                    await Task.Factory.StartNew(async () =>
                        await Handler(input.Event.message.message_id, input.Event.message.content, chatId, warehouse,
                            document, "chat_id"));
                    return;
                }
            }
        }

        logger.LogWarning("未匹配到任何处理逻辑，返回错误码2");
        await context.Response.WriteAsJsonAsync(new
        {
            code = 2,
        });
    }

    private async Task Handler(string messageId, string content, string sessionId,
        Warehouse warehouse, Document document,
        string type = "open_id")
    {
        logger.LogInformation("开始处理消息 - MessageId: {MessageId}, SessionId: {SessionId}, Type: {Type}",
            messageId, sessionId, type);

        try
        {
            logger.LogDebug("开始解析消息内容: {Content}", content);
            var userInput = JsonSerializer.Deserialize<UserInputs>(content);
            logger.LogInformation("消息解析成功，IsText: {IsText}", userInput?.IsText);

            await SendMessages("sessionId", "正在努力思考中，请稍后...", type);

            var history = new ChatHistory();

            // 解析仓库的目录结构
            var path = document.GitPath;

            var kernel = await KernelFactory.GetKernel(OpenAIOptions.Endpoint,
                OpenAIOptions.ChatApiKey, path, OpenAIOptions.ChatModel, false);

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

            string tree = document.GetCatalogueSmartFilterOptimized();

            history.AddSystemMessage(await PromptContext.Chat(nameof(PromptConstant.Chat.Responses),
                new KernelArguments()
                {
                    ["catalogue"] = tree,
                    ["repository"] = warehouse.Address.Replace(".git", ""),
                    ["repository_name"] = warehouse.Name,
                    ["branch"] = warehouse.Branch
                }, OpenAIOptions.DeepResearchModel));

            var sb = new StringBuilder();

            if (userInput?.IsText == true)
            {
                logger.LogInformation("处理纯文本消息，原始文本: {Text}", userInput.text);
                history.AddUserMessage(userInput.text);
            }
            else
            {
                logger.LogInformation("处理复合消息内容");

                if (userInput.content.Any(x => x.Any(a => a.IsImage)))
                {
                    logger.LogInformation("检测到图片内容，开始处理图片编辑");

                    var contents = new ChatMessageContentItemCollection();
                    foreach (var input in userInput.content.SelectMany(x => x))
                    {
                        if (input.IsText)
                        {
                            contents.Add(new TextContent(input.text));
                        }
                        else
                        {
                            var originalImageBytes = await DownloadImageAsync(messageId, input.image_key);
                            contents.Add(new ImageContent(originalImageBytes, "image/png"));
                        }
                    }

                    history.AddUserMessage(contents);
                }
                else
                {
                    logger.LogInformation("处理纯文字复合消息");

                    // 提取所有的文字
                    var texts = userInput.content.First().Where(x => x.IsText).Select(x => x.text);
                    var prompt = string.Join("\n", texts);
                    logger.LogInformation("提取的文字内容: {Prompt}", prompt);

                    if (string.IsNullOrWhiteSpace(prompt))
                    {
                        logger.LogWarning("没有提取到有效的文字描述");
                        await SendMessages(sessionId, "没有提取到有效的文字描述，无法生成图片", type);
                        return;
                    }

                    var contents = new ChatMessageContentItemCollection();
                    foreach (var input in userInput.content.SelectMany(x => x))
                    {
                        if (input.IsText)
                        {
                            contents.Add(new TextContent(input.text));
                        }
                        else
                        {
                            var originalImageBytes = await DownloadImageAsync(messageId, input.image_key);
                            contents.Add(new ImageContent(originalImageBytes, "image/png"));
                        }
                    }

                    history.AddUserMessage(contents);
                }
            }

            await foreach (var chatItem in chat.GetStreamingChatMessageContentsAsync(history,
                               new OpenAIPromptExecutionSettings()
                               {
                                   ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions,
                                   MaxTokens = DocumentsHelper.GetMaxTokens(OpenAIOptions.DeepResearchModel),
                               }, kernel))
            {
                // 发送数据
                if (chatItem.InnerContent is not StreamingChatCompletionUpdate message) continue;

                if (DocumentContext.DocumentStore != null && DocumentContext.DocumentStore.GitIssus.Count > 0)
                {
                    DocumentContext.DocumentStore.GitIssus.Clear();
                }

                // 普通消息内容
                if (!string.IsNullOrEmpty(chatItem.Content))
                {
                    sb.Append(chatItem.Content);
                }
            }

            // 使用正则表达式移除<thinking>标签及其内容
            sb = new StringBuilder(Regex.Replace(sb.ToString(), @"<thinking>.*?<\/thinking>", "",
                RegexOptions.IgnoreCase | RegexOptions.Singleline));
            sb = new StringBuilder(Regex.Replace(sb.ToString(), @"<think>.*?<\/think>", "",
                RegexOptions.IgnoreCase | RegexOptions.Singleline));

            // 解析sb的#标题
            var title = "来自 " + warehouse.Name + " 的回复";

            await SendRichMessage(sessionId, title, sb.ToString(), type);
            logger.LogInformation("已发送回复消息给用户: {SessionId}", sessionId);
        }
        catch (Exception exception)
        {
            logger.LogError(exception, "处理消息时发生异常 - MessageId: {MessageId}, SessionId: {SessionId}, Type: {Type}",
                messageId, sessionId, type);
            await SendMessages(sessionId, "处理消息失败：" + exception, type);
        }
    }

    public async Task SendMessages(string sessionId, string message, string receiveIdType = "open_id")
    {
        await feiShuClient.SendMessages(
            new SendMessageInput(JsonSerializer.Serialize(new
                {
                    text = message,
                }, JsonSerializerOptions.Web), "text",
                sessionId), receiveIdType);
    }

    public async Task SendRichMessage(string sessionId, string title, string text,
        string receiveIdType = "open_id")
    {
        await feiShuClient.SendMessages(
            new SendMessageInput(JsonSerializer.Serialize(new
                {
                    zh_cn = new
                    {
                        title,
                        content = new object[]
                        {
                            new object[]
                            {
                                new
                                {
                                    tag = "text",
                                    text,
                                }
                            }
                        }
                    }
                }, JsonSerializerOptions.Web), "post",
                sessionId), receiveIdType);
    }

    public async Task SendImageMessages(string sessionId, byte[] bytes, string receiveIdType = "open_id")
    {
        await feiShuClient.SendImageAsync(bytes, sessionId, receiveIdType);
    }

    public async Task<byte[]> DownloadImageAsync(string messageId, string imageKey)
        => await feiShuClient.DownloadImageAsync(messageId, imageKey);
}