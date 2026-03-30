using System.ComponentModel.DataAnnotations;
using FastService;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains.Users;
using KoalaWiki.Dto;
using KoalaWiki.Infrastructure;
using MapsterMapper;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Services;

/// <summary>
/// 角色管理服务
/// </summary>
[Tags("角色管理")]
[Route("/api/Role")]
[Filter(typeof(ResultFilter))]
[Authorize(Roles = "admin")]
public class RoleService(
    IKoalaWikiContext dbContext,
    IMapper mapper,
    ILogger<RoleService> logger,
    IUserContext userContext) : FastApi
{
    /// <summary>
    /// 获取角色列表
    /// </summary>
    /// <param name="page">页码</param>
    /// <param name="pageSize">每页数量</param>
    /// <param name="keyword">搜索关键词</param>
    /// <param name="isActive">是否启用筛选</param>
    /// <returns>角色列表</returns>
    [EndpointSummary("获取角色列表")]
    public async Task<PageDto<RoleInfoDto>> GetRoleListAsync(int? page = 1, int? pageSize = 20, string? keyword = null,
        bool? isActive = null)
    {
        try
        {
            page ??= 1;
            pageSize ??= int.MaxValue;

            var query = dbContext.Roles.AsNoTracking();

            // 关键词搜索
            if (!string.IsNullOrWhiteSpace(keyword))
            {
                query = query.Where(r =>
                    r.Name.Contains(keyword) || (r.Description != null && r.Description.Contains(keyword)));
            }

            // 状态筛选
            if (isActive.HasValue)
            {
                query = query.Where(r => r.IsActive == isActive.Value);
            }

            // 按创建时间降序排序
            query = query.OrderByDescending(r => r.CreatedAt);

            // 计算总数
            var total = await query.CountAsync();

            // 获取分页数据
            var roles = await query
                .Skip((page.Value - 1) * pageSize.Value)
                .Take(pageSize.Value)
                .ToListAsync();

            // 获取每个角色的用户数量和仓库权限数量
            var roleInfos = new List<RoleInfoDto>();
            foreach (var role in roles)
            {
                var roleInfo = mapper.Map<RoleInfoDto>(role);

                // 计算用户数量
                roleInfo.UserCount = await dbContext.UserInRoles
                    .Where(ur => ur.RoleId == role.Id)
                    .CountAsync();

                // 计算仓库权限数量
                roleInfo.WarehousePermissionCount = await dbContext.WarehouseInRoles
                    .Where(wr => wr.RoleId == role.Id)
                    .CountAsync();

                roleInfos.Add(roleInfo);
            }

            return new PageDto<RoleInfoDto>(total, roleInfos);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取角色列表失败");
            throw;
        }
    }

    /// <summary>
    /// 获取角色详情
    /// </summary>
    /// <param name="id">角色ID</param>
    /// <returns>角色详情</returns>
    [EndpointSummary("获取角色详情")]
    public async Task<RoleDetailDto> GetRoleDetailAsync([Required] string id)
    {
        try
        {
            var role = await dbContext.Roles
                .AsNoTracking()
                .FirstOrDefaultAsync(r => r.Id == id);

            if (role == null)
            {
                throw new ArgumentException($"角色不存在: {id}");
            }

            var roleDetail = mapper.Map<RoleDetailDto>(role);

            // 获取拥有该角色的用户
            var userIds = await dbContext.UserInRoles
                .Where(ur => ur.RoleId == id)
                .Select(ur => ur.UserId)
                .ToListAsync();

            var users = await dbContext.Users
                .Where(u => userIds.Contains(u.Id))
                .ToListAsync();

            roleDetail.Users = mapper.Map<List<UserInfoDto>>(users);

            // 获取仓库权限
            var warehousePermissions = await (from wr in dbContext.WarehouseInRoles
                join w in dbContext.Warehouses on wr.WarehouseId equals w.Id
                where wr.RoleId == id
                select new WarehousePermissionDetailDto
                {
                    WarehouseId = wr.WarehouseId,
                    IsReadOnly = wr.IsReadOnly,
                    IsWrite = wr.IsWrite,
                    IsDelete = wr.IsDelete,
                    OrganizationName = w.OrganizationName,
                    WarehouseName = w.Name,
                    WarehouseDescription = w.Description
                }).ToListAsync();

            roleDetail.WarehousePermissions = warehousePermissions;

            return roleDetail;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取角色详情失败, RoleId: {RoleId}", id);
            throw;
        }
    }

    /// <summary>
    /// 创建角色
    /// </summary>
    /// <param name="input">角色创建信息</param>
    /// <returns>创建的角色信息</returns>
    [EndpointSummary("创建角色")]
    public async Task<RoleInfoDto> CreateRoleAsync([Required] CreateRoleDto input)
    {
        try
        {
            // 检查角色名称是否已存在
            var existingRole = await dbContext.Roles
                .FirstOrDefaultAsync(r => r.Name == input.Name);

            if (existingRole != null)
            {
                throw new ArgumentException($"角色名称已存在: {input.Name}");
            }

            var role = new Role
            {
                Id = Guid.NewGuid().ToString("N"),
                Name = input.Name,
                Description = input.Description,
                IsActive = input.IsActive,
                IsSystemRole = false,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            await dbContext.Roles.AddAsync(role);
            await dbContext.SaveChangesAsync();

            logger.LogInformation("创建角色成功: {RoleName} by {UserId}", input.Name, userContext.CurrentUserId);

            var roleInfo = mapper.Map<RoleInfoDto>(role);
            roleInfo.UserCount = 0;
            roleInfo.WarehousePermissionCount = 0;

            return roleInfo;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "创建角色失败: {RoleName}", input.Name);
            throw;
        }
    }

    /// <summary>
    /// 更新角色
    /// </summary>
    /// <param name="id">角色ID</param>
    /// <param name="input">角色更新信息</param>
    /// <returns>更新后的角色信息</returns>
    [EndpointSummary("更新角色")]
    public async Task<RoleInfoDto> UpdateRoleAsync([Required] string id, [Required] UpdateRoleDto input)
    {
        try
        {
            var role = await dbContext.Roles.FirstOrDefaultAsync(r => r.Id == id);

            if (role == null)
            {
                throw new ArgumentException($"角色不存在: {id}");
            }

            if (role.IsSystemRole)
            {
                throw new InvalidOperationException("系统角色不能修改");
            }

            // 检查角色名称是否已存在（排除当前角色）
            var existingRole = await dbContext.Roles
                .FirstOrDefaultAsync(r => r.Name == input.Name && r.Id != id);

            if (existingRole != null)
            {
                throw new ArgumentException($"角色名称已存在: {input.Name}");
            }

            role.Name = input.Name;
            role.Description = input.Description;
            role.IsActive = input.IsActive;
            role.UpdatedAt = DateTime.UtcNow;

            dbContext.Roles.Update(role);
            await dbContext.SaveChangesAsync();

            logger.LogInformation("更新角色成功: {RoleName} by {UserId}", input.Name, userContext.CurrentUserId);

            var roleInfo = mapper.Map<RoleInfoDto>(role);

            // 计算用户数量和仓库权限数量
            roleInfo.UserCount = await dbContext.UserInRoles
                .Where(ur => ur.RoleId == id)
                .CountAsync();

            roleInfo.WarehousePermissionCount = await dbContext.WarehouseInRoles
                .Where(wr => wr.RoleId == id)
                .CountAsync();

            return roleInfo;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "更新角色失败: {RoleId}", id);
            throw;
        }
    }

    /// <summary>
    /// 删除角色
    /// </summary>
    /// <param name="id">角色ID</param>
    /// <returns>删除结果</returns>
    [EndpointSummary("删除角色")]
    public async Task<bool> DeleteRoleAsync([Required] string id)
    {
        try
        {
            var role = await dbContext.Roles.FirstOrDefaultAsync(r => r.Id == id);

            if (role == null)
            {
                throw new ArgumentException($"角色不存在: {id}");
            }

            if (role.IsSystemRole)
            {
                throw new InvalidOperationException("系统角色不能删除");
            }

            // 检查是否有用户分配了该角色
            var hasUsers = await dbContext.UserInRoles.AnyAsync(ur => ur.RoleId == id);
            if (hasUsers)
            {
                throw new InvalidOperationException("该角色已被分配给用户，无法删除");
            }

            // 删除角色的仓库权限
            var warehousePermissions = await dbContext.WarehouseInRoles
                .Where(wr => wr.RoleId == id)
                .ToListAsync();

            if (warehousePermissions.Any())
            {
                dbContext.WarehouseInRoles.RemoveRange(warehousePermissions);
            }

            // 删除角色
            dbContext.Roles.Remove(role);
            await dbContext.SaveChangesAsync();

            logger.LogInformation("删除角色成功: {RoleName} by {UserId}", role.Name, userContext.CurrentUserId);

            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "删除角色失败: {RoleId}", id);
            throw;
        }
    }

    /// <summary>
    /// 获取所有角色（简化版本，用于下拉选择）
    /// </summary>
    /// <returns>角色列表</returns>
    [EndpointSummary("获取所有角色")]
    [AllowAnonymous]
    public async Task<List<RoleInfoDto>> GetAllRolesAsync()
    {
        try
        {
            var roles = await dbContext.Roles
                .AsNoTracking()
                .Where(r => r.IsActive)
                .OrderBy(r => r.Name)
                .ToListAsync();

            return mapper.Map<List<RoleInfoDto>>(roles);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取所有角色失败");
            throw;
        }
    }

    /// <summary>
    /// 批量启用/禁用角色
    /// </summary>
    /// <param name="ids">角色ID列表</param>
    /// <param name="isActive">是否启用</param>
    /// <returns>操作结果</returns>
    [EndpointSummary("批量启用/禁用角色")]
    public async Task<bool> BatchUpdateRoleStatusAsync([Required] List<string> ids, bool isActive)
    {
        try
        {
            var roles = await dbContext.Roles
                .Where(r => ids.Contains(r.Id) && !r.IsSystemRole)
                .ToListAsync();

            if (!roles.Any())
            {
                throw new ArgumentException("没有找到可操作的角色");
            }

            foreach (var role in roles)
            {
                role.IsActive = isActive;
                role.UpdatedAt = DateTime.UtcNow;
            }

            dbContext.Roles.UpdateRange(roles);
            await dbContext.SaveChangesAsync();

            logger.LogInformation("批量更新角色状态成功: {RoleIds} -> {IsActive} by {UserId}",
                string.Join(", ", ids), isActive, userContext.CurrentUserId);

            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "批量更新角色状态失败: {RoleIds}", string.Join(", ", ids));
            throw;
        }
    }
}