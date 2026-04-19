using System.Text.Json;
using FastService;
using KoalaWiki.Domains;
using KoalaWiki.Dto;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Services;

[Tags("应用配置管理")]
[FastService.Route("/api/AppConfig")]
[Filter(typeof(ResultFilter))]
public class AppConfigService(IKoalaWikiContext koala, IUserContext userContext) : FastApi
{
    /// <summary>
    /// 创建应用配置
    /// </summary>
    [FastService.Route("/")]
    public async Task<AppConfigOutput> CreateAsync(AppConfigInput input)
    {
        // 检查 AppId 是否已存在
        var existingApp = await koala.AppConfigs
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.AppId == input.AppId);

        if (existingApp != null)
        {
            throw new Exception("应用ID已存在");
        }

        // 检查用户是否有权限访问该组织和仓库
        var warehouse = await koala.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(x =>
                x.OrganizationName.ToLower() == input.OrganizationName.ToLower() &&
                x.Name.ToLower() == input.RepositoryName.ToLower());

        if (warehouse == null)
        {
            throw new Exception("指定的组织或仓库不存在");
        }

        var appConfig = new AppConfig
        {
            Id = Guid.NewGuid().ToString(),
            AppId = input.AppId,
            Name = input.Name,
            OrganizationName = input.OrganizationName,
            RepositoryName = input.RepositoryName,
            AllowedDomainsJson = JsonSerializer.Serialize(input.AllowedDomains),
            EnableDomainValidation = input.EnableDomainValidation,
            Description = input.Description,
            Prompt = input.Prompt,
            Introduction = input.Introduction,
            Model = input.Model,
            RecommendedQuestions = input.RecommendedQuestions,
            Mcps = input.Mcps?.Select(m => new Domains.AppConfigMcp
            {
                Url = m.Url,
                Headers = m.Headers
            }).ToList() ?? new(),
            UserId = userContext.CurrentUserId ?? throw new Exception("用户未登录"),
            IsEnabled = true,
            CreatedAt = DateTime.UtcNow
        };

        await koala.AppConfigs.AddAsync(appConfig);
        await koala.SaveChangesAsync();

        return MapToOutput(appConfig);
    }

    /// <summary>
    /// 获取应用配置列表
    /// </summary>
    [FastService.Route("/")]
    public async Task<List<AppConfigOutput>> GetAsync()
    {
        var appConfigs = await koala.AppConfigs
            .AsNoTracking()
            .Where(x => x.UserId == userContext.CurrentUserId)
            .OrderByDescending(x => x.CreatedAt)
            .ToListAsync();

        return appConfigs.Select(MapToOutput).ToList();
    }

    /// <summary>
    /// 根据 AppId 获取应用配置
    /// </summary>
    [HttpGet("/{appId}")]
    public async Task<AppConfigOutput> GetByAppIdAsync(string appId)
    {
        var appConfig = await koala.AppConfigs
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.AppId == appId && x.UserId == userContext.CurrentUserId);

        if (appConfig == null)
        {
            throw new Exception("应用配置不存在");
        }

        return MapToOutput(appConfig);
    }

    /// <summary>
    /// 更新应用配置
    /// </summary>
    [HttpPut("/{appId}")]
    public async Task<AppConfigOutput> UpdateAsync(string appId, AppConfigInput input)
    {
        var appConfig = await koala.AppConfigs
            .FirstOrDefaultAsync(x => x.AppId == appId && x.UserId == userContext.CurrentUserId);

        if (appConfig == null)
        {
            throw new Exception("应用配置不存在");
        }

        // 检查新的组织和仓库是否存在（如果有变更）
        if (appConfig.OrganizationName != input.OrganizationName ||
            appConfig.RepositoryName != input.RepositoryName)
        {
            var warehouse = await koala.Warehouses
                .AsNoTracking()
                .FirstOrDefaultAsync(x =>
                    x.OrganizationName.ToLower() == input.OrganizationName.ToLower() &&
                    x.Name.ToLower() == input.RepositoryName.ToLower());

            if (warehouse == null)
            {
                throw new Exception("指定的组织或仓库不存在");
            }
        }

        appConfig.Name = input.Name;
        appConfig.OrganizationName = input.OrganizationName;
        appConfig.RepositoryName = input.RepositoryName;
        appConfig.AllowedDomainsJson = JsonSerializer.Serialize(input.AllowedDomains);
        appConfig.EnableDomainValidation = input.EnableDomainValidation;
        appConfig.Description = input.Description;
        appConfig.Prompt = input.Prompt;
        appConfig.Introduction = input.Introduction;
        appConfig.Model = input.Model;
        appConfig.RecommendedQuestions = input.RecommendedQuestions;
        appConfig.Mcps = input.Mcps?.Select(m => new Domains.AppConfigMcp
        {
            Url = m.Url,
            Headers = m.Headers
        }).ToList() ?? new();

        await koala.SaveChangesAsync();

        return MapToOutput(appConfig);
    }

    /// <summary>
    /// 删除应用配置
    /// </summary>
    [HttpDelete("/{appId}")]
    public async Task DeleteAsync(string appId)
    {
        var appConfig = await koala.AppConfigs
            .FirstOrDefaultAsync(x => x.AppId == appId && x.UserId == userContext.CurrentUserId);

        if (appConfig == null)
        {
            throw new Exception("应用配置不存在");
        }

        koala.AppConfigs.Remove(appConfig);
        await koala.SaveChangesAsync();
    }

    /// <summary>
    /// 启用/禁用应用
    /// </summary>
    [HttpPost("/{appId}/toggle")]
    public async Task<AppConfigOutput> ToggleEnabledAsync(string appId)
    {
        var appConfig = await koala.AppConfigs
            .FirstOrDefaultAsync(x => x.AppId == appId && x.UserId == userContext.CurrentUserId);

        if (appConfig == null)
        {
            throw new Exception("应用配置不存在");
        }

        await koala.AppConfigs.Where(x => x.AppId == appId && x.UserId == userContext.CurrentUserId)
            .ExecuteUpdateAsync(x => x.SetProperty(a => a.IsEnabled, a => !a.IsEnabled));

        return MapToOutput(appConfig);
    }

    /// <summary>
    /// 域名验证（公开接口，不需要登录）
    /// </summary>
    [HttpPost("/validatedomain")]
    [AllowAnonymous]
    public async Task<DomainValidationResponse> ValidateDomainAsync(DomainValidationRequest request)
    {
        var appConfig = await koala.AppConfigs
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.AppId == request.AppId && x.IsEnabled);

        if (appConfig == null)
        {
            return new DomainValidationResponse
            {
                IsValid = false,
                Reason = "应用配置不存在或已禁用"
            };
        }

        // 如果未启用域名验证，直接通过
        if (!appConfig.EnableDomainValidation)
        {
            // 更新最后使用时间
            await UpdateLastUsedTimeAsync(appConfig.Id);

            return new DomainValidationResponse
            {
                IsValid = true,
                AppConfig = MapToOutput(appConfig)
            };
        }

        // 解析允许的域名列表
        var allowedDomains = JsonSerializer.Deserialize<List<string>>(appConfig.AllowedDomainsJson) ??
                             new List<string>();

        if (allowedDomains.Count == 0)
        {
            return new DomainValidationResponse
            {
                IsValid = false,
                Reason = "未配置允许的域名"
            };
        }

        // 验证域名
        var isValidDomain = allowedDomains.Any(domain =>
            request.Domain.Equals(domain, StringComparison.OrdinalIgnoreCase) ||
            request.Domain.EndsWith("." + domain, StringComparison.OrdinalIgnoreCase));

        if (!isValidDomain)
        {
            return new DomainValidationResponse
            {
                IsValid = false,
                Reason = $"域名 {request.Domain} 未被授权"
            };
        }

        // 更新最后使用时间
        await UpdateLastUsedTimeAsync(appConfig.Id);

        return new DomainValidationResponse
        {
            IsValid = true,
            AppConfig = MapToOutput(appConfig)
        };
    }

    /// <summary>
    /// 获取应用配置（公开接口，用于第三方脚本）
    /// </summary>
    [HttpGet("/public/{appId}")]
    [AllowAnonymous]
    public async Task<AppConfigOutput?> GetPublicConfigAsync(string appId)
    {
        var appConfig = await koala.AppConfigs
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.AppId == appId && x.IsEnabled);

        if (appConfig == null)
        {
            return null;
        }

        // 更新最后使用时间
        await UpdateLastUsedTimeAsync(appConfig.Id);

        return MapToOutput(appConfig);
    }

    /// <summary>
    /// 更新最后使用时间
    /// </summary>
    private async Task UpdateLastUsedTimeAsync(string appConfigId)
    {
        await koala.AppConfigs
            .Where(x => x.Id == appConfigId)
            .ExecuteUpdateAsync(x => x.SetProperty(p => p.LastUsedAt, DateTime.UtcNow));
    }

    /// <summary>
    /// 将实体映射为输出 DTO
    /// </summary>
    private static AppConfigOutput MapToOutput(AppConfig appConfig)
    {
        var allowedDomains = JsonSerializer.Deserialize<List<string>>(appConfig.AllowedDomainsJson) ??
                             new List<string>();

        return new AppConfigOutput
        {
            AppId = appConfig.AppId,
            Name = appConfig.Name,
            OrganizationName = appConfig.OrganizationName,
            RepositoryName = appConfig.RepositoryName,
            AllowedDomains = allowedDomains,
            EnableDomainValidation = appConfig.EnableDomainValidation,
            Description = appConfig.Description,
            Prompt = appConfig.Prompt,
            Introduction = appConfig.Introduction,
            Model = appConfig.Model,
            RecommendedQuestions = appConfig.RecommendedQuestions,
            Mcps = appConfig.Mcps?.Select(m => new Dto.AppConfigMcpDto
            {
                Url = m.Url,
                Headers = m.Headers
            }).ToList() ?? new(),
            IsEnabled = appConfig.IsEnabled,
            CreatedAt = appConfig.CreatedAt,
            UpdatedAt = appConfig.CreatedAt // 这里可以根据需要添加 UpdatedAt 字段
        };
    }
}