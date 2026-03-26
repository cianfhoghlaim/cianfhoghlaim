using System.Text.Json;
using System.Web;
using FastService;
using KoalaWiki.Domains;
using KoalaWiki.Domains.DocumentFile;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Dto;
using KoalaWiki.KoalaWarehouse.DocumentPending;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Infrastructure;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Caching.Memory;

namespace KoalaWiki.Services;

/// <summary>
/// 仓库管理服务
/// </summary>
[Tags("仓库管理服务")]
[FastService.Route("/api/Repository")]
[Filter(typeof(ResultFilter))]
public class RepositoryService(
    IKoalaWikiContext dbContext,
    IServiceProvider serviceProvider,
    IMemoryCache memoryCache,
    ILogger<RepositoryService> logger,
    IUserContext userContext,
    IHttpContextAccessor httpContextAccessor,
    IWarehouseSyncService warehouseSyncService) : FastApi
{
    /// <summary>
    /// 检查用户对指定仓库的访问权限
    /// </summary>
    /// <param name="warehouseId">仓库ID</param>
    /// <returns>是否有访问权限</returns>
    private async Task<bool> CheckWarehouseAccessAsync(string warehouseId)
    {
        var currentUserId = userContext.CurrentUserId;
        var isAdmin = httpContextAccessor.HttpContext?.User?.IsInRole("admin") ?? false;

        // 管理员有所有权限
        if (isAdmin) return true;

        // 检查仓库是否存在WarehouseInRole分配
        var hasPermissionAssignment = await dbContext.WarehouseInRoles
            .AnyAsync(wr => wr.WarehouseId == warehouseId);

        // 如果仓库没有权限分配，则是公共仓库，所有人都可以访问
        if (!hasPermissionAssignment) return true;

        // 如果用户未登录，无法访问有权限分配的仓库
        if (string.IsNullOrEmpty(currentUserId)) return false;

        // 获取用户的角色ID列表
        var userRoleIds = await dbContext.UserInRoles
            .Where(ur => ur.UserId == currentUserId)
            .Select(ur => ur.RoleId)
            .ToListAsync();

        // 如果用户没有任何角色，无法访问有权限分配的仓库
        if (!userRoleIds.Any()) return false;

        // 检查用户角色是否有该仓库的权限
        return await dbContext.WarehouseInRoles
            .AnyAsync(wr => userRoleIds.Contains(wr.RoleId) && wr.WarehouseId == warehouseId);
    }

    /// <summary>
    /// 检查用户对指定仓库的管理权限
    /// </summary>
    /// <param name="warehouseId">仓库ID</param>
    /// <returns>是否有管理权限</returns>
    private async Task<bool> CheckWarehouseManageAccessAsync(string warehouseId)
    {
        var currentUserId = userContext.CurrentUserId;
        var isAdmin = httpContextAccessor.HttpContext?.User?.IsInRole("admin") ?? false;

        // 管理员有所有权限
        if (isAdmin) return true;

        // 如果用户未登录，无管理权限
        if (string.IsNullOrEmpty(currentUserId)) return false;

        // 检查仓库是否存在权限分配
        var hasPermissionAssignment = await dbContext.WarehouseInRoles
            .AnyAsync(wr => wr.WarehouseId == warehouseId);

        // 如果仓库没有权限分配，只有管理员可以管理
        if (!hasPermissionAssignment) return false;

        // 获取用户的角色ID列表
        var userRoleIds = await dbContext.UserInRoles
            .Where(ur => ur.UserId == currentUserId)
            .Select(ur => ur.RoleId)
            .ToListAsync();

        // 如果用户没有任何角色，无管理权限
        if (!userRoleIds.Any()) return false;

        // 检查用户角色是否有该仓库的写入或删除权限（管理权限）
        return await dbContext.WarehouseInRoles
            .AnyAsync(wr => userRoleIds.Contains(wr.RoleId) &&
                            wr.WarehouseId == warehouseId &&
                            (wr.IsWrite || wr.IsDelete));
    }

    /// <summary>
    /// 获取仓库列表
    /// </summary>
    /// <param name="page">页码</param>
    /// <param name="pageSize">每页数量</param>
    /// <param name="keyword">搜索关键词</param>
    /// <returns>仓库列表</returns>
    [HttpGet("RepositoryList")]
    public async Task<PageDto<RepositoryInfoDto>> GetRepositoryListAsync(int page, int pageSize, string? keyword)
    {
        var query = dbContext.Warehouses.AsNoTracking();

        // 如果有关键词，则按名称或地址搜索
        if (!string.IsNullOrWhiteSpace(keyword))
        {
            query = query.Where(r => r.Name.Contains(keyword) ||
                                     r.Address.Contains(keyword) ||
                                     r.OrganizationName.Contains(keyword));
        }

        // 权限过滤：如果仓库存在WarehouseInRole分配，则只有拥有相应角色的用户才能访问
        var currentUserId = userContext.CurrentUserId;
        var isAdmin = httpContextAccessor.HttpContext?.User?.IsInRole("admin") ?? false;

        if (!isAdmin && !string.IsNullOrEmpty(currentUserId))
        {
            // 获取用户的角色ID列表
            var userRoleIds = await dbContext.UserInRoles
                .Where(ur => ur.UserId == currentUserId)
                .Select(ur => ur.RoleId)
                .ToListAsync();

            // 如果用户没有任何角色，只能看到公共仓库（没有权限分配的仓库）
            if (!userRoleIds.Any())
            {
                var publicWarehouseIds = await dbContext.Warehouses
                    .Where(w => !dbContext.WarehouseInRoles.Any(wr => wr.WarehouseId == w.Id))
                    .Select(w => w.Id)
                    .ToListAsync();

                query = query.Where(x => publicWarehouseIds.Contains(x.Id));
            }
            else
            {
                // 用户可以访问的仓库：
                // 1. 通过角色权限可以访问的仓库
                // 2. 没有任何权限分配的公共仓库
                var accessibleWarehouseIds = await dbContext.WarehouseInRoles
                    .Where(wr => userRoleIds.Contains(wr.RoleId))
                    .Select(wr => wr.WarehouseId)
                    .Distinct()
                    .ToListAsync();

                var publicWarehouseIds = await dbContext.Warehouses
                    .Where(w => !dbContext.WarehouseInRoles.Any(wr => wr.WarehouseId == w.Id))
                    .Select(w => w.Id)
                    .ToListAsync();

                var allAccessibleIds = accessibleWarehouseIds.Concat(publicWarehouseIds).Distinct().ToList();
                query = query.Where(x => allAccessibleIds.Contains(x.Id));
            }
        }
        else if (string.IsNullOrEmpty(currentUserId))
        {
            // 未登录用户只能看到公共仓库
            var publicWarehouseIds = await dbContext.Warehouses
                .Where(w => !dbContext.WarehouseInRoles.Any(wr => wr.WarehouseId == w.Id))
                .Select(w => w.Id)
                .ToListAsync();

            query = query.Where(x => publicWarehouseIds.Contains(x.Id));
        }
        // 管理员可以看到所有仓库，不需要额外过滤

        // 排序：先按推荐状态，再按完成状态，最后按创建时间
        query = query
            .OrderByDescending(x => x.IsRecommended)
            .ThenByDescending(x => x.Status == WarehouseStatus.Completed)
            .ThenByDescending(x => x.CreatedAt);

        // 按仓库名称和组织名称分组，保持排序一致性
        var groupedQuery = query
            .GroupBy(x => new { x.Name, x.OrganizationName })
            .Select(g => g.OrderByDescending(x => x.IsRecommended)
                .ThenByDescending(x => x.Status == WarehouseStatus.Completed)
                .ThenByDescending(x => x.CreatedAt)
                .FirstOrDefault());

        // 计算总数
        var total = await groupedQuery.CountAsync();

        // 获取分页数据
        var repositories = await groupedQuery
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        // 将实体映射为DTO
        var repositoryDtos = repositories.Select(r => r.Adapt<RepositoryInfoDto>()).ToList();

        return new PageDto<RepositoryInfoDto>(total, repositoryDtos);
    }

    /// <summary>
    /// 获取仓库详情
    /// </summary>
    /// <param name="id">仓库ID</param>
    /// <returns>仓库详情</returns>
    [HttpGet("/Repository")]
    public async Task<ResultDto<RepositoryInfoDto>> GetRepositoryAsync(string id)
    {
        var repository = await dbContext.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(r => r.Id == id);

        if (repository == null)
        {
            return ResultDto<RepositoryInfoDto>.Error("仓库不存在");
        }

        // 检查用户权限
        if (!await CheckWarehouseAccessAsync(id))
        {
            return ResultDto<RepositoryInfoDto>.Error("您没有权限访问此仓库");
        }

        // 将实体映射为DTO
        var repositoryDto = repository.Adapt<RepositoryInfoDto>();
        return ResultDto<RepositoryInfoDto>.Success(repositoryDto);
    }

    /// <summary>
    /// 根据组织名称和仓库名称获取仓库详情
    /// </summary>
    /// <param name="owner">组织名称</param>
    /// <param name="name">仓库名称</param>
    /// <param name="branch">分支名称（可选）</param>
    /// <returns>仓库详情</returns>
    [HttpGet("RepositoryByOwnerAndName")]
    public async Task<RepositoryInfoDto> GetRepositoryByOwnerAndNameAsync(string owner, string name,
        string? branch = null)
    {
        var query = dbContext.Warehouses
            .AsNoTracking()
            .Where(r => r.OrganizationName == owner && r.Name == name &&
                        (r.Status == WarehouseStatus.Completed || r.Status == WarehouseStatus.Processing));

        // 如果指定了分支，则按分支筛选
        if (!string.IsNullOrEmpty(branch))
        {
            query = query.Where(r => r.Branch == branch);
        }

        var repository = await query.FirstOrDefaultAsync();

        if (repository == null)
        {
            throw new Exception($"仓库不存在: {owner}/{name}{(branch != null ? $"/{branch}" : "")}");
        }

        // 检查用户权限
        if (!await CheckWarehouseAccessAsync(repository.Id))
        {
            throw new UnauthorizedAccessException("您没有权限访问此仓库");
        }

        // 将实体映射为DTO
        var repositoryDto = repository.Adapt<RepositoryInfoDto>();

        return repositoryDto;
    }

    /// <summary>
    /// 创建Git仓库
    /// </summary>
    /// <param name="createDto">仓库信息</param>
    /// <returns>创建结果</returns>
    [HttpPost("GitRepository")]
    public async Task<RepositoryInfoDto> CreateGitRepositoryAsync(CreateGitRepositoryDto createDto)
    {
        // 只有管理员可以创建新仓库
        var isAdmin = httpContextAccessor.HttpContext?.User?.IsInRole("admin") ?? false;
        if (!isAdmin)
        {
            throw new UnauthorizedAccessException("只有管理员可以创建新仓库");
        }

        // 处理Git地址
        if (!createDto.Address.EndsWith(".git"))
        {
            createDto.Address += ".git";
        }

        // 解析仓库路径和组织名称
        var (_, organization) = GitService.GetRepositoryPath(createDto.Address);
        var names = createDto.Address.Split('/');
        var repositoryName = names[^1].Replace(".git", "");

        // URL decode parameters
        var decodedOrganization = HttpUtility.UrlDecode(organization);
        var decodedRepositoryName = HttpUtility.UrlDecode(repositoryName);

        // 检查仓库是否已存在
        var existingRepo = await dbContext.Warehouses.FirstOrDefaultAsync(x =>
            x.OrganizationName == decodedOrganization &&
            x.Name == decodedRepositoryName &&
            x.Branch == createDto.Branch);

        // 判断这个仓库是否已经添加
        if (existingRepo?.Status is WarehouseStatus.Completed)
        {
            throw new Exception("该仓库已存在且处于完成状态，不可重复创建");
        }
        else if (existingRepo?.Status is WarehouseStatus.Pending)
        {
            throw new Exception("该仓库已存在且处于待处理状态，请等待处理完成");
        }
        else if (existingRepo?.Status is WarehouseStatus.Processing)
        {
            throw new Exception("该仓库已存在且正在处理中，请稍后再试");
        }
        else if (!string.IsNullOrEmpty(createDto.Branch))
        {
            var branch = await dbContext.Warehouses
                .AsNoTracking()
                .Where(x => x.Branch == createDto.Branch &&
                            x.OrganizationName == decodedOrganization &&
                            x.Name == decodedRepositoryName)
                .FirstOrDefaultAsync();

            if (branch != null)
            {
                throw new Exception("该分支已经存在");
            }
        }

        // 删除旧的仓库（如果存在）
        await dbContext.Warehouses
            .Where(x => x.OrganizationName == decodedOrganization &&
                        x.Name == decodedRepositoryName &&
                        x.Branch == createDto.Branch)
            .ExecuteDeleteAsync();

        // 创建新仓库
        var entity = new Warehouse
        {
            Id = Guid.NewGuid().ToString(),
            OrganizationName = decodedOrganization,
            Name = decodedRepositoryName,
            Address = createDto.Address,
            Description = string.Empty,
            Version = string.Empty,
            Error = string.Empty,
            Branch = createDto.Branch,
            Type = "git",
            GitUserName = createDto.GitUserName,
            GitPassword = createDto.GitPassword,
            Email = createDto.Email,
            CreatedAt = DateTime.UtcNow,
            Status = WarehouseStatus.Pending
        };

        // 保存仓库
        await dbContext.Warehouses.AddAsync(entity);
        await dbContext.SaveChangesAsync();

        // 将实体映射为DTO
        var repositoryDto = entity.Adapt<RepositoryInfoDto>();

        return repositoryDto;
    }

    /// <summary>
    /// 更新仓库
    /// </summary>
    /// <param name="id">仓库ID</param>
    /// <param name="updateDto">更新信息</param>
    /// <returns>更新结果</returns>
    [HttpPost("Repository")]
    public async Task<RepositoryInfoDto> UpdateRepositoryAsync(string id, UpdateRepositoryDto updateDto)
    {
        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(id))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        var repository = await dbContext.Warehouses.FindAsync(id);
        if (repository == null)
        {
            throw new Exception("仓库不存在");
        }

        // 更新仓库信息
        if (updateDto.Description != null)
        {
            repository.Description = updateDto.Description;
        }

        if (updateDto.IsRecommended.HasValue)
        {
            repository.IsRecommended = updateDto.IsRecommended.Value;
        }

        // 保存更改
        dbContext.Warehouses.Update(repository);
        await dbContext.SaveChangesAsync();

        // 将实体映射为DTO
        var repositoryDto = repository.Adapt<RepositoryInfoDto>();

        return repositoryDto;
    }

    /// <summary>
    /// 删除仓库
    /// </summary>
    /// <param name="id">仓库ID</param>
    /// <returns>删除结果</returns>
    [HttpDelete("Repository")]
    [EndpointSummary("仓库管理：删除仓库")]
    public async Task<bool> DeleteRepositoryAsync(string id)
    {
        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(id))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        await dbContext.Warehouses
            .Where(x => x.Id.ToLower() == id.ToLower())
            .ExecuteDeleteAsync();

        var document = await dbContext.Documents
            .AsNoTracking()
            .Where(x => x.WarehouseId.ToLower() == id.ToLower())
            .FirstOrDefaultAsync();

        try
        {
            if (document != null)
                Directory.Delete(document.GitPath, true);
        }
        catch (Exception e)
        {
            logger.LogError(e, "删除仓库失败");
        }

        await dbContext.Documents
            .Where(x => x.WarehouseId.ToLower() == id.ToLower())
            .ExecuteDeleteAsync();

        await dbContext.DocumentCatalogs
            .Where(x => x.WarehouseId.ToLower() == id.ToLower())
            .ExecuteDeleteAsync();


        return true;
    }

    /// <summary>
    /// 重新处理仓库
    /// </summary>
    /// <param name="id">仓库ID</param>
    /// <returns>处理结果</returns>
    [HttpPost("ResetRepository")]
    [EndpointSummary("仓库管理：重新处理仓库")]
    public async Task<bool> ResetRepositoryAsync(string id)
    {
        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(id))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        // 更新仓库状态为待处理
        await dbContext.Warehouses
            .Where(x => x.Id == id)
            .ExecuteUpdateAsync(x => x.SetProperty(y => y.Status, WarehouseStatus.Pending));

        var warehouse = await dbContext.Warehouses
            .AsNoTracking()
            .Where(x => x.Id == id)
            .FirstOrDefaultAsync();

        if (warehouse == null)
        {
            return false;
        }

        return true;
    }

    /// <summary>
    /// 获取仓库文件目录结构
    /// </summary>
    /// <param name="id">仓库ID</param>
    /// <returns>文件目录结构</returns>
    [HttpGet("Files")]
    [EndpointSummary("仓库管理：获取仓库文件目录结构")]
    public async Task<List<TreeNode>> GetFilesAsync(string id)
    {
        // 检查用户权限
        if (!await CheckWarehouseAccessAsync(id))
        {
            throw new UnauthorizedAccessException("您没有权限访问此仓库");
        }

        var catalogs = await dbContext.DocumentCatalogs
            .AsNoTracking()
            .Where(x => x.WarehouseId == id && x.IsDeleted == false)
            .ToListAsync();

        var result = BuildDocumentCatalogTree(catalogs);

        return result;
    }

    /// <summary>
    /// 重命名目录
    /// </summary>
    [HttpPost("RenameCatalog")]
    [EndpointSummary("仓库管理：重命名目录")]
    public async Task<bool> RenameCatalogAsync(string id, string newName)
    {
        var catalog = await dbContext.DocumentCatalogs.FirstOrDefaultAsync(x => x.Id == id);
        if (catalog == null)
        {
            throw new ArgumentException("目录不存在");
        }

        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(catalog.WarehouseId))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        await dbContext.DocumentCatalogs
            .Where(x => x.Id == id)
            .ExecuteUpdateAsync(x => x.SetProperty(y => y.Name, newName));

        return true;
    }

    [EndpointSummary("仓库管理：删除目录")]
    [HttpDelete("{id}")]
    public async Task<bool> DeleteCatalogAsync(string id)
    {
        var catalog = await dbContext.DocumentCatalogs.FirstOrDefaultAsync(x => x.Id == id);
        if (catalog == null)
        {
            throw new ArgumentException("目录不存在");
        }

        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(catalog.WarehouseId))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        // 逻辑删除目录
        await dbContext.DocumentCatalogs
            .Where(x => x.Id == id)
            .ExecuteDeleteAsync();

        var fileItem = await dbContext.DocumentFileItems
            .AsNoTracking()
            .Where(x => x.DocumentCatalogId == id)
            .Select(x => x.Id)
            .ToListAsync();

        // 删除目录下的文件
        await dbContext.DocumentFileItems
            .Where(x => x.DocumentCatalogId == id)
            .ExecuteDeleteAsync();

        // 删除目录下的文件源
        await dbContext.DocumentFileItemSources
            .Where(x => fileItem.Contains(x.DocumentFileItemId))
            .ExecuteDeleteAsync();

        return true;
    }

    [HttpPost("CreateCatalog")]
    [EndpointSummary("仓库管理：新建目录，并且实时生成文档")]
    public async Task<bool> CreateCatalogAsync(CreateCatalogInput input)
    {
        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(input.WarehouseId))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        // 先判断是否存在仓库
        if (await dbContext.Warehouses
                .AsNoTracking()
                .AnyAsync(x => x.Id == input.WarehouseId) == false)
        {
            throw new Exception("仓库不存在");
        }

        // 判断是否存在同名目录或同路由
        if (await dbContext.DocumentCatalogs
                .AsNoTracking()
                .AnyAsync(x => x.Name == input.Name && x.WarehouseId == input.WarehouseId))
        {
            throw new Exception("目录名称已存在");
        }

        if (await dbContext.DocumentCatalogs
                .AsNoTracking()
                .AnyAsync(x => x.Url == input.Url && x.WarehouseId == input.WarehouseId))
        {
            throw new Exception("目录路由已存在");
        }

        if (string.IsNullOrEmpty(input.Name))
        {
            throw new Exception("目录名称不能为空");
        }

        if (string.IsNullOrEmpty(input.Url))
        {
            throw new Exception("目录路由不能为空");
        }

        if (string.IsNullOrEmpty(input.WarehouseId))
        {
            throw new Exception("仓库ID不能为空");
        }

        if (string.IsNullOrEmpty(input.Prompt))
        {
            throw new Exception("目录提示不能为空");
        }

        var catalog = new DocumentCatalog
        {
            Id = Guid.NewGuid().ToString(),
            Name = input.Name,
            Url = input.Url,
            Prompt = input.Prompt,
            ParentId = input.ParentId,
            Order = input.Order,
            WarehouseId = input.WarehouseId,
            IsDeleted = false,
            CreatedAt = DateTime.UtcNow
        };

        await dbContext.DocumentCatalogs.AddAsync(catalog);
        await dbContext.SaveChangesAsync();

        var warehouse = await dbContext.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == input.WarehouseId);
        var document = await dbContext.Documents
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.WarehouseId == input.WarehouseId);

        var fileKernel = await KernelFactory.GetKernel(OpenAIOptions.Endpoint,
            OpenAIOptions.ChatApiKey, document.GitPath, OpenAIOptions.ChatModel, false);
        // 对当前单目录进行分析
        var (catalogs, fileItem, files)
            = await DocumentPendingService.ProcessDocumentAsync(catalog, fileKernel,
                document.GetCatalogueSmartFilterOptimized(),
                warehouse.Address, warehouse.Branch, document.GitPath, null, warehouse.Classify);

        // 处理完成后，更新目录状态

        // 更新文档状态
        await dbContext.DocumentCatalogs.Where(x => x.Id == catalog.Id)
            .ExecuteUpdateAsync(x => x.SetProperty(y => y.IsCompleted, true));

        // 修复Mermaid语法错误
        DocumentPendingService.RepairMermaid(fileItem);

        await dbContext.DocumentFileItems.AddAsync(fileItem);
        await dbContext.DocumentFileItemSources.AddRangeAsync(files.Select(x => new DocumentFileItemSource()
        {
            Address = x,
            DocumentFileItemId = fileItem.Id,
            Name = x,
            Id = Guid.NewGuid().ToString("N"),
        }));

        await dbContext.SaveChangesAsync();

        return true;
    }

    /// <summary>
    /// AI智能生成文件内容
    /// </summary>
    /// <returns></returns>
    [HttpPost("GenerateFileContent")]
    public async Task<bool> GenerateFileContentAsync(GenerateFileContentInput input)
    {
        // 使用memoryCache增加缓存，避免重复处理同一目录
        if (memoryCache.TryGetValue(input.Id, out bool isProcessing) && isProcessing)
        {
            throw new Exception("该目录正在处理中，请稍后再试");
        }

        memoryCache.Set(input.Id, true, TimeSpan.FromMinutes(5));

        var scope = serviceProvider.CreateScope();

        Task.Run(async () =>
        {
            try
            {
                var dbContext = scope.ServiceProvider.GetRequiredService<IKoalaWikiContext>();

                var catalog = await dbContext.DocumentCatalogs
                    .AsNoTracking()
                    .FirstOrDefaultAsync(x => x.Id == input.Id);

                if (catalog == null)
                {
                    throw new ArgumentException("目录不存在");
                }

                // 检查管理权限
                if (!await CheckWarehouseManageAccessAsync(catalog.WarehouseId))
                {
                    throw new UnauthorizedAccessException("您没有权限管理此仓库");
                }

                if (!string.IsNullOrEmpty(input.Prompt))
                {
                    await dbContext.DocumentCatalogs
                        .Where(x => x.Id == input.Id)
                        .ExecuteUpdateAsync(x => x.SetProperty(y => y.Prompt, input.Prompt));
                }

                var warehouse = await dbContext.Warehouses
                    .AsNoTracking()
                    .FirstOrDefaultAsync(x => x.Id == catalog.WarehouseId);

                Log.Logger.Information("开始处理目录：{CatalogName}",
                    JsonSerializer.Serialize(catalog, JsonSerializerOptions.Web));
                Log.Logger.Information("仓库信息：{WarehouseInfo}",
                    JsonSerializer.Serialize(warehouse, JsonSerializerOptions.Web));

                var document = await dbContext.Documents
                    .AsNoTracking()
                    .FirstOrDefaultAsync(x => x.WarehouseId == catalog.WarehouseId);

                if (document == null)
                {
                    throw new Exception("文档不存在");
                }

                var fileKernel = await KernelFactory.GetKernel(OpenAIOptions.Endpoint,
                    OpenAIOptions.ChatApiKey, document.GitPath, OpenAIOptions.ChatModel, false);

                // 对当前单目录进行分析
                var (catalogs, fileItem, files)
                    = await DocumentPendingService.ProcessDocumentAsync(catalog, fileKernel,
                        document.GetCatalogueSmartFilterOptimized(),
                        warehouse.Address, warehouse.Branch, document.GitPath, null, warehouse.Classify);

                // 处理完成后，更新目录状态

                // 更新文档状态
                await dbContext.DocumentCatalogs.Where(x => x.Id == catalog.Id)
                    .ExecuteUpdateAsync(x => x.SetProperty(y => y.IsCompleted, true));

                // 修复Mermaid语法错误
                DocumentPendingService.RepairMermaid(fileItem);

                await dbContext.DocumentFileItems.Where(x => x.Id == fileItem.Id)
                    .ExecuteDeleteAsync();

                await dbContext.DocumentFileItems.AddAsync(fileItem);
                await dbContext.DocumentFileItemSources.AddRangeAsync(files.Select(x => new DocumentFileItemSource()
                {
                    Address = x,
                    DocumentFileItemId = fileItem.Id,
                    Name = x,
                    Id = Guid.NewGuid().ToString("N"),
                }));

                await dbContext.SaveChangesAsync();
            }
            finally
            {
                memoryCache.Remove(input.Id);
                scope.Dispose();
            }
        });

        await Task.Delay(5000);

        return true;
    }

    /// <summary>
    /// 获取文件内容
    /// </summary>
    /// <param name="id"></param>
    /// <returns></returns>
    /// <exception cref="Exception"></exception>
    [HttpGet("FileContent")]
    [EndpointSummary("仓库管理：获取文件内容")]
    public async Task<string> GetFileContentAsync(string id)
    {
        var catalog = await dbContext.DocumentCatalogs.FirstOrDefaultAsync(x => x.Id == id);

        if (catalog == null)
        {
            throw new ArgumentException("目录不存在");
        }

        // 检查用户权限
        if (!await CheckWarehouseAccessAsync(catalog.WarehouseId))
        {
            throw new UnauthorizedAccessException("您没有权限访问此仓库");
        }

        var fileItem = await dbContext.DocumentFileItems.FirstOrDefaultAsync(x => x.DocumentCatalogId == id);

        if (fileItem == null)
        {
            return "";
        }

        return fileItem.Content;
    }

    /// <summary>
    /// 仓库管理：保存文件内容
    /// </summary>
    [HttpPost("FileContent")]
    [EndpointSummary("仓库管理：保存文件内容")]
    public async Task<bool> FileContentAsync(SaveFileContentInput input)
    {
        var catalog = await dbContext.DocumentCatalogs.FirstOrDefaultAsync(x => x.Id == input.Id);

        if (catalog == null)
        {
            throw new ArgumentException("目录不存在");
        }

        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(catalog.WarehouseId))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        var fileItem = await dbContext.DocumentFileItems.FirstOrDefaultAsync(x => x.DocumentCatalogId == input.Id);

        if (fileItem == null)
        {
            fileItem = new DocumentFileItem()
            {
                Id = Guid.NewGuid().ToString(),
                DocumentCatalogId = input.Id,
                Content = input.Content,
                CreatedAt = DateTime.UtcNow
            };

            await dbContext.DocumentFileItems.AddAsync(fileItem);
        }
        else
        {
            fileItem.Content = input.Content;

            dbContext.DocumentFileItems.Update(fileItem);
        }

        await dbContext.SaveChangesAsync();

        return true;
    }

    /// <summary>
    /// 更新仓库基本信息
    /// </summary>
    /// <param name="id">仓库ID</param>
    /// <param name="input">更新仓库输入</param>
    /// <returns></returns>
    [HttpPut("UpdateWarehouse")]
    [EndpointSummary("仓库管理：更新仓库信息")]
    public async Task<bool> UpdateWarehouseAsync(string id, UpdateWarehouseInput input)
    {
        // 检查仓库是否存在
        var warehouse = await dbContext.Warehouses
            .FirstOrDefaultAsync(x => x.Id == id);

        if (warehouse == null)
        {
            throw new ArgumentException("仓库不存在");
        }

        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(id))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        // 更新仓库信息
        if (!string.IsNullOrEmpty(input.Name))
            warehouse.Name = input.Name;
        if (!string.IsNullOrEmpty(input.Description))
            warehouse.Description = input.Description;

        dbContext.Warehouses.Update(warehouse);
        await dbContext.SaveChangesAsync();

        logger.LogInformation("仓库 {WarehouseId} 的信息已更新", id);

        return true;
    }

    /// <summary>
    /// 更新仓库同步设置
    /// </summary>
    /// <param name="id">仓库ID</param>
    /// <param name="input">更新同步设置输入</param>
    /// <returns></returns>
    [HttpPost("UpdateSync")]
    [EndpointSummary("仓库管理：更新同步设置")]
    public async Task<bool> UpdateWarehouseSyncAsync(string id, UpdateWarehouseSyncInput input)
    {
        // 检查仓库是否存在
        var warehouse = await dbContext.Warehouses
            .FirstOrDefaultAsync(x => x.Id == id);

        if (warehouse == null)
        {
            throw new ArgumentException("仓库不存在");
        }

        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(id))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        // 更新同步设置
        warehouse.EnableSync = input.EnableSync;
        dbContext.Warehouses.Update(warehouse);
        await dbContext.SaveChangesAsync();

        logger.LogInformation("仓库 {WarehouseId} 的同步设置已更新为 {EnableSync}", id, input.EnableSync);

        return true;
    }

    /// <summary>
    /// 手动触发仓库同步
    /// </summary>
    /// <param name="id">仓库ID</param>
    /// <returns></returns>
    [HttpPost("ManualSync")]
    [EndpointSummary("仓库管理：手动触发同步")]
    public async Task<bool> TriggerManualSyncAsync(string id)
    {
        // 检查仓库是否存在
        var warehouse = await dbContext.Warehouses
            .FirstOrDefaultAsync(x => x.Id == id);

        if (warehouse == null)
        {
            throw new ArgumentException("仓库不存在");
        }

        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(id))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        // 调用同步服务执行同步
        var result = await warehouseSyncService.SyncWarehouseAsync(id, WarehouseSyncTrigger.Manual);

        if (!result)
        {
            throw new Exception("触发同步失败，请检查仓库配置");
        }

        logger.LogInformation("成功触发仓库 {WarehouseId} 的手动同步", id);

        return true;
    }

    /// <summary>
    /// 获取仓库同步记录
    /// </summary>
    /// <param name="warehouseId">仓库ID</param>
    /// <param name="page">页码</param>
    /// <param name="pageSize">每页大小</param>
    /// <returns></returns>
    [HttpGet("SyncRecords")]
    [EndpointSummary("仓库管理：获取同步记录")]
    public async Task<PageDto<WarehouseSyncRecordDto>> GetWarehouseSyncRecordsAsync(string warehouseId, int page = 1,
        int pageSize = 10)
    {
        // 检查访问权限
        if (!await CheckWarehouseAccessAsync(warehouseId))
        {
            throw new UnauthorizedAccessException("您没有权限访问此仓库");
        }

        // 从数据库查询同步记录
        var query = dbContext.WarehouseSyncRecords
            .Where(x => x.WarehouseId == warehouseId)
            .OrderByDescending(x => x.StartTime);

        var totalCount = await query.CountAsync();
        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(x => new WarehouseSyncRecordDto
            {
                Id = x.Id,
                WarehouseId = x.WarehouseId,
                Status = x.Status.ToString(),
                StartTime = x.StartTime,
                EndTime = x.EndTime,
                FromVersion = x.FromVersion,
                ToVersion = x.ToVersion,
                ErrorMessage = x.ErrorMessage,
                FileCount = x.FileCount,
                UpdatedFileCount = x.UpdatedFileCount,
                AddedFileCount = x.AddedFileCount,
                DeletedFileCount = x.DeletedFileCount,
                Trigger = x.Trigger.ToString(),
                CreatedAt = x.CreatedAt
            })
            .ToListAsync();

        return new PageDto<WarehouseSyncRecordDto>(totalCount, items);
    }

    /// <summary>
    /// 获取仓库统计信息
    /// </summary>
    [HttpGet("RepositoryStats")]
    [EndpointSummary("仓库管理：获取仓库统计信息")]
    public async Task<RepositoryStatsDto> GetRepositoryStatsAsync(string id)
    {
        // 检查用户权限
        if (!await CheckWarehouseAccessAsync(id))
        {
            throw new UnauthorizedAccessException("您没有权限访问此仓库");
        }

        var repository = await dbContext.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == id);

        if (repository == null)
        {
            throw new ArgumentException("仓库不存在");
        }

        // 获取文档统计
        var documentCount = await dbContext.DocumentCatalogs
            .Where(x => x.WarehouseId == id && !x.IsDeleted)
            .CountAsync();

        var completedDocumentCount = await dbContext.DocumentCatalogs
            .Where(x => x.WarehouseId == id && !x.IsDeleted && x.IsCompleted)
            .CountAsync();

        var fileCount = await dbContext.DocumentFileItems
            .Where(x => dbContext.DocumentCatalogs
                .Where(c => c.WarehouseId == id && !c.IsDeleted)
                .Select(c => c.Id)
                .Contains(x.DocumentCatalogId))
            .CountAsync();

        return new RepositoryStatsDto
        {
            TotalDocuments = documentCount,
            CompletedDocuments = completedDocumentCount,
            PendingDocuments = documentCount - completedDocumentCount,
            TotalFiles = fileCount,
            LastSyncTime = repository.CreatedAt,
            ProcessingStatus = repository.Status.ToString()
        };
    }

    /// <summary>
    /// 获取仓库操作日志
    /// </summary>
    [HttpGet("RepositoryLogs")]
    [EndpointSummary("仓库管理：获取仓库操作日志")]
    public async Task<PageDto<RepositoryLogDto>> GetRepositoryLogsAsync(string repositoryId, int page = 1,
        int pageSize = 20)
    {
        // 检查用户权限
        if (!await CheckWarehouseAccessAsync(repositoryId))
        {
            throw new UnauthorizedAccessException("您没有权限访问此仓库");
        }

        // 这里暂时返回空数据，实际应该从日志表查询
        var logs = new List<RepositoryLogDto>();

        return new PageDto<RepositoryLogDto>(0, logs);
    }

    /// <summary>
    /// 批量操作仓库
    /// </summary>
    [HttpPost("BatchOperate")]
    [EndpointSummary("仓库管理：批量操作仓库")]
    public async Task<bool> BatchOperateRepositoriesAsync(BatchOperationDto data)
    {
        var isAdmin = httpContextAccessor.HttpContext?.User?.IsInRole("admin") ?? false;
        if (!isAdmin)
        {
            throw new UnauthorizedAccessException("只有管理员可以执行批量操作");
        }

        foreach (var id in data.Ids)
        {
            switch (data.Operation.ToLower())
            {
                case "refresh":
                    await ResetRepositoryAsync(id);
                    break;
                case "delete":
                    await DeleteRepositoryAsync(id);
                    break;
                default:
                    throw new ArgumentException($"不支持的操作: {data.Operation}");
            }
        }

        return true;
    }

    /// <summary>
    /// 获取仓库文档目录
    /// </summary>
    [HttpGet("DocumentCatalogs")]
    [EndpointSummary("仓库管理：获取仓库文档目录")]
    public async Task<List<TreeNode>> GetDocumentCatalogsAsync(string repositoryId)
    {
        // 检查用户权限
        if (!await CheckWarehouseAccessAsync(repositoryId))
        {
            throw new UnauthorizedAccessException("您没有权限访问此仓库");
        }

        var catalogs = await dbContext.DocumentCatalogs
            .AsNoTracking()
            .Where(x => x.WarehouseId == repositoryId && !x.IsDeleted)
            .OrderBy(x => x.Order)
            .ToListAsync();

        // 构建树形结构
        var result = BuildDocumentCatalogTree(catalogs);

        return result;
    }

    /// <summary>
    /// 构建DocumentCatalog树形结构
    /// </summary>
    private List<TreeNode> BuildDocumentCatalogTree(List<DocumentCatalog> catalogs)
    {
        var result = new List<TreeNode>();

        // 获取顶级目录
        var topLevel = catalogs.Where(x => x.ParentId == null || string.IsNullOrEmpty(x.ParentId))
            .OrderBy(x => x.Order)
            .ToList();

        foreach (var item in topLevel)
        {
            var node = new TreeNode
            {
                title = item.Name,
                key = item.Url ?? item.Id, // 使用URL作为key，如果为空则使用ID
                isLeaf = catalogs.All(x => x.ParentId != item.Id), // 如果没有子节点，则为叶子节点
                children = new List<TreeNode>(),
                catalog = item,
            };

            // 递归添加子节点
            if (!node.isLeaf.Value)
            {
                node.children = GetDocumentCatalogChildren(item.Id, catalogs);
            }

            result.Add(node);
        }

        return result;
    }

    /// <summary>
    /// 递归获取DocumentCatalog子节点
    /// </summary>
    private List<TreeNode> GetDocumentCatalogChildren(string parentId, List<DocumentCatalog> catalogs)
    {
        var children = new List<TreeNode>();
        var directChildren = catalogs
            .Where(x => x.ParentId == parentId)
            .OrderBy(x => x.Order)
            .ToList();

        foreach (var child in directChildren)
        {
            var hasChildren = catalogs.Any(x => x.ParentId == child.Id);

            var node = new TreeNode
            {
                title = child.Name,
                key = child.Url ?? child.Id, // 使用URL作为key，如果为空则使用ID
                isLeaf = !hasChildren, // 如果没有子节点，则为叶子节点
                children = hasChildren ? new List<TreeNode>() : null,
                catalog = child
            };

            // 递归添加子节点
            if (hasChildren)
            {
                node.children = GetDocumentCatalogChildren(child.Id, catalogs);
            }

            children.Add(node);
        }

        return children;
    }
}

/// <summary>
/// 文件树节点
/// </summary>
public class TreeNode
{
    /// <summary>
    /// 节点标题
    /// </summary>
    public string title { get; set; }

    /// <summary>
    /// 节点唯一标识
    /// </summary>
    public string key { get; set; }

    /// <summary>
    /// 是否为叶子节点(文件)
    /// </summary>
    public bool? isLeaf { get; set; }

    /// <summary>
    /// 子节点列表
    /// </summary>
    public List<TreeNode> children { get; set; }

    public DocumentCatalog catalog { get; set; }
}

/// <summary>
/// 更新仓库输入
/// </summary>
public class UpdateWarehouseInput
{
    /// <summary>
    /// 仓库名称
    /// </summary>
    public string? Name { get; set; }

    /// <summary>
    /// 仓库描述
    /// </summary>
    public string? Description { get; set; }
}

/// <summary>
/// 更新仓库同步设置输入
/// </summary>
public class UpdateWarehouseSyncInput
{
    /// <summary>
    /// 是否启用同步
    /// </summary>
    public bool EnableSync { get; set; }
}

/// <summary>
/// 仓库同步记录DTO
/// </summary>
public class WarehouseSyncRecordDto
{
    public string Id { get; set; }
    public string WarehouseId { get; set; }
    public string Status { get; set; }
    public DateTime StartTime { get; set; }
    public DateTime? EndTime { get; set; }
    public string? FromVersion { get; set; }
    public string? ToVersion { get; set; }
    public string? ErrorMessage { get; set; }
    public int FileCount { get; set; }
    public int UpdatedFileCount { get; set; }
    public int AddedFileCount { get; set; }
    public int DeletedFileCount { get; set; }
    public string Trigger { get; set; }
    public DateTime CreatedAt { get; set; }
}