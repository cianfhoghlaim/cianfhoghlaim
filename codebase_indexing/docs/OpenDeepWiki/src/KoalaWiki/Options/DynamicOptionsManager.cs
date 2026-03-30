namespace KoalaWiki.Options;

/// <summary>
/// 动态配置管理器 - 统一管理所有Options类的动态配置
/// </summary>
public class DynamicOptionsManager
{
    private readonly DynamicConfigService _configService;
    private readonly ILogger<DynamicOptionsManager> _logger;

    public DynamicOptionsManager(DynamicConfigService configService, ILogger<DynamicOptionsManager> logger)
    {
        _configService = configService;
        _logger = logger;
    }

    /// <summary>
    /// 初始化所有Options类的动态配置
    /// </summary>
    public async Task InitializeAsync()
    {
        try
        {
            _logger.LogInformation("开始初始化动态配置...");

            // 初始化系统设置
            await _configService.InitializeAsync();

            // 加载各个Options类的配置
            await LoadOpenAIOptionsAsync();
            await LoadDocumentOptionsAsync();
            await LoadJwtOptionsAsync();
            await LoadGithubOptionsAsync();
            await LoadGiteeOptionsAsync();

            _logger.LogInformation("动态配置初始化完成");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "动态配置初始化失败");
            throw;
        }
    }

    /// <summary>
    /// 加载OpenAI配置
    /// </summary>
    private async Task LoadOpenAIOptionsAsync()
    {
        OpenAIOptions.ChatModel = await _configService.GetValueAsync<string>("ChatModel") ?? "";
        OpenAIOptions.AnalysisModel = await _configService.GetValueAsync<string>("AnalysisModel") ?? "";
        OpenAIOptions.ChatApiKey = await _configService.GetValueAsync<string>("ChatApiKey") ?? "";
        OpenAIOptions.Endpoint = await _configService.GetValueAsync<string>("Endpoint") ?? "";
        OpenAIOptions.ModelProvider = await _configService.GetValueAsync<string>("ModelProvider") ?? "OpenAI";
        OpenAIOptions.DeepResearchModel = await _configService.GetValueAsync<string>("DeepResearchModel") ?? "";
        OpenAIOptions.EnableMem0 = await _configService.GetValueAsync<bool>("EnableMem0", false);
        OpenAIOptions.Mem0ApiKey = await _configService.GetValueAsync<string>("Mem0ApiKey") ?? "";
        OpenAIOptions.Mem0Endpoint = await _configService.GetValueAsync<string>("Mem0Endpoint") ?? "";

        // 如果DeepResearchModel为空，使用ChatModel
        if (string.IsNullOrEmpty(OpenAIOptions.DeepResearchModel))
        {
            OpenAIOptions.DeepResearchModel = OpenAIOptions.ChatModel;
        }

        // 如果AnalysisModel为空，使用ChatModel
        if (string.IsNullOrEmpty(OpenAIOptions.AnalysisModel))
        {
            OpenAIOptions.AnalysisModel = OpenAIOptions.ChatModel;
        }

        _logger.LogDebug("OpenAI配置已加载");
    }

    /// <summary>
    /// 加载文档配置
    /// </summary>
    private async Task LoadDocumentOptionsAsync()
    {
        DocumentOptions.EnableIncrementalUpdate =
            await _configService.GetValueAsync<bool>("EnableIncrementalUpdate", true);
        DocumentOptions.ExcludedFiles =
            await _configService.GetValueAsync<string[]>("ExcludedFiles") ?? Array.Empty<string>();
        DocumentOptions.ExcludedFolders =
            await _configService.GetValueAsync<string[]>("ExcludedFolders") ?? Array.Empty<string>();
        DocumentOptions.EnableSmartFilter = await _configService.GetValueAsync<bool>("EnableSmartFilter", true);
        DocumentOptions.CatalogueFormat = await _configService.GetValueAsync<string>("CatalogueFormat") ?? "compact";
        DocumentOptions.EnableWarehouseFunctionPromptTask =
            await _configService.GetValueAsync<bool>("EnableWarehouseFunctionPromptTask", true);
        DocumentOptions.EnableWarehouseDescriptionTask =
            await _configService.GetValueAsync<bool>("EnableWarehouseDescriptionTask", true);
        DocumentOptions.EnableFileCommit = await _configService.GetValueAsync<bool>("EnableFileCommit", true);
        DocumentOptions.RefineAndEnhanceQuality =
            await _configService.GetValueAsync<bool>("RefineAndEnhanceQuality", true);
        DocumentOptions.EnableWarehouseCommit = await _configService.GetValueAsync<bool>("EnableWarehouseCommit", true);
        DocumentOptions.ReadMaxTokens = await _configService.GetValueAsync<int>("ReadMaxTokens", 90000);

        _logger.LogDebug("Document配置已加载");
    }

    /// <summary>
    /// 加载JWT配置
    /// </summary>
    private async Task LoadJwtOptionsAsync()
    {
        // JWT配置需要特殊处理，因为它不是静态类
        // 这里仅作为示例，实际使用时需要通过依赖注入获取配置
        _logger.LogDebug("JWT配置加载跳过（需要通过依赖注入处理）");
    }

    /// <summary>
    /// 加载GitHub配置
    /// </summary>
    private async Task LoadGithubOptionsAsync()
    {
        // 使用带组名前缀的键来避免与Gitee冲突
        GithubOptions.ClientId = await GetGroupValueAsync("GitHub", "ClientId") ?? "";
        GithubOptions.ClientSecret = await GetGroupValueAsync("GitHub", "ClientSecret") ?? "";
        GithubOptions.Token = await GetGroupValueAsync("GitHub", "Token") ?? "";

        _logger.LogDebug("GitHub配置已加载");
    }

    /// <summary>
    /// 加载Gitee配置
    /// </summary>
    private async Task LoadGiteeOptionsAsync()
    {
        // 使用带组名前缀的键来避免与GitHub冲突
        GiteeOptions.ClientId = await GetGroupValueAsync("Gitee", "ClientId") ?? "";
        GiteeOptions.ClientSecret = await GetGroupValueAsync("Gitee", "ClientSecret") ?? "";
        GiteeOptions.Token = await GetGroupValueAsync("Gitee", "Token") ?? "";

        _logger.LogDebug("Gitee配置已加载");
    }

    /// <summary>
    /// 根据分组获取配置值
    /// </summary>
    private async Task<string?> GetGroupValueAsync(string group, string key)
    {
        // 首先尝试获取带组前缀的值
        var groupKey = $"{group}.{key}";
        var value = await _configService.GetStringValueAsync(groupKey);

        // 如果没有找到，尝试使用不带组前缀的键
        if (string.IsNullOrEmpty(value))
        {
            value = await _configService.GetStringValueAsync(key);
        }

        return value;
    }

    /// <summary>
    /// 重新加载所有配置
    /// </summary>
    public async Task ReloadAsync()
    {
        _logger.LogInformation("重新加载动态配置...");

        // 清空缓存
        _configService.ClearCache();

        // 重新加载所有配置
        await LoadOpenAIOptionsAsync();
        await LoadDocumentOptionsAsync();
        await LoadJwtOptionsAsync();
        await LoadGithubOptionsAsync();
        await LoadGiteeOptionsAsync();

        _logger.LogInformation("动态配置重新加载完成");
    }

    /// <summary>
    /// 更新配置并重新加载
    /// </summary>
    public async Task UpdateAndReloadAsync(string key, string? value)
    {
        var success = await _configService.UpdateValueAsync(key, value);
        if (success)
        {
            await ReloadAsync();
            _logger.LogInformation("配置已更新并重新加载：{Key}", key);
        }
        else
        {
            _logger.LogWarning("配置更新失败：{Key}", key);
        }
    }

    /// <summary>
    /// 批量更新配置并重新加载
    /// </summary>
    public async Task BatchUpdateAndReloadAsync(Dictionary<string, string?> keyValues)
    {
        var success = await _configService.BatchUpdateAsync(keyValues);
        if (success)
        {
            await ReloadAsync();
            _logger.LogInformation("批量配置已更新并重新加载，共 {Count} 项", keyValues.Count);
        }
        else
        {
            _logger.LogWarning("批量配置更新失败");
        }
    }
}