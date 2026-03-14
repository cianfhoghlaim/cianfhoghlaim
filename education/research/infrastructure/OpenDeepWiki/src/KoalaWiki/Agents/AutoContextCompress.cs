using System.Text;
using System.Text.Json;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Logging;
using ChatMessage = Microsoft.Extensions.AI.ChatMessage;
using FunctionCallContent = Microsoft.Extensions.AI.FunctionCallContent;
using FunctionResultContent = Microsoft.Extensions.AI.FunctionResultContent;

namespace KoalaWiki.Agents;

public class AutoContextCompress : ChatMessageStore
{
    private List<ChatMessage> messages = new();
    private readonly ChatClientAgentOptions.ChatMessageStoreFactoryContext messageContext;
    private readonly IChatClient chatClient;
    private readonly ILogger<AutoContextCompress>? logger;

    // Configuration from environment variables
    private readonly bool isCompressionEnabled;
    private readonly int tokenLimit;
    private readonly int maxTokenLimit;

    public AutoContextCompress(
        ChatClientAgentOptions.ChatMessageStoreFactoryContext messageContext,
        IChatClient chatClient,
        ILogger<AutoContextCompress>? logger = null)
    {
        this.messageContext = messageContext;
        this.chatClient = chatClient;
        this.logger = logger;

        // Read configuration from environment variables
        isCompressionEnabled = GetEnvironmentVariableBool("AUTO_CONTEXT_COMPRESS_ENABLED", true);
        tokenLimit = GetEnvironmentVariableInt("AUTO_CONTEXT_COMPRESS_TOKEN_LIMIT", 100000);
        maxTokenLimit = GetEnvironmentVariableInt("AUTO_CONTEXT_COMPRESS_MAX_TOKEN_LIMIT", 200000);

        // Validate configuration
        ValidateConfiguration();

        if (isCompressionEnabled)
        {
            logger?.LogInformation(
                "Auto context compression enabled: TokenLimit={TokenLimit}, MaxTokenLimit={MaxTokenLimit}",
                tokenLimit, maxTokenLimit);
        }
    }

    private void ValidateConfiguration()
    {
        if (isCompressionEnabled)
        {
            if (tokenLimit <= 0)
            {
                throw new InvalidOperationException(
                    "AUTO_CONTEXT_COMPRESS_TOKEN_LIMIT must be set to a positive value when compression is enabled.");
            }

            if (maxTokenLimit <= 0)
            {
                throw new InvalidOperationException(
                    "AUTO_CONTEXT_COMPRESS_MAX_TOKEN_LIMIT must be set to a positive value.");
            }

            if (tokenLimit > maxTokenLimit)
            {
                throw new InvalidOperationException(
                    $"AUTO_CONTEXT_COMPRESS_TOKEN_LIMIT ({tokenLimit}) cannot exceed AUTO_CONTEXT_COMPRESS_MAX_TOKEN_LIMIT ({maxTokenLimit}).");
            }
        }
    }

    public override async Task AddMessagesAsync(IEnumerable<ChatMessage> messages,
        CancellationToken cancellationToken = default)
    {
        this.messages.AddRange(messages);

        if (!isCompressionEnabled)
        {
            return;
        }

        var token = CalculateTotalTokens();

        if (token > tokenLimit)
        {
            // Check if recent messages contain Write/Edit operations
            // If so, skip compression as these are critical new changes
            if (HasRecentWriteOperations())
            {
                logger?.LogInformation(
                    "Skipping compression: Recent Write/Edit operations detected. Current={CurrentTokens}, Limit={TokenLimit}",
                    token, tokenLimit);
                return;
            }

            logger?.LogWarning(
                "Token limit exceeded: Current={CurrentTokens}, Limit={TokenLimit}. Triggering compression.",
                token, tokenLimit);

            await CompressContextAsync(cancellationToken);

            var newToken = CalculateTotalTokens();
            logger?.LogInformation(
                "Context compression completed: Before={BeforeTokens}, After={AfterTokens}, Reduced={ReducedTokens}",
                token, newToken, token - newToken);
        }
    }

    private bool HasRecentWriteOperations()
    {
        // Check last 10 messages for Write/Edit operations
        var recentCount = Math.Min(10, messages.Count);
        var recentMessages = messages.Skip(Math.Max(0, messages.Count - recentCount)).ToList();

        foreach (var message in recentMessages)
        {
            foreach (var content in message.Contents)
            {
                if (content is FunctionCallContent functionCall)
                {
                    var functionName = functionCall.Name.ToLowerInvariant();
                    // Check for critical write operations
                    if (functionName.Contains("write") ||
                        functionName.Contains("edit") ||
                        functionName.Contains("notebookedit") ||
                        functionName.Contains("create") ||
                        functionName.Contains("modify"))
                    {
                        logger?.LogDebug(
                            "Recent write operation detected: {FunctionName} in last {MessageCount} messages",
                            functionCall.Name, recentCount);
                        return true;
                    }
                }
            }
        }

        return false;
    }

    private int CalculateTotalTokens()
    {
        var token = 0;
        foreach (var message in this.messages)
        {
            token += CalculateMessageTokens(message);
        }

        return token;
    }

    private int CalculateMessageTokens(ChatMessage message)
    {
        var token = 0;

        if (!string.IsNullOrEmpty(message.Text))
        {
            token += TokenHelper.GetTokens(message.Text);
        }
        else
        {
            foreach (var content in message.Contents)
            {
                if (content is FunctionResultContent functionResultContent)
                {
                    token += TokenHelper.GetTokens(JsonSerializer.Serialize(functionResultContent.Result,
                        JsonSerializerOptions.Web));
                }
                else if (content is FunctionCallContent functionCallContent)
                {
                    token += TokenHelper.GetTokens(JsonSerializer.Serialize(functionCallContent.Arguments));
                }
                else if (content is Microsoft.Extensions.AI.TextContent textContent)
                {
                    token += TokenHelper.GetTokens(textContent.Text);
                }
            }
        }

        return token;
    }

    private async Task<List<ChatMessage>> CompressContextAsync(CancellationToken cancellationToken)
    {
        // If there are few messages, keep all
        if (messages.Count <= 5)
        {
            return messages;
        }

        // Always keep the last 3 messages
        var keepLastCount = 3;
        var messagesToAnalyze = messages.Count - keepLastCount;

        // Messages to compress (excluding last 3)
        var messagesToCompress = messages.Take(messagesToAnalyze).ToList();

        // Create compression prompt
        var analysisMessages = new List<ChatMessage>
        {
            new ChatMessage(ChatRole.System,
                """
                You are a conversation summarization assistant for AI development conversations.
                Your task is to analyze conversation history and create a concise, accurate summary.
                Focus on extracting the most important information while maintaining context coherence.
                """)
        };

        // Pass the messages to compress as context
        analysisMessages.AddRange(messagesToCompress);
        analysisMessages.Add(new ChatMessage(ChatRole.User, BuildCompressionPrompt()));

        var response = await chatClient.GetResponseAsync(analysisMessages, cancellationToken: cancellationToken);

        // Get the compressed summary
        var summary = response.Text ?? "Unable to generate summary";

        logger?.LogInformation(
            "Compressed {CompressedCount} messages. Keeping last {KeepCount} messages.",
            messagesToAnalyze, keepLastCount);

        // Build new message list
        var compressedMessages = new List<ChatMessage>();

        // Keep System messages from original
        var systemMessages = messages.Where(m => m.Role == ChatRole.System).ToList();
        compressedMessages.AddRange(systemMessages);

        // Add compressed summary as System message
        compressedMessages.Add(new ChatMessage(ChatRole.System,
            $"""
            <conversation-history-summary>
            [This is a summary of our previous conversation for context]

            {summary}
            </conversation-history-summary>
            """));

        // Add last N messages
        var recentMessages = messages.Skip(messagesToAnalyze).ToList();
        compressedMessages.AddRange(recentMessages);

        // Update the messages to the compressed set
        messages = compressedMessages;
        return messages;
    }

    private string BuildCompressionPrompt()
    {
        return """
            Please compress the above conversation history into a concise summary.

            The summary should:
            1. **Retain key information and context**:
               - File paths, class names, function names mentioned
               - Code snippets or implementations discussed
               - Initial task requirements and goals

            2. **Record important decisions and outcomes**:
               - Technical decisions and architecture choices
               - Solutions to problems or bugs fixed
               - Files modified and changes made
               - Test results or build status

            3. **Preserve the final task requirements and goals**:
               - What needs to be accomplished
               - Current implementation status
               - Any pending tasks or issues

            4. **Use concise language**:
               - Not exceeding 1/3 of the original length
               - Use bullet points for clarity
               - Focus on technical details, not conversational fluff

            **Important**: Provide ONLY the summary without any additional explanations, meta-commentary, or preamble.
            Start directly with the summarized content.
            """;
    }

    public override JsonElement Serialize(JsonSerializerOptions? jsonSerializerOptions = null)
    {
        return JsonSerializer.SerializeToElement(messages, jsonSerializerOptions);
    }

    public override async Task<IEnumerable<ChatMessage>> GetMessagesAsync(CancellationToken cancellationToken = default)
    {
        return await Task.FromResult(messages);
    }

    private static string GetEnvironmentVariable(string name, string defaultValue)
    {
        return Environment.GetEnvironmentVariable(name) ?? defaultValue;
    }

    private static bool GetEnvironmentVariableBool(string name, bool defaultValue)
    {
        var value = Environment.GetEnvironmentVariable(name);
        if (string.IsNullOrEmpty(value))
        {
            return defaultValue;
        }

        return bool.TryParse(value, out var result) ? result : defaultValue;
    }

    private static int GetEnvironmentVariableInt(string name, int defaultValue)
    {
        var value = Environment.GetEnvironmentVariable(name);
        if (string.IsNullOrEmpty(value))
        {
            return defaultValue;
        }

        return int.TryParse(value, out var result) ? result : defaultValue;
    }
}