using System.ClientModel;
using Azure.AI.OpenAI;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Logging;
using OpenAI;

namespace KoalaWiki.Agents;

public class AgentFactory
{
    public static ChatClientAgent CreateChatClientAgentAsync(string modelId,
        Action<ChatClientAgentOptions> agentAction,
        ILoggerFactory? loggerFactory = null)
    {
        if (OpenAIOptions.ModelProvider.Equals("OpenAI", StringComparison.OrdinalIgnoreCase))
        {
            var openAIClient = new OpenAIClient(new ApiKeyCredential(OpenAIOptions.ChatApiKey), new OpenAIClientOptions
            {
                Endpoint = new Uri(OpenAIOptions.Endpoint),
            });

            var chatClient = openAIClient.GetChatClient(modelId);

            var agentOptions = new ChatClientAgentOptions
            {
                ChatMessageStoreFactory = (messageContext) =>
                {
                    var logger = loggerFactory?.CreateLogger<AutoContextCompress>();
                    return new AutoContextCompress(messageContext, chatClient.AsIChatClient(), logger);
                },
            };
            agentAction.Invoke(agentOptions);

            var agent = chatClient.CreateAIAgent(agentOptions);

            return agent;
        }
        else if (OpenAIOptions.ModelProvider.Equals("AzureOpenAI", StringComparison.OrdinalIgnoreCase))
        {
            var azureOpenAIClient =
                new AzureOpenAIClient(new Uri(OpenAIOptions.Endpoint), new ApiKeyCredential(OpenAIOptions.ChatApiKey));

            var chatClient = azureOpenAIClient.GetChatClient(modelId);

            var agentOptions = new ChatClientAgentOptions();
            agentOptions.ChatMessageStoreFactory = (messageContext) =>
            {
                var logger = loggerFactory?.CreateLogger<AutoContextCompress>();
                return new AutoContextCompress(messageContext, chatClient.AsIChatClient(), logger);
            };
            agentAction.Invoke(agentOptions);
            var agent = chatClient.CreateAIAgent(agentOptions);

            return agent;
        }
        else
        {
            throw new NotSupportedException($"Model provider '{OpenAIOptions.ModelProvider}' is not supported.");
        }
    }
}