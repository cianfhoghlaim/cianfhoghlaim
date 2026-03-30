namespace KoalaWiki.Options;

public class DocumentOptions
{
    public const string Name = "Document";

    /// <summary>
    /// 是否启用增量更新
    /// </summary>
    /// <returns></returns>
    public static bool EnableIncrementalUpdate { get; set; } = true;

    /// <summary>
    /// 排除的文件
    /// </summary>
    /// <returns></returns>
    public static string[] ExcludedFiles { get; set; } = [];

    /// <summary>
    /// 排除的文件夹
    /// </summary>
    /// <returns></returns>
    public static string[] ExcludedFolders { get; set; } = [];

    /// <summary>
    /// 是否启用智能过滤
    /// </summary>
    /// <returns></returns>
    public static bool EnableSmartFilter { get; set; } = true;

    /// <summary>
    /// 目录结构格式 (compact, json, pathlist, unix)
    /// </summary>
    /// <returns></returns>
    public static string CatalogueFormat { get; set; } = "compact";

    /// <summary>
    /// 是否启用仓库功能提示任务
    /// </summary>
    public static bool EnableWarehouseFunctionPromptTask { get; set; } = true;

    /// <summary>
    /// 是否启用仓库描述任务
    /// </summary>
    public static bool EnableWarehouseDescriptionTask { get; set; } = true;

    /// <summary>
    /// 是否启用文件提交
    /// </summary>
    /// <returns></returns>
    public static bool EnableFileCommit { get; set; } = true;

    /// <summary>
    /// 精炼并且提高质量
    /// </summary>
    /// <returns></returns>
    public static bool RefineAndEnhanceQuality { get; set; } = false;

    /// <summary>
    /// 是否启用仓库提交
    /// </summary>
    /// <returns></returns>
    public static bool EnableWarehouseCommit { get; set; } = true;

    /// <summary>
    /// 限制单个AI读取的最大token上下文比例是当前模型的多少，范围0.1-1.0
    /// </summary>
    /// <returns></returns>
    public static int ReadMaxTokens { get; set; } = 80000;

    /// <summary>
    /// Git代理设置
    /// 支持HTTP/HTTPS代理，格式：http://proxy-server:port 或 https://proxy-server:port
    /// 可通过环境变量GIT_PROXY进行配置
    /// </summary>
    /// <returns></returns>
    public static string? Proxy { get; set; }

    /// <summary>
    /// 是否启用Agent工具插件
    /// </summary>
    /// <returns></returns>
    public static bool EnableAgentTool { get; set; } = false;
    
    /// <summary>
    /// 是否启用Wiki功能
    /// </summary>
    public static bool EnableWiki { get; set; } = true;

    public static Dictionary<string, string> McpStreamable = new Dictionary<string, string>();

    public static void InitConfig(IConfiguration configuration)
    {
        var mcpStreamable = Environment.GetEnvironmentVariable("MCP_STREAMABLE");
        if (!string.IsNullOrEmpty(mcpStreamable))
        {
            var pairs = mcpStreamable.Split(',', StringSplitOptions.RemoveEmptyEntries);
            foreach (var pair in pairs)
            {
                var keyValue = pair.Split('=', 2, StringSplitOptions.RemoveEmptyEntries);
                if (keyValue.Length == 2)
                {
                    McpStreamable[keyValue[0].Trim()] = keyValue[1].Trim();
                }
            }
        }
        
        
        configuration.GetSection(Name).Get<DocumentOptions>();

        var enableWarehouseCommit = configuration.GetValue<bool?>($"ENABLE_WAREHOUSE_COMMIT") ?? true;

        EnableWarehouseCommit = enableWarehouseCommit;

        var enableFileCommit = configuration.GetValue<bool?>($"ENABLE_FILE_COMMIT") ?? true;

        EnableFileCommit = enableFileCommit;

        var enableIncrementalUpdate = configuration.GetValue<string>($"ENABLE_INCREMENTAL_UPDATE");
        if (!string.IsNullOrEmpty(enableIncrementalUpdate))
        {
            if (bool.TryParse(enableIncrementalUpdate, out var enable))
            {
                EnableIncrementalUpdate = enable;
            }
        }

        var refineAndEnhanceQuality =
            configuration.GetValue<string>($"REFINE_AND_ENHANCE_QUALITY");

        if (!string.IsNullOrEmpty(refineAndEnhanceQuality))
        {
            RefineAndEnhanceQuality = bool.TryParse(refineAndEnhanceQuality, out var enable) && enable;
        }

        var enableWarehouseFunctionPromptTask =
            configuration.GetValue<string>($"ENABLE_WAREHOUSE_FUNCTION_PROMPT_TASK");

        if (!string.IsNullOrEmpty(enableWarehouseFunctionPromptTask))
        {
            if (bool.TryParse(enableWarehouseFunctionPromptTask, out var enable))
            {
                EnableWarehouseFunctionPromptTask = enable;
            }
        }

        var enableWarehouseDescriptionTask = configuration.GetValue<string>($"ENABLE_WAREHOUSE_DESCRIPTION_TASK");
        if (!string.IsNullOrEmpty(enableWarehouseDescriptionTask))
        {
            if (bool.TryParse(enableWarehouseDescriptionTask, out var enable))
            {
                EnableWarehouseDescriptionTask = enable;
            }
        }

        var catalogueFormat = configuration.GetValue<string>($"CATALOGUE_FORMAT");
        if (!string.IsNullOrEmpty(catalogueFormat))
        {
            CatalogueFormat = catalogueFormat.ToLower();
        }

        var maxFileReadCount = configuration.GetValue<string>($"READ_MAX_TOKENS");
        if (!string.IsNullOrEmpty(maxFileReadCount))
        {
            if (int.TryParse(maxFileReadCount, out var count) && count >= 0)
            {
                ReadMaxTokens = count;
            }
        }

        var proxy = configuration.GetValue<string>($"GIT_PROXY");
        if (!string.IsNullOrEmpty(proxy))
        {
            Proxy = proxy;
        }

        var enableAgentTool = configuration.GetValue<string>($"ENABLE_AGENT_TOOL");
        if (!string.IsNullOrEmpty(enableAgentTool))
        {
            if (bool.TryParse(enableAgentTool, out var enable))
            {
                EnableAgentTool = enable;
            }
        }
        
        var enableWiki = configuration.GetValue<string>($"ENABLE_WIKI");
        if (!string.IsNullOrEmpty(enableWiki))
        {
            if (bool.TryParse(enableWiki, out var enable))
            {
                EnableWiki = enable;
            }
        }
    }
}