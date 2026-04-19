using System.ComponentModel.DataAnnotations;
using FastService;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains.Users;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Dto;
using KoalaWiki.Infrastructure;
using MapsterMapper;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Services;

/// <summary>
/// 权限管理服务
/// </summary>
[Tags("权限管理")]
[Route("/api/Permission")]
[Filter(typeof(ResultFilter))]
[Authorize(Roles = "admin")]
public class PermissionService(
    IKoalaWikiContext dbContext,
    IMapper mapper,
    ILogger<PermissionService> logger,
    IUserContext userContext) : FastApi
{
    /// <summary>
    /// 获取仓库权限树形结构
    /// </summary>
    /// <param name="roleId">角色ID（可选，用于显示当前权限配置）</param>
    /// <returns>权限树</returns>
    [EndpointSummary("获取仓库权限树形结构")]
    public async Task<List<WarehousePermissionTreeDto>> GetWarehousePermissionTreeAsync(string? roleId = null)
    {
        try
        {
            // 获取所有仓库，按组织分组
            var warehouses = await dbContext.Warehouses
                .AsNoTracking()
                .Where(w => w.Status == WarehouseStatus.Completed)
                .OrderBy(w => w.OrganizationName)
                .ThenBy(w => w.Name)
                .ToListAsync();

            // 获取角色的现有权限（如果提供了角色ID）
            Dictionary<string, WarehouseInRole> existingPermissions = new();
            if (!string.IsNullOrEmpty(roleId))
            {
                var permissions = await dbContext.WarehouseInRoles
                    .Where(wr => wr.RoleId == roleId)
                    .ToListAsync();

                existingPermissions = permissions.ToDictionary(p => p.WarehouseId, p => p);
            }

            // 按组织分组构建树形结构
            var tree = new List<WarehousePermissionTreeDto>();
            var organizationGroups = warehouses.GroupBy(w => w.OrganizationName);

            foreach (var orgGroup in organizationGroups)
            {
                var orgNode = new WarehousePermissionTreeDto
                {
                    Id = $"org_{orgGroup.Key}",
                    Name = orgGroup.Key,
                    Type = "organization",
                    IsSelected = false,
                    Children = new List<WarehousePermissionTreeDto>()
                };

                // 检查组织下是否所有仓库都被选中
                var orgWarehouses = orgGroup.ToList();
                var selectedWarehouseCount = 0;

                foreach (var warehouse in orgWarehouses)
                {
                    var isSelected = existingPermissions.ContainsKey(warehouse.Id);
                    if (isSelected) selectedWarehouseCount++;

                    var warehouseNode = new WarehousePermissionTreeDto
                    {
                        Id = warehouse.Id,
                        Name = warehouse.Name,
                        Type = "warehouse",
                        IsSelected = isSelected
                    };

                    // 如果选中，设置权限配置
                    if (isSelected && existingPermissions.TryGetValue(warehouse.Id, out var permission))
                    {
                        warehouseNode.Permission = new WarehousePermissionDto
                        {
                            WarehouseId = warehouse.Id,
                            IsReadOnly = permission.IsReadOnly,
                            IsWrite = permission.IsWrite,
                            IsDelete = permission.IsDelete
                        };
                    }

                    orgNode.Children.Add(warehouseNode);
                }

                // 如果组织下所有仓库都被选中，则标记组织为选中
                orgNode.IsSelected = selectedWarehouseCount > 0 && selectedWarehouseCount == orgWarehouses.Count;

                tree.Add(orgNode);
            }

            return tree;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取仓库权限树失败");
            throw;
        }
    }

    /// <summary>
    /// 设置角色权限
    /// </summary>
    /// <param name="input">权限配置</param>
    /// <returns>操作结果</returns>
    [EndpointSummary("设置角色权限")]
    public async Task<bool> SetRolePermissionsAsync([Required] RolePermissionDto input)
    {
        try
        {
            // 验证角色是否存在
            var role = await dbContext.Roles.FirstOrDefaultAsync(r => r.Id == input.RoleId);
            if (role == null)
            {
                throw new ArgumentException($"角色不存在: {input.RoleId}");
            }

            if (role.IsSystemRole)
            {
                throw new InvalidOperationException("系统角色权限不能修改");
            }

            // 删除角色现有的所有仓库权限
            var existingPermissions = await dbContext.WarehouseInRoles
                .Where(wr => wr.RoleId == input.RoleId)
                .ToListAsync();

            if (existingPermissions.Any())
            {
                dbContext.WarehouseInRoles.RemoveRange(existingPermissions);
            }

            // 添加新的权限配置
            if (input.WarehousePermissions.Any())
            {
                // 验证仓库是否存在
                var warehouseIds = input.WarehousePermissions.Select(wp => wp.WarehouseId).ToList();
                var validWarehouses = await dbContext.Warehouses
                    .Where(w => warehouseIds.Contains(w.Id))
                    .Select(w => w.Id)
                    .ToListAsync();

                var newPermissions = new List<WarehouseInRole>();
                foreach (var permission in input.WarehousePermissions)
                {
                    if (!validWarehouses.Contains(permission.WarehouseId))
                    {
                        logger.LogWarning("跳过无效的仓库ID: {WarehouseId}", permission.WarehouseId);
                        continue;
                    }

                    newPermissions.Add(new WarehouseInRole
                    {
                        RoleId = input.RoleId,
                        WarehouseId = permission.WarehouseId,
                        IsReadOnly = permission.IsReadOnly,
                        IsWrite = permission.IsWrite,
                        IsDelete = permission.IsDelete
                    });
                }

                if (newPermissions.Any())
                {
                    await dbContext.WarehouseInRoles.AddRangeAsync(newPermissions);
                }
            }

            await dbContext.SaveChangesAsync();
            logger.LogInformation("设置角色权限成功: RoleId={RoleId}, PermissionCount={Count} by {UserId}",
                input.RoleId, input.WarehousePermissions.Count, userContext.CurrentUserId);

            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "设置角色权限失败: RoleId={RoleId}", input.RoleId);
            throw;
        }
    }

    /// <summary>
    /// 获取角色的仓库权限列表
    /// </summary>
    /// <param name="roleId">角色ID</param>
    /// <returns>权限列表</returns>
    [EndpointSummary("获取角色的仓库权限列表")]
    public async Task<List<WarehousePermissionDetailDto>> GetRoleWarehousePermissionsAsync([Required] string roleId)
    {
        try
        {
            var permissions = await (from wr in dbContext.WarehouseInRoles
                join w in dbContext.Warehouses on wr.WarehouseId equals w.Id
                where wr.RoleId == roleId
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

            return permissions;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取角色仓库权限失败: RoleId={RoleId}", roleId);
            throw;
        }
    }

    /// <summary>
    /// 分配用户角色
    /// </summary>
    /// <param name="input">用户角色分配信息</param>
    /// <returns>操作结果</returns>
    [EndpointSummary("分配用户角色")]
    public async Task<bool> AssignUserRolesAsync([Required] UserRoleDto input)
    {
        try
        {
            // 验证用户是否存在
            var user = await dbContext.Users.FirstOrDefaultAsync(u => u.Id == input.UserId);
            if (user == null)
            {
                throw new ArgumentException($"用户不存在: {input.UserId}");
            }

            // 验证角色是否存在且有效
            var validRoles = await dbContext.Roles
                .Where(r => input.RoleIds.Contains(r.Id) && r.IsActive)
                .Select(r => r.Id)
                .ToListAsync();

            // 删除用户现有的角色分配
            var existingUserRoles = await dbContext.UserInRoles
                .Where(ur => ur.UserId == input.UserId)
                .ToListAsync();

            if (existingUserRoles.Any())
            {
                dbContext.UserInRoles.RemoveRange(existingUserRoles);
            }

            // 添加新的角色分配
            if (validRoles.Any())
            {
                var newUserRoles = validRoles.Select(roleId => new UserInRole
                {
                    UserId = input.UserId,
                    RoleId = roleId
                }).ToList();

                await dbContext.UserInRoles.AddRangeAsync(newUserRoles);
            }

            await dbContext.SaveChangesAsync();

            logger.LogInformation("分配用户角色成功: UserId={UserId}, RoleIds={RoleIds} by {CurrentUserId}",
                input.UserId, string.Join(", ", validRoles), userContext.CurrentUserId);

            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "分配用户角色失败: UserId={UserId}", input.UserId);
            throw;
        }
    }

    /// <summary>
    /// 获取用户的角色列表
    /// </summary>
    /// <param name="userId">用户ID</param>
    /// <returns>角色列表</returns>
    [EndpointSummary("获取用户的角色列表")]
    public async Task<List<RoleInfoDto>> GetUserRolesAsync([Required] string userId)
    {
        try
        {
            var roles = await (from ur in dbContext.UserInRoles
                join r in dbContext.Roles on ur.RoleId equals r.Id
                where ur.UserId == userId
                select r).ToListAsync();

            return mapper.Map<List<RoleInfoDto>>(roles);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取用户角色失败: UserId={UserId}", userId);
            throw;
        }
    }

    /// <summary>
    /// 检查用户对仓库的权限
    /// </summary>
    /// <param name="userId">用户ID</param>
    /// <param name="warehouseId">仓库ID</param>
    /// <returns>权限信息</returns>
    [EndpointSummary("检查用户对仓库的权限")]
    [AllowAnonymous]
    public async Task<WarehousePermissionDto?> CheckUserWarehousePermissionAsync([Required] string userId,
        [Required] string warehouseId)
    {
        try
        {
            // 获取用户的所有角色
            var userRoleIds = await dbContext.UserInRoles
                .Where(ur => ur.UserId == userId)
                .Select(ur => ur.RoleId)
                .ToListAsync();

            if (!userRoleIds.Any())
            {
                return null;
            }

            // 获取用户角色对该仓库的权限（取最高权限）
            var permissions = await dbContext.WarehouseInRoles
                .Where(wr => userRoleIds.Contains(wr.RoleId) && wr.WarehouseId == warehouseId)
                .ToListAsync();

            if (!permissions.Any())
            {
                return null;
            }

            // 合并权限（任一角色有权限则认为用户有权限）
            var mergedPermission = new WarehousePermissionDto
            {
                WarehouseId = warehouseId,
                IsReadOnly = permissions.Any(p => p.IsReadOnly),
                IsWrite = permissions.Any(p => p.IsWrite),
                IsDelete = permissions.Any(p => p.IsDelete)
            };

            return mergedPermission;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "检查用户仓库权限失败: UserId={UserId}, WarehouseId={WarehouseId}", userId, warehouseId);
            throw;
        }
    }

    /// <summary>
    /// 获取用户可访问的仓库列表
    /// </summary>
    /// <param name="userId">用户ID</param>
    /// <returns>可访问的仓库列表</returns>
    [EndpointSummary("获取用户可访问的仓库列表")]
    [AllowAnonymous]
    public async Task<List<WarehousePermissionDetailDto>> GetUserAccessibleWarehousesAsync([Required] string userId)
    {
        try
        {
            // 获取用户的所有角色
            var userRoleIds = await dbContext.UserInRoles
                .Where(ur => ur.UserId == userId)
                .Select(ur => ur.RoleId)
                .ToListAsync();

            if (!userRoleIds.Any())
            {
                return new List<WarehousePermissionDetailDto>();
            }

            // 获取用户通过角色可访问的仓库
            var accessibleWarehouses = await (from wr in dbContext.WarehouseInRoles
                join w in dbContext.Warehouses on wr.WarehouseId equals w.Id
                where userRoleIds.Contains(wr.RoleId)
                group wr by new { w.Id, w.OrganizationName, w.Name, w.Description }
                into g
                select new WarehousePermissionDetailDto
                {
                    WarehouseId = g.Key.Id,
                    OrganizationName = g.Key.OrganizationName,
                    WarehouseName = g.Key.Name,
                    WarehouseDescription = g.Key.Description,
                    // 合并权限（任一角色有权限则认为用户有权限）
                    IsReadOnly = g.Any(x => x.IsReadOnly),
                    IsWrite = g.Any(x => x.IsWrite),
                    IsDelete = g.Any(x => x.IsDelete)
                }).ToListAsync();

            return accessibleWarehouses;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取用户可访问仓库失败: UserId={UserId}", userId);
            throw;
        }
    }

    /// <summary>
    /// 批量设置组织权限（为角色设置某个组织下所有仓库的权限）
    /// </summary>
    /// <param name="roleId">角色ID</param>
    /// <param name="organizationName">组织名称</param>
    /// <param name="input">权限配置</param>
    /// <returns>操作结果</returns>
    [EndpointSummary("批量设置组织权限")]
    public async Task<bool> SetOrganizationPermissionsAsync([Required] string roleId,
        [Required] string organizationName, [Required] WarehousePermissionDto input)
    {
        try
        {
            // 验证角色是否存在
            var role = await dbContext.Roles.FirstOrDefaultAsync(r => r.Id == roleId);
            if (role == null)
            {
                throw new ArgumentException($"角色不存在: {roleId}");
            }

            if (role.IsSystemRole)
            {
                throw new InvalidOperationException("系统角色权限不能修改");
            }

            // 获取组织下所有仓库
            var warehouses = await dbContext.Warehouses
                .Where(w => w.OrganizationName == organizationName && w.Status == WarehouseStatus.Completed)
                .ToListAsync();

            if (!warehouses.Any())
            {
                throw new ArgumentException($"组织下没有找到可用的仓库: {organizationName}");
            }

            // 删除该组织下所有仓库的现有权限
            var warehouseIds = warehouses.Select(w => w.Id).ToList();
            var existingPermissions = await dbContext.WarehouseInRoles
                .Where(wr => wr.RoleId == roleId && warehouseIds.Contains(wr.WarehouseId))
                .ToListAsync();

            if (existingPermissions.Any())
            {
                dbContext.WarehouseInRoles.RemoveRange(existingPermissions);
            }

            // 添加新的权限配置
            var newPermissions = warehouses.Select(w => new WarehouseInRole
            {
                RoleId = roleId,
                WarehouseId = w.Id,
                IsReadOnly = input.IsReadOnly,
                IsWrite = input.IsWrite,
                IsDelete = input.IsDelete
            }).ToList();

            await dbContext.WarehouseInRoles.AddRangeAsync(newPermissions);
            await dbContext.SaveChangesAsync();

            logger.LogInformation(
                "批量设置组织权限成功: RoleId={RoleId}, Organization={Organization}, WarehouseCount={Count} by {UserId}",
                roleId, organizationName, warehouses.Count, userContext.CurrentUserId);

            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "批量设置组织权限失败: RoleId={RoleId}, Organization={Organization}", roleId, organizationName);
            throw;
        }
    }
}