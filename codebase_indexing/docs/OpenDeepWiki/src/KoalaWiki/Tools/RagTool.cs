using System.ComponentModel;
using System.Net.Http.Headers;
using System.Text.Json;
using Mem0.NET;
using ModelContextProtocol.Server;

namespace KoalaWiki.Tools;

public class RagTool(string? warehouseId = null)
{
    private static readonly Mem0Client Mem0Client = new(OpenAIOptions.Mem0ApiKey, OpenAIOptions.Mem0Endpoint, null,
        null,
        new HttpClient()
        {
            Timeout = TimeSpan.FromMinutes(600),
            DefaultRequestHeaders =
            {
                UserAgent = { new ProductInfoHeaderValue("KoalaWiki", "1.0") }
            }
        });

    [McpServerTool(Name = "rag_search"), Description(
         "Search and retrieve relevant code or documentation content from the current repository index using specific keywords.")]
    public static async Task<string> SearchMcpAsync(
        McpServer server,
        [Description(
            "Detailed description of the code or documentation you need. Specify whether you're looking for a function, class, method, or specific documentation. Be as specific as possible to improve search accuracy.")]
        string query,
        [Description(
            "Number of search results to return. Default is 5. Increase for broader coverage or decrease for focused results.")]
        int limit = 5,
        [Description(
            "Minimum relevance threshold for vector search results, ranging from 0 to 1. Default is 0.3. Higher values (e.g., 0.7) return more precise matches, while lower values provide more varied results.")]
        double minRelevance = 0.3)
    {
        var warehouseId = server.ServerOptions.Capabilities!.Experimental["warehouseId"].ToString();
        var result = await Mem0Client.SearchAsync(new SearchRequest()
        {
            Query = query,
            UserId = warehouseId,
            Threshold = minRelevance,
            Limit = limit,
        });

        return JsonSerializer.Serialize(result, JsonSerializerOptions.Web);
    }

    [KernelFunction("rag_search"), Description(
         "Search and retrieve relevant code or documentation content from the current repository index using specific keywords.")]
    public async Task<string> SearchAsync(
        [Description(
            "Detailed description of the code or documentation you need. Specify whether you're looking for a function, class, method, or specific documentation. Be as specific as possible to improve search accuracy.")]
        string query,
        [Description(
            "Number of search results to return. Default is 5. Increase for broader coverage or decrease for focused results.")]
        int limit = 5,
        [Description(
            "Minimum relevance threshold for vector search results, ranging from 0 to 1. Default is 0.3. Higher values (e.g., 0.7) return more precise matches, while lower values provide more varied results.")]
        double minRelevance = 0.3)
    {
        var result = await Mem0Client.SearchAsync(new SearchRequest()
        {
            Query = query,
            UserId = warehouseId,
            Threshold = minRelevance,
            Limit = limit,
        });

        return JsonSerializer.Serialize(result, JsonSerializerOptions.Web);
    }
}