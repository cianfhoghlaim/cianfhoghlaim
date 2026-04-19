using Microsoft.Extensions.Logging.Abstractions;
using ModelContextProtocol.Client;

namespace KoalaWiki.MCP.ModelContextProtocol;

/// <summary>
/// Extension methods for KernelPlugin
/// </summary>
public static class KernelExtensions
{
    private static readonly ConcurrentDictionary<string, IKernelBuilderPlugins> SseMap = new();


    /// <summary>
    /// Creates a Model Content Protocol plugin from an SSE server that contains the specified MCP functions and adds it into the plugin collection.
    /// </summary>
    /// <param name="endpoint"></param>
    /// <param name="serverName"></param>
    /// <param name="cancellationToken">The optional <see cref="CancellationToken"/>.</param>
    /// <param name="plugins"></param>
    /// <returns>A <see cref="KernelPlugin"/> containing the functions.</returns>
    public static async Task<IKernelBuilderPlugins> AddMcpFunctionsFromSseServerAsync(
        this IKernelBuilderPlugins plugins,
        string endpoint, string serverName, CancellationToken cancellationToken = default)
    {
        var key = ToSafePluginName(serverName);

        if (SseMap.TryGetValue(key, out var sseKernelPlugin))
        {
            return sseKernelPlugin;
        }

        var mcpClient = await GetClientAsync(serverName, endpoint, null, null, cancellationToken).ConfigureAwait(false);
        var functions = await mcpClient.MapToFunctionsAsync(cancellationToken: cancellationToken).ConfigureAwait(false);

        cancellationToken.Register(() => mcpClient.DisposeAsync().ConfigureAwait(false).GetAwaiter().GetResult());

        sseKernelPlugin = plugins.AddFromFunctions(key, functions);
        return SseMap[key] = sseKernelPlugin;
    }

    private static async Task<McpClient> GetClientAsync(string serverName, string? endpoint,
        Dictionary<string, string>? transportOptions, ILoggerFactory? loggerFactory,
        CancellationToken cancellationToken)
    {
        string transportType = string.Empty;

        if (!string.IsNullOrEmpty(endpoint))
        {
            transportType = "sse";
        }
        else
        {
            endpoint = null;
            transportType = "stdio";
        }

        McpClientOptions options = new()
        {
            ClientInfo = new()
            {
                Name = $"{serverName} {transportType}",
                Version = "1.0.0"
            }
        };

        IClientTransport config = null;

        if (transportType == "sse")
        {
            config = new HttpClientTransport(new HttpClientTransportOptions()
            {
                Endpoint = new Uri(endpoint),
                Name = serverName,
                ConnectionTimeout = TimeSpan.FromSeconds(15),
            });
        }
        else
        {
            config = new StdioClientTransport(new StdioClientTransportOptions()
            {
                Name = serverName,
                Command = transportOptions?["command"] ?? "npx",
                Arguments = transportOptions?["arguments"].ToString().Split(" "),
                EnvironmentVariables = transportOptions?.ToDictionary(x => x.Key, x => x.Value)
            }, loggerFactory: loggerFactory ?? NullLoggerFactory.Instance);
        }


        var click = await McpClient.CreateAsync(config, options, loggerFactory: loggerFactory ?? NullLoggerFactory.Instance,
                cancellationToken: cancellationToken)
            .ConfigureAwait(false);

        return click;
    }

    // A plugin name can contain only ASCII letters, digits, and underscores.
    private static string ToSafePluginName(string serverName)
    {
        return Regex.Replace(serverName, @"[^\w]", "_");
    }
}