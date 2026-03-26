using FastService;
using KoalaWiki.Domains;
using KoalaWiki.Dto;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;

namespace KoalaWiki.Services;

[Tags("系统设置管理")]
[FastService.Route("/api/SystemSetting")]
[Filter(typeof(ResultFilter))]
[Authorize(Roles = "admin")] // 只有管理员可以访问
public class SystemSettingService(
    IKoalaWikiContext context,
    DynamicConfigService configService,
    DynamicOptionsManager dynamicOptionsManager,
    ILogger<SystemSettingService> logger) : FastApi
{
    /// <summary>
    /// 获取所有系统设置分组
    /// </summary>
    [HttpGet("/groups")]
    public async Task<List<SystemSettingGroupOutput>> GetSettingGroupsAsync()
    {
        var settings = await context.SystemSettings
            .AsNoTracking()
            .Where(x => x.IsEnabled)
            .OrderBy(x => x.Group)
            .ThenBy(x => x.Order)
            .ToListAsync();

        var groups = settings
            .GroupBy(x => x.Group)
            .Select(g => new SystemSettingGroupOutput
            {
                Group = g.Key,
                Settings = g.Select(MapToOutput).ToList()
            })
            .ToList();

        return groups;
    }

    /// <summary>
    /// 根据分组获取系统设置
    /// </summary>
    [HttpGet("/group/{group}")]
    public async Task<List<SystemSettingOutput>> GetSettingsByGroupAsync(string group)
    {
        var settings = await context.SystemSettings
            .AsNoTracking()
            .Where(x => x.Group == group && x.IsEnabled)
            .OrderBy(x => x.Order)
            .ToListAsync();

        return settings.Select(MapToOutput).ToList();
    }

    /// <summary>
    /// 获取单个系统设置
    /// </summary>
    [HttpGet("/{key}")]
    public async Task<SystemSettingOutput?> GetSettingAsync(string key)
    {
        var setting = await context.SystemSettings
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Key == key && x.IsEnabled);

        return setting != null ? MapToOutput(setting) : null;
    }

    /// <summary>
    /// 更新单个系统设置
    /// </summary>
    [HttpPut("/{key}")]
    public async Task<bool> UpdateSettingAsync(string key, [FromBody] string? value)
    {
        logger.LogInformation("更新系统设置：{Key} = {Value}", key, IsKeySensitive(key) ? "***" : value);

        var result = await configService.UpdateValueAsync(key, value);

        if (result)
        {
            logger.LogInformation("系统设置已更新：{Key}", key);
        }

        await dynamicOptionsManager.InitializeAsync();

        return result;
    }

    /// <summary>
    /// 批量更新系统设置
    /// </summary>
    [HttpPut("/batch")]
    public async Task<bool> BatchUpdateSettingsAsync(BatchUpdateSystemSettingsInput input)
    {
        logger.LogInformation("批量更新系统设置，共 {Count} 项", input.Settings.Count);

        var keyValues = input.Settings.ToDictionary(s => s.Key, s => s.Value);
        var result = await configService.BatchUpdateAsync(keyValues);

        if (result)
        {
            logger.LogInformation("批量更新系统设置完成");
        }
        await dynamicOptionsManager.InitializeAsync();

        return result;
    }

    /// <summary>
    /// 创建新的系统设置
    /// </summary>
    [HttpPost("/")]
    public async Task<SystemSettingOutput> CreateSettingAsync(SystemSettingInput input)
    {
        // 检查是否已存在
        var existing = await context.SystemSettings
            .FirstOrDefaultAsync(x => x.Key == input.Key);

        if (existing != null)
        {
            throw new Exception($"设置项已存在：{input.Key}");
        }

        var setting = new SystemSetting
        {
            Id = Guid.NewGuid().ToString(),
            Key = input.Key,
            Value = input.Value,
            Group = input.Group,
            ValueType = input.ValueType,
            Description = input.Description,
            IsSensitive = input.IsSensitive,
            RequiresRestart = input.RequiresRestart,
            DefaultValue = input.DefaultValue,
            Order = input.Order,
            IsEnabled = true,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await context.SystemSettings.AddAsync(setting);
        await context.SaveChangesAsync();

        // 清空配置缓存
        configService.ClearCache();

        logger.LogInformation("创建系统设置：{Key}", input.Key);
        await dynamicOptionsManager.InitializeAsync();

        return MapToOutput(setting);
    }

    /// <summary>
    /// 删除系统设置
    /// </summary>
    [HttpDelete("/{key}")]
    public async Task<bool> DeleteSettingAsync(string key)
    {
        var setting = await context.SystemSettings
            .FirstOrDefaultAsync(x => x.Key == key);

        if (setting == null)
        {
            return false;
        }

        context.SystemSettings.Remove(setting);
        await context.SaveChangesAsync();

        // 清空配置缓存
        configService.ClearCache();

        logger.LogInformation("删除系统设置：{Key}", key);
        await dynamicOptionsManager.InitializeAsync();

        return true;
    }

    /// <summary>
    /// 重置设置为默认值
    /// </summary>
    [HttpPost("/{key}/reset")]
    public async Task<bool> ResetSettingAsync(string key)
    {
        var setting = await context.SystemSettings
            .FirstOrDefaultAsync(x => x.Key == key);

        if (setting == null)
        {
            return false;
        }

        setting.Value = setting.DefaultValue;
        setting.UpdatedAt = DateTime.UtcNow;

        await context.SaveChangesAsync();

        // 清空配置缓存
        configService.ClearCache();

        logger.LogInformation("重置系统设置为默认值：{Key}", key);
        await dynamicOptionsManager.InitializeAsync();

        return true;
    }

    /// <summary>
    /// 清空配置缓存
    /// </summary>
    [HttpPost("/cache/clear")]
    public async Task ClearCache()
    {
        configService.ClearCache();
        logger.LogInformation("配置缓存已清空");

        await Task.CompletedTask;
    }

    /// <summary>
    /// 获取需要重启的设置项
    /// </summary>
    [HttpGet("/restart-required")]
    public async Task<List<string>> GetRestartRequiredSettingsAsync()
    {
        var settings = await context.SystemSettings
            .AsNoTracking()
            .Where(x => x.RequiresRestart && x.IsEnabled)
            .Select(x => x.Key)
            .ToListAsync();

        return settings;
    }

    /// <summary>
    /// 导出系统设置（不包含敏感信息）
    /// </summary>
    [HttpGet("/export")]
    public async Task<List<SystemSettingOutput>> ExportSettingsAsync()
    {
        var settings = await context.SystemSettings
            .AsNoTracking()
            .Where(x => x.IsEnabled && !x.IsSensitive)
            .OrderBy(x => x.Group)
            .ThenBy(x => x.Order)
            .ToListAsync();

        return settings.Select(MapToOutput).ToList();
    }

    /// <summary>
    /// 验证配置值的有效性
    /// </summary>
    [HttpPost("/validate")]
    public async Task<Dictionary<string, string>> ValidateSettingsAsync(BatchUpdateSystemSettingsInput input)
    {
        var errors = new Dictionary<string, string>();

        foreach (var item in input.Settings)
        {
            var setting = await context.SystemSettings
                .AsNoTracking()
                .FirstOrDefaultAsync(x => x.Key == item.Key);

            if (setting == null)
            {
                errors[item.Key] = "设置项不存在";
                continue;
            }

            // 根据设置类型验证值
            var validationError = ValidateSettingValue(setting, item.Value);
            if (!string.IsNullOrEmpty(validationError))
            {
                errors[item.Key] = validationError;
            }
        }

        return errors;
    }

    /// <summary>
    /// 测试AI API连接
    /// </summary>
    [HttpPost("/test/ai")]
    public async Task<TestResultResponse> TestAIConnectionAsync([FromBody] TestAIApiRequest request)
    {
        try
        {
            logger.LogInformation("开始测试AI API连接：Endpoint={Endpoint}, Model={Model}", 
                request.Endpoint, request.Model ?? "default");

            // 验证必填参数
            if (string.IsNullOrWhiteSpace(request.Endpoint))
            {
                return new TestResultResponse
                {
                    Success = false,
                    Message = "API端点不能为空"
                };
            }

            if (string.IsNullOrWhiteSpace(request.ApiKey))
            {
                return new TestResultResponse
                {
                    Success = false,
                    Message = "API密钥不能为空"
                };
            }

            // 使用提供的模型或当前配置的模型
            var model = string.IsNullOrWhiteSpace(request.Model) ? OpenAIOptions.ChatModel : request.Model;
            
            if (string.IsNullOrWhiteSpace(model))
            {
                return new TestResultResponse
                {
                    Success = false,
                    Message = "未指定模型名称"
                };
            }

            // 创建临时目录用于测试
            var tempPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempPath);

            try
            {
                // 使用KernelFactory创建测试Kernel
                var kernel = await KernelFactory.GetKernel(
                    chatEndpoint: request.Endpoint,
                    apiKey: request.ApiKey,
                    gitPath: tempPath,
                    model: model,
                    isCodeAnalysis: false, // 测试时不需要加载代码分析插件
                    files: null
                );

                // 发送测试消息
                var chatService = kernel.GetRequiredService<IChatCompletionService>();
                var chatHistory = new ChatHistory();
                chatHistory.AddUserMessage("Hello");

                var response = await chatService.GetChatMessageContentAsync(chatHistory);

                logger.LogInformation("AI API连接测试成功");

                return new TestResultResponse
                {
                    Success = true,
                    Message = "AI API连接测试成功，模型响应正常",
                    Details = new
                    {
                        Model = model,
                        Endpoint = request.Endpoint,
                        Response = response.Content
                    }
                };
            }
            finally
            {
                // 清理临时目录
                try
                {
                    if (Directory.Exists(tempPath))
                    {
                        Directory.Delete(tempPath, true);
                    }
                }
                catch (Exception ex)
                {
                    logger.LogWarning(ex, "清理临时目录失败：{TempPath}", tempPath);
                }
            }
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "AI API连接测试失败");

            var errorMessage = ex.InnerException?.Message ?? ex.Message;
            
            return new TestResultResponse
            {
                Success = false,
                Message = $"AI API连接测试失败：{errorMessage}",
                Details = new
                {
                    Error = errorMessage,
                    Type = ex.GetType().Name
                }
            };
        }
    }

    /// <summary>
    /// 验证设置值的有效性
    /// </summary>
    private string? ValidateSettingValue(SystemSetting setting, string? value)
    {
        if (string.IsNullOrEmpty(value))
        {
            return null; // 允许空值
        }

        try
        {
            switch (setting.ValueType.ToLower())
            {
                case "bool":
                    if (!bool.TryParse(value, out _))
                        return "必须是布尔值（true/false）";
                    break;

                case "int":
                    if (!int.TryParse(value, out _))
                        return "必须是整数";
                    break;

                case "array":
                case "json":
                    System.Text.Json.JsonSerializer.Deserialize<object>(value);
                    break;
            }

            return null;
        }
        catch
        {
            return $"值格式不正确，期望类型：{setting.ValueType}";
        }
    }

    /// <summary>
    /// 检查设置键是否敏感
    /// </summary>
    private bool IsKeySensitive(string key)
    {
        var sensitiveKeys = new[] { "secret", "password", "key", "token", "apikey" };
        return sensitiveKeys.Any(sk => key.ToLower().Contains(sk));
    }

    /// <summary>
    /// 将实体映射为输出DTO
    /// </summary>
    private static SystemSettingOutput MapToOutput(SystemSetting setting)
    {
        return new SystemSettingOutput
        {
            Id = setting.Id,
            Key = setting.Key,
            Value = setting.IsSensitive && !string.IsNullOrEmpty(setting.Value)
                ? "***"
                : setting.Value,
            Group = setting.Group,
            ValueType = setting.ValueType,
            Description = setting.Description,
            IsSensitive = setting.IsSensitive,
            RequiresRestart = setting.RequiresRestart,
            DefaultValue = setting.IsSensitive && !string.IsNullOrEmpty(setting.DefaultValue)
                ? "***"
                : setting.DefaultValue,
            Order = setting.Order,
            IsEnabled = setting.IsEnabled,
            CreatedAt = setting.CreatedAt,
            UpdatedAt = setting.UpdatedAt
        };
    }
}