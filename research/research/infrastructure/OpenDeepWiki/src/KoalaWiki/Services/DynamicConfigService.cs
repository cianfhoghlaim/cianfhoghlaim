using System.Collections.Concurrent;
using System.Text.Json;
using KoalaWiki.Domains;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Services;

/// <summary>
/// 动态配置服务 - 负责管理系统设置
/// 配置优先级：数据库 > 环境变量 > 默认值
/// </summary>
public class DynamicConfigService
{
    private readonly IKoalaWikiContext _context;
    private readonly IConfiguration _configuration;
    private readonly ILogger<DynamicConfigService> _logger;
    
    // 缓存配置值，避免频繁查询数据库
    private readonly ConcurrentDictionary<string, string?> _configCache = new();
    private DateTime _lastCacheUpdate = DateTime.MinValue;
    private readonly TimeSpan _cacheTimeout = TimeSpan.FromMinutes(5);

    public DynamicConfigService(
        IKoalaWikiContext context, 
        IConfiguration configuration, 
        ILogger<DynamicConfigService> logger)
    {
        _context = context;
        _configuration = configuration;
        _logger = logger;
    }

    /// <summary>
    /// 初始化系统设置 - 首次启动时调用
    /// </summary>
    public async Task InitializeAsync()
    {
        try
        {
            _logger.LogInformation("开始初始化系统设置...");

            var defaultSettings = GetDefaultSettings();
            
            foreach (var defaultSetting in defaultSettings)
            {
                var existing = await _context.SystemSettings
                    .FirstOrDefaultAsync(x => x.Key == defaultSetting.Key);

                if (existing == null)
                {
                    // 从环境变量或配置文件获取值
                    var envValue = GetEnvironmentValue(defaultSetting.Key, defaultSetting.Group);
                    
                    var setting = new SystemSetting
                    {
                        Id = Guid.NewGuid().ToString(),
                        Key = defaultSetting.Key,
                        Value = envValue ?? defaultSetting.DefaultValue,
                        Group = defaultSetting.Group,
                        ValueType = defaultSetting.ValueType,
                        Description = defaultSetting.Description,
                        IsSensitive = defaultSetting.IsSensitive,
                        RequiresRestart = defaultSetting.RequiresRestart,
                        DefaultValue = defaultSetting.DefaultValue,
                        Order = defaultSetting.Order,
                        IsEnabled = true,
                        CreatedAt = System.DateTime.UtcNow,
                        UpdatedAt = System.DateTime.UtcNow
                    };

                    await _context.SystemSettings.AddAsync(setting);
                    _logger.LogDebug("初始化设置：{Key} = {Value}", defaultSetting.Key, 
                        defaultSetting.IsSensitive ? "***" : (envValue ?? defaultSetting.DefaultValue));
                }
            }

            await _context.SaveChangesAsync();
            
            // 清空缓存，强制重新加载
            _configCache.Clear();
            _lastCacheUpdate = DateTime.MinValue;
            
            _logger.LogInformation("系统设置初始化完成");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "初始化系统设置失败");
            throw;
        }
    }

    /// <summary>
    /// 获取配置值
    /// </summary>
    public async Task<T?> GetValueAsync<T>(string key, T? defaultValue = default)
    {
        var stringValue = await GetStringValueAsync(key);
        
        if (string.IsNullOrEmpty(stringValue))
        {
            return defaultValue;
        }

        try
        {
            if (typeof(T) == typeof(string))
            {
                return (T)(object)stringValue;
            }
            
            if (typeof(T) == typeof(bool) || typeof(T) == typeof(bool?))
            {
                return (T)(object)bool.Parse(stringValue);
            }
            
            if (typeof(T) == typeof(int) || typeof(T) == typeof(int?))
            {
                return (T)(object)int.Parse(stringValue);
            }
            
            if (typeof(T).IsArray || typeof(T).GetInterfaces().Any(i => i.IsGenericType && i.GetGenericTypeDefinition() == typeof(IEnumerable<>)))
            {
                return JsonSerializer.Deserialize<T>(stringValue, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
            }

            return JsonSerializer.Deserialize<T>(stringValue, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "解析配置值失败：{Key}, 值：{Value}", key, stringValue);
            return defaultValue;
        }
    }

    /// <summary>
    /// 获取字符串配置值
    /// </summary>
    public async Task<string?> GetStringValueAsync(string key)
    {
        // 检查缓存
        if (_configCache.TryGetValue(key, out var cachedValue) && 
            System.DateTime.UtcNow - _lastCacheUpdate < _cacheTimeout)
        {
            return cachedValue;
        }

        try
        {
            // 从数据库获取
            var setting = await _context.SystemSettings
                .AsNoTracking()
                .FirstOrDefaultAsync(x => x.Key == key && x.IsEnabled);

            var value = setting?.Value;

            // 如果数据库中没有值，尝试从环境变量获取
            if (string.IsNullOrEmpty(value))
            {
                value = GetEnvironmentValue(key, setting?.Group);
            }

            // 如果仍然没有值，使用默认值
            if (string.IsNullOrEmpty(value))
            {
                value = setting?.DefaultValue;
            }

            // 更新缓存
            _configCache.TryAdd(key, value);
            
            return value;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取配置值失败：{Key}", key);
            return null;
        }
    }

    /// <summary>
    /// 更新配置值
    /// </summary>
    public async Task<bool> UpdateValueAsync(string key, string? value)
    {
        try
        {
            var setting = await _context.SystemSettings
                .FirstOrDefaultAsync(x => x.Key == key);

            if (setting == null)
            {
                _logger.LogWarning("配置项不存在：{Key}", key);
                return false;
            }

            setting.Value = value;
            setting.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            // 更新缓存
            _configCache.TryRemove(key, out _);
            _configCache.TryAdd(key, value);

            _logger.LogInformation("配置项已更新：{Key}", key);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "更新配置值失败：{Key}", key);
            return false;
        }
    }

    /// <summary>
    /// 批量更新配置
    /// </summary>
    public async Task<bool> BatchUpdateAsync(Dictionary<string, string?> keyValues)
    {
        try
        {
            var keys = keyValues.Keys.ToList();
            var settings = await _context.SystemSettings
                .Where(x => keys.Contains(x.Key))
                .ToListAsync();

            foreach (var setting in settings)
            {
                if (keyValues.TryGetValue(setting.Key, out var newValue))
                {
                    setting.Value = newValue;
                    setting.UpdatedAt = System.DateTime.UtcNow;
                    
                    // 更新缓存
                    _configCache.TryRemove(setting.Key, out _);
                    _configCache.TryAdd(setting.Key, newValue);
                }
            }

            await _context.SaveChangesAsync();
            _logger.LogInformation("批量更新配置完成，共 {Count} 项", settings.Count);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "批量更新配置失败");
            return false;
        }
    }

    /// <summary>
    /// 清空缓存
    /// </summary>
    public void ClearCache()
    {
        _configCache.Clear();
        _lastCacheUpdate = DateTime.MinValue;
        _logger.LogInformation("配置缓存已清空");
    }

    /// <summary>
    /// 从环境变量或配置文件获取值
    /// </summary>
    private string? GetEnvironmentValue(string key, string? group = null)
    {
        // 为特定键提供环境变量映射
        var envMappings = GetEnvironmentVariableMappings();
        
        // 首先检查特定的环境变量映射
        if (envMappings.TryGetValue(key, out var specificEnvKeys))
        {
            foreach (var envKey in specificEnvKeys)
            {
                var envValue = Environment.GetEnvironmentVariable(envKey);
                if (!string.IsNullOrEmpty(envValue))
                {
                    return envValue;
                }
                
                var configValue = _configuration[envKey];
                if (!string.IsNullOrEmpty(configValue))
                {
                    return configValue;
                }
            }
        }

        // 尝试多种环境变量命名方式
        var envVariations = new List<string> { key };
        
        if (!string.IsNullOrEmpty(group))
        {
            envVariations.Add($"{group}_{key}");
            envVariations.Add($"{group.ToUpper()}_{key.ToUpper()}");
        }
        
        envVariations.Add(key.ToUpper());
        envVariations.Add(key.ToUpper().Replace(".", "_"));

        // 先尝试环境变量
        foreach (var variation in envVariations)
        {
            var envValue = Environment.GetEnvironmentVariable(variation);
            if (!string.IsNullOrEmpty(envValue))
            {
                return envValue;
            }
        }

        // 再尝试配置文件
        foreach (var variation in envVariations)
        {
            var configValue = _configuration[variation];
            if (!string.IsNullOrEmpty(configValue))
            {
                return configValue;
            }
        }

        // 如果是分组配置，尝试从分组节点获取
        if (!string.IsNullOrEmpty(group))
        {
            var sectionValue = _configuration.GetSection(group)[key];
            if (!string.IsNullOrEmpty(sectionValue))
            {
                return sectionValue;
            }
        }

        return null;
    }

    /// <summary>
    /// 获取环境变量映射表
    /// </summary>
    private Dictionary<string, string[]> GetEnvironmentVariableMappings()
    {
        return new Dictionary<string, string[]>
        {
            // OpenAI 配置映射
            { "ChatModel", new[] { "CHAT_MODEL", "ChatModel" } },
            { "AnalysisModel", new[] { "ANALYSIS_MODEL", "AnalysisModel" } },
            { "ChatApiKey", new[] { "CHAT_API_KEY", "ChatApiKey" } },
            { "Endpoint", new[] { "ENDPOINT", "Endpoint" } },
            { "ModelProvider", new[] { "MODEL_PROVIDER", "ModelProvider" } },
            { "MaxFileLimit", new[] { "MAX_FILE_LIMIT", "MaxFileLimit" } },
            { "DeepResearchModel", new[] { "DEEP_RESEARCH_MODEL", "DeepResearchModel" } },
            { "EnableMem0", new[] { "ENABLE_MEM0", "EnableMem0" } },
            { "Mem0ApiKey", new[] { "MEM0_API_KEY", "Mem0ApiKey" } },
            { "Mem0Endpoint", new[] { "MEM0_ENDPOINT", "Mem0Endpoint" } },
            { "Temperature", new[] { "TEMPERATURE", "Temperature" } },
            { "MaxTokens", new[] { "MAX_TOKENS", "MaxTokens" } },
            { "TopP", new[] { "TOP_P", "TopP" } },
            { "FrequencyPenalty", new[] { "FREQUENCY_PENALTY", "FrequencyPenalty" } },
            { "PresencePenalty", new[] { "PRESENCE_PENALTY", "PresencePenalty" } },
            { "CustomBodyParams", new[] { "CUSTOM_BODY_PARAMS", "CustomBodyParams" } },
            
            // Document 配置映射
            { "EnableIncrementalUpdate", new[] { "ENABLE_INCREMENTAL_UPDATE", "EnableIncrementalUpdate" } },
            { "EnableSmartFilter", new[] { "ENABLE_SMART_FILTER", "EnableSmartFilter" } },
            { "CatalogueFormat", new[] { "CATALOGUE_FORMAT", "CatalogueFormat" } },
            { "EnableCodeDependencyAnalysis", new[] { "ENABLE_CODED_DEPENDENCY_ANALYSIS", "EnableCodeDependencyAnalysis" } },
            { "EnableWarehouseFunctionPromptTask", new[] { "ENABLE_WAREHOUSE_FUNCTION_PROMPT_TASK", "EnableWarehouseFunctionPromptTask" } },
            { "EnableWarehouseDescriptionTask", new[] { "ENABLE_WAREHOUSE_DESCRIPTION_TASK", "EnableWarehouseDescriptionTask" } },
            { "EnableFileCommit", new[] { "ENABLE_FILE_COMMIT", "EnableFileCommit" } },
            { "RefineAndEnhanceQuality", new[] { "REFINE_AND_ENHANCE_QUALITY", "RefineAndEnhanceQuality" } },
            { "EnableWarehouseCommit", new[] { "ENABLE_WAREHOUSE_COMMIT", "EnableWarehouseCommit" } },
            { "EnableCodeCompression", new[] { "ENABLE_CODE_COMPRESSION", "EnableCodeCompression" } },
            { "MaxFileReadCount", new[] { "MAX_FILE_READ_COUNT", "MaxFileReadCount" } },
            
            // GitHub 配置映射
            { "GitHub.ClientId", new[] { "GITHUB_CLIENT_ID", "Github:ClientId" } },
            { "GitHub.ClientSecret", new[] { "GITHUB_CLIENT_SECRET", "Github:ClientSecret" } },
            { "GitHub.Token", new[] { "GITHUB_TOKEN", "Github:Token" } },
            
            // Gitee 配置映射
            { "Gitee.ClientId", new[] { "GITEE_CLIENT_ID", "Gitee:ClientId" } },
            { "Gitee.ClientSecret", new[] { "GITEE_CLIENT_SECRET", "Gitee:ClientSecret" } },
            { "Gitee.Token", new[] { "GITEE_TOKEN", "Gitee:Token" } },
            
            // JWT 配置映射
            { "Secret", new[] { "JWT_SECRET", "Jwt:Secret" } },
            { "Issuer", new[] { "JWT_ISSUER", "Jwt:Issuer" } },
            { "Audience", new[] { "JWT_AUDIENCE", "Jwt:Audience" } },
            { "ExpireMinutes", new[] { "JWT_EXPIRE_MINUTES", "Jwt:ExpireMinutes" } },
            { "RefreshExpireMinutes", new[] { "JWT_REFRESH_EXPIRE_MINUTES", "Jwt:RefreshExpireMinutes" } }
        };
    }

    /// <summary>
    /// 获取默认设置定义
    /// </summary>
    private List<SystemSetting> GetDefaultSettings()
    {
        return new List<SystemSetting>
        {
            // OpenAI配置
            new() { Key = "ChatModel", Group = "OpenAI", ValueType = "string", Description = "聊天模型", IsSensitive = false, RequiresRestart = true, DefaultValue = "", Order = 1 },
            new() { Key = "AnalysisModel", Group = "OpenAI", ValueType = "string", Description = "分析模型", IsSensitive = false, RequiresRestart = true, DefaultValue = "", Order = 2 },
            new() { Key = "ChatApiKey", Group = "OpenAI", ValueType = "string", Description = "API密钥", IsSensitive = true, RequiresRestart = true, DefaultValue = "", Order = 3 },
            new() { Key = "Endpoint", Group = "OpenAI", ValueType = "string", Description = "API地址", IsSensitive = false, RequiresRestart = true, DefaultValue = "", Order = 4 },
            new() { Key = "ModelProvider", Group = "OpenAI", ValueType = "string", Description = "模型提供商", IsSensitive = false, RequiresRestart = true, DefaultValue = "OpenAI", Order = 5 },
            new() { Key = "MaxFileLimit", Group = "OpenAI", ValueType = "int", Description = "最大文件限制", IsSensitive = false, RequiresRestart = false, DefaultValue = "10", Order = 6 },
            new() { Key = "DeepResearchModel", Group = "OpenAI", ValueType = "string", Description = "深度研究模型", IsSensitive = false, RequiresRestart = true, DefaultValue = "", Order = 7 },
            new() { Key = "EnableMem0", Group = "OpenAI", ValueType = "bool", Description = "启用Mem0", IsSensitive = false, RequiresRestart = true, DefaultValue = "false", Order = 8 },
            new() { Key = "Mem0ApiKey", Group = "OpenAI", ValueType = "string", Description = "Mem0 API密钥", IsSensitive = true, RequiresRestart = true, DefaultValue = "", Order = 9 },
            new() { Key = "Mem0Endpoint", Group = "OpenAI", ValueType = "string", Description = "Mem0端点", IsSensitive = false, RequiresRestart = true, DefaultValue = "", Order = 10 },
            new() { Key = "Temperature", Group = "OpenAI", ValueType = "string", Description = "模型温度 (0.0-2.0)", IsSensitive = false, RequiresRestart = false, DefaultValue = "0.7", Order = 11 },
            new() { Key = "MaxTokens", Group = "OpenAI", ValueType = "int", Description = "最大令牌数", IsSensitive = false, RequiresRestart = false, DefaultValue = "4000", Order = 12 },
            new() { Key = "TopP", Group = "OpenAI", ValueType = "string", Description = "Top P 采样 (0.0-1.0)", IsSensitive = false, RequiresRestart = false, DefaultValue = "1.0", Order = 13 },
            new() { Key = "FrequencyPenalty", Group = "OpenAI", ValueType = "string", Description = "频率惩罚 (-2.0-2.0)", IsSensitive = false, RequiresRestart = false, DefaultValue = "0.0", Order = 14 },
            new() { Key = "PresencePenalty", Group = "OpenAI", ValueType = "string", Description = "存在惩罚 (-2.0-2.0)", IsSensitive = false, RequiresRestart = false, DefaultValue = "0.0", Order = 15 },
            new() { Key = "CustomBodyParams", Group = "OpenAI", ValueType = "string", Description = "自定义请求body参数，格式: key1=value1,key2=value2", IsSensitive = false, RequiresRestart = true, DefaultValue = "", Order = 16 },

            // Document配置
            new() { Key = "EnableIncrementalUpdate", Group = "Document", ValueType = "bool", Description = "启用增量更新", IsSensitive = false, RequiresRestart = false, DefaultValue = "true", Order = 17 },
            new() { Key = "ExcludedFiles", Group = "Document", ValueType = "array", Description = "排除的文件", IsSensitive = false, RequiresRestart = false, DefaultValue = GetDefaultExcludedFilesJson(), Order = 18 },
            new() { Key = "ExcludedFolders", Group = "Document", ValueType = "array", Description = "排除的文件夹", IsSensitive = false, RequiresRestart = false, DefaultValue = GetDefaultExcludedFoldersJson(), Order = 19 },
            new() { Key = "EnableSmartFilter", Group = "Document", ValueType = "bool", Description = "启用智能过滤", IsSensitive = false, RequiresRestart = false, DefaultValue = "true", Order = 20 },
            new() { Key = "CatalogueFormat", Group = "Document", ValueType = "string", Description = "目录结构格式", IsSensitive = false, RequiresRestart = false, DefaultValue = "compact", Order = 21 },
            new() { Key = "EnableCodeDependencyAnalysis", Group = "Document", ValueType = "bool", Description = "启用代码依赖分析", IsSensitive = false, RequiresRestart = false, DefaultValue = "false", Order = 22 },
            new() { Key = "EnableWarehouseFunctionPromptTask", Group = "Document", ValueType = "bool", Description = "启用仓库功能提示任务", IsSensitive = false, RequiresRestart = false, DefaultValue = "true", Order = 23 },
            new() { Key = "EnableWarehouseDescriptionTask", Group = "Document", ValueType = "bool", Description = "启用仓库描述任务", IsSensitive = false, RequiresRestart = false, DefaultValue = "true", Order = 24 },
            new() { Key = "EnableFileCommit", Group = "Document", ValueType = "bool", Description = "启用文件提交", IsSensitive = false, RequiresRestart = false, DefaultValue = "true", Order = 25 },
            new() { Key = "RefineAndEnhanceQuality", Group = "Document", ValueType = "bool", Description = "精炼并提高质量", IsSensitive = false, RequiresRestart = false, DefaultValue = "true", Order = 26 },
            new() { Key = "EnableWarehouseCommit", Group = "Document", ValueType = "bool", Description = "启用仓库提交", IsSensitive = false, RequiresRestart = false, DefaultValue = "true", Order = 27 },
            new() { Key = "EnableCodeCompression", Group = "Document", ValueType = "bool", Description = "启用代码压缩", IsSensitive = false, RequiresRestart = false, DefaultValue = "false", Order = 28 },
            new() { Key = "MaxFileReadCount", Group = "Document", ValueType = "int", Description = "最大文件读取数量", IsSensitive = false, RequiresRestart = false, DefaultValue = "15", Order = 29 },

            // JWT配置
            new() { Key = "Secret", Group = "JWT", ValueType = "string", Description = "JWT密钥", IsSensitive = true, RequiresRestart = true, DefaultValue = "", Order = 30 },
            new() { Key = "Issuer", Group = "JWT", ValueType = "string", Description = "颁发者", IsSensitive = false, RequiresRestart = true, DefaultValue = "KoalaWiki", Order = 31 },
            new() { Key = "Audience", Group = "JWT", ValueType = "string", Description = "接收者", IsSensitive = false, RequiresRestart = true, DefaultValue = "KoalaWiki", Order = 32 },
            new() { Key = "ExpireMinutes", Group = "JWT", ValueType = "int", Description = "过期时间（分钟）", IsSensitive = false, RequiresRestart = false, DefaultValue = "1440", Order = 33 },
            new() { Key = "RefreshExpireMinutes", Group = "JWT", ValueType = "int", Description = "刷新令牌过期时间（分钟）", IsSensitive = false, RequiresRestart = false, DefaultValue = "10080", Order = 34 },

            // GitHub配置
            new() { Key = "GitHub.ClientId", Group = "GitHub", ValueType = "string", Description = "GitHub客户端ID", IsSensitive = false, RequiresRestart = true, DefaultValue = "", Order = 35 },
            new() { Key = "GitHub.ClientSecret", Group = "GitHub", ValueType = "string", Description = "GitHub客户端密钥", IsSensitive = true, RequiresRestart = true, DefaultValue = "", Order = 36 },
            new() { Key = "GitHub.Token", Group = "GitHub", ValueType = "string", Description = "GitHub访问令牌", IsSensitive = true, RequiresRestart = true, DefaultValue = "", Order = 37 },

            // Gitee配置
            new() { Key = "Gitee.ClientId", Group = "Gitee", ValueType = "string", Description = "Gitee客户端ID", IsSensitive = false, RequiresRestart = true, DefaultValue = "", Order = 38 },
            new() { Key = "Gitee.ClientSecret", Group = "Gitee", ValueType = "string", Description = "Gitee客户端密钥", IsSensitive = true, RequiresRestart = true, DefaultValue = "", Order = 39 },
            new() { Key = "Gitee.Token", Group = "Gitee", ValueType = "string", Description = "Gitee访问令牌", IsSensitive = true, RequiresRestart = true, DefaultValue = "", Order = 40 }
        };
    }

    /// <summary>
    /// 获取默认排除文件的JSON字符串
    /// </summary>
    private static string GetDefaultExcludedFilesJson()
    {
        var excludedFiles = new[]
        {
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "npm-shrinkwrap.json",
            "poetry.lock",
            "Pipfile.lock",
            "requirements.txt.lock",
            "Cargo.lock",
            "composer.lock",
            ".lock",
            ".DS_Store",
            "Thumbs.db",
            "desktop.ini",
            "*.lnk",
            ".env",
            ".env.*",
            "*.env",
            "*.cfg",
            "*.ini",
            ".flaskenv",
            ".gitignore",
            ".gitattributes",
            ".gitmodules",
            ".github",
            ".gitlab-ci.yml",
            ".prettierrc",
            ".eslintrc",
            ".eslintignore",
            ".stylelintrc",
            ".editorconfig",
            ".jshintrc",
            ".pylintrc",
            ".flake8",
            "mypy.ini",
            "pyproject.toml",
            "tsconfig.json",
            "webpack.config.js",
            "babel.config.js",
            "rollup.config.js",
            "jest.config.js",
            "karma.conf.js",
            "vite.config.js",
            "next.config.js",
            "*.min.js",
            "*.min.css",
            "*.bundle.js",
            "*.bundle.css",
            "*.map",
            "*.gz",
            "*.zip",
            "*.tar",
            "*.tgz",
            "*.rar",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "*.so",
            "*.dll",
            "*.class",
            "*.exe",
            "*.o",
            "*.a",
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.gif",
            "*.ico",
            "*.svg",
            "*.webp",
            "*.mp3",
            "*.mp4",
            "*.wav",
            "*.avi",
            "*.mov",
            "*.webm",
            "*.csv",
            "*.tsv",
            "*.xls",
            "*.xlsx",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            "*.pdf",
            "*.docx",
            "*.pptx",
            ".doc",
            "*.ppt",
            "*.xls",
            "*.resw",
            "*.nupkg",
            "*.jar",
            "*.plist",
            "*.pyc",
            "*.log"
        };

        return JsonSerializer.Serialize(excludedFiles);
    }

    /// <summary>
    /// 获取默认排除文件夹的JSON字符串
    /// </summary>
    private static string GetDefaultExcludedFoldersJson()
    {
        var excludedFolders = new[]
        {
            "./.venv/",
            "./venv/",
            "./env/",
            "./virtualenv/",
            "./node_modules/",
            "./bower_components/",
            "./jspm_packages/",
            "./.git/",
            "./.svn/",
            "./.hg/",
            "./.bzr/",
            "./__pycache__/",
            "./.pytest_cache/",
            "./.mypy_cache/",
            "./.ruff_cache/",
            "./.coverage/",
            "./dist/",
            "./build/",
            "./out/",
            "./target/",
            "./bin/",
            "./obj/",
            "./docs/",
            "./_docs/",
            "./site-docs/",
            "./_site/",
            "./.idea/",
            "./.vscode/",
            "./.vs/",
            "./.eclipse/",
            "./.settings/",
            "./logs/",
            "./log/",
            "./tmp/",
            "./temp/",
            "./.eng",
            "./.idea/",
            "./.vscode/"
        };

        return JsonSerializer.Serialize(excludedFolders);
    }
} 