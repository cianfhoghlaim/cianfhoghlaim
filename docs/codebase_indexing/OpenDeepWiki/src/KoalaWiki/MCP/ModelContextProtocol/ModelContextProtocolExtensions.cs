using System.Text.Json;
using ModelContextProtocol.Client;
using ModelContextProtocol.Protocol;

namespace KoalaWiki.MCP.ModelContextProtocol;

/// <summary>
/// Extension methods for ModelContextProtocol
/// </summary>
internal static class ModelContextProtocolExtensions
{
    /// <summary>
    /// MCPNames
    /// </summary>
    /// <returns></returns>
    public static Dictionary<string, bool> MCPNames { get; set; } = new();

    /// <summary>
    /// 判断当前函数是否MCP
    /// </summary>
    /// <returns></returns>
    public static bool IsMCP(this string mcpName)
    {
        return MCPNames.ContainsKey(mcpName);
    }

    /// <summary>
    /// Map the tools exposed on this <see cref="IMcpClient"/> to a collection of <see cref="KernelFunction"/> instances for use with the Semantic Kernel.
    /// <param name="mcpClient">The <see cref="IMcpClient"/>.</param>
    /// <param name="cancellationToken">The optional <see cref="CancellationToken"/>.</param>
    /// </summary>
    public static async Task<IReadOnlyList<KernelFunction>> MapToFunctionsAsync(this McpClient mcpClient,
        CancellationToken cancellationToken = default)
    {
        var functions = new List<KernelFunction>();
        foreach (var tool in await mcpClient.ListToolsAsync(cancellationToken: cancellationToken).ConfigureAwait(false))
        {
            if (!MCPNames.TryGetValue(tool.Name, out _))
            {
                MCPNames.Add(tool.Name, true);
            }

            functions.Add(tool.ToKernelFunction(mcpClient, cancellationToken));
        }

        return functions;
    }

    private static KernelFunction ToKernelFunction(this McpClientTool tool, McpClient mcpClient,
        CancellationToken cancellationToken)
    {
        async Task<string> InvokeToolAsync(Kernel kernel, KernelFunction function, KernelArguments arguments,
            CancellationToken ct)
        {
            try
            {
                // Convert arguments to dictionary format expected by ModelContextProtocol
                Dictionary<string, object?> mcpArguments = [];
                foreach (var arg in arguments)
                {
                    if (arg.Value is not null)
                    {
                        mcpArguments[arg.Key] = function.ToArgumentValue(arg.Key, arg.Value);
                    }
                }

                var result = await mcpClient.CallToolAsync(
                    tool.Name,
                    mcpArguments.AsReadOnly(),
                    cancellationToken: ct
                ).ConfigureAwait(false);

                // Extract the text content from the result
                return string.Join("\n", result.Content
                    .Where(x => x.Type == "text")
                    .Select(c => c is TextContentBlock block ? block.Text : c.ToString()));
            }
            catch (Exception ex)
            {
                await Console.Error.WriteLineAsync($"Error invoking tool '{tool.Name}': {ex.Message}");
                throw;
            }
        }

        return KernelFunctionFactory.CreateFromMethod(
            method: InvokeToolAsync,
            functionName: tool.Name,
            description: tool.Description,
            parameters: tool.ToParameters(),
            returnParameter: ToReturnParameter()
        );
    }

    private static object ToArgumentValue(this KernelFunction function, string name, object value)
    {
        var parameterType = function.Metadata.Parameters.FirstOrDefault(p => p.Name == name)?.ParameterType;

        if (parameterType == null)
        {
            return value;
        }

        if (Nullable.GetUnderlyingType(parameterType) == typeof(int))
        {
            return Convert.ToInt32(value);
        }

        if (Nullable.GetUnderlyingType(parameterType) == typeof(double))
        {
            return Convert.ToDouble(value);
        }

        if (Nullable.GetUnderlyingType(parameterType) == typeof(bool))
        {
            return Convert.ToBoolean(value);
        }

        if (parameterType == typeof(List<string>))
        {
            return (value as IEnumerable<object>)?.ToList() ?? value;
        }

        if (parameterType == typeof(Dictionary<string, object>))
        {
            return (value as Dictionary<string, object>)?.ToDictionary(kvp => kvp.Key, kvp => kvp.Value) ?? value;
        }

        return value;
    }

    private static List<KernelParameterMetadata>? ToParameters(this McpClientTool tool)
    {
        var inputSchema = JsonSerializer.Deserialize<JsonSchema>(tool.JsonSchema.GetRawText());
        var properties = inputSchema?.Properties;
        if (properties == null)
        {
            return null;
        }

        HashSet<string> requiredProperties = [.. inputSchema!.Required ?? []];
        return properties.Select(kvp =>
            new KernelParameterMetadata(kvp.Key)
            {
                Description = kvp.Value.Description,
                ParameterType = ConvertParameterDataType(kvp.Value, requiredProperties.Contains(kvp.Key)),
                IsRequired = requiredProperties.Contains(kvp.Key)
            }).ToList();
    }

    private static KernelReturnParameterMetadata ToReturnParameter()
    {
        return new KernelReturnParameterMetadata
        {
            ParameterType = typeof(string),
        };
    }

    private static Type ConvertParameterDataType(JsonSchemaProperty property, bool required)
    {
        var type = property.Type switch
        {
            "string" => typeof(string),
            "integer" => typeof(int),
            "number" => typeof(double),
            "boolean" => typeof(bool),
            "array" => typeof(List<string>),
            "object" => typeof(Dictionary<string, object>),
            _ => typeof(object)
        };

        return !required && type.IsValueType ? typeof(Nullable<>).MakeGenericType(type) : type;
    }
}