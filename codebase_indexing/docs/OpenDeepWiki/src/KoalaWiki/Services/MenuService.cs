using FastService;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Dto;
using KoalaWiki.Infrastructure;
using MapsterMapper;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Services;

/// <summary>
/// 菜单管理服务
/// </summary>
[Tags("菜单管理")]
[Route("/api/Menu")]
[Filter(typeof(ResultFilter))]
public class MenuService(
    IKoalaWikiContext dbContext,
    IMapper mapper,
    ILogger<MenuService> logger,
    IUserContext userContext) : FastApi
{
    /// <summary>
    /// 获取当前用户的菜单
    /// </summary>
    /// <returns>用户菜单</returns>
    [EndpointSummary("获取当前用户的菜单")]
    [Authorize]
    public async Task<UserMenuDto> GetUserMenuAsync()
    {
        try
        {
            var userId = userContext.CurrentUserId;
            if (string.IsNullOrEmpty(userId))
            {
                throw new UnauthorizedAccessException("用户未登录");
            }

            // 获取用户信息
            var user = await dbContext.Users
                .AsNoTracking()
                .FirstOrDefaultAsync(u => u.Id == userId);

            if (user == null)
            {
                throw new ArgumentException("用户不存在");
            }

            var userInfo = mapper.Map<UserInfoDto>(user);

            // 获取用户角色
            var userRoleIds = await dbContext.UserInRoles
                .Where(ur => ur.UserId == userId)
                .Select(ur => ur.RoleId)
                .ToListAsync();

            var userRoles = await dbContext.Roles
                .Where(r => userRoleIds.Contains(r.Id))
                .Select(r => r.Name)
                .ToListAsync();

            userInfo.Role = string.Join(',', userRoles);

            // 构建菜单
            var menus = BuildUserMenus(userRoles);

            return new UserMenuDto
            {
                User = userInfo,
                Menus = menus
            };
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取用户菜单失败: UserId={UserId}", userContext.CurrentUserId);
            throw;
        }
    }

    /// <summary>
    /// 获取系统菜单结构（管理员权限）
    /// </summary>
    /// <returns>完整菜单结构</returns>
    [EndpointSummary("获取系统菜单结构")]
    [Authorize(Roles = "admin")]
    public async Task<List<MenuItemDto>> GetSystemMenusAsync()
    {
        try
        {
            await Task.CompletedTask; // 占位，实际可能从数据库读取
            return GetSystemMenuStructure();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取系统菜单失败");
            throw;
        }
    }

    /// <summary>
    /// 构建用户菜单
    /// </summary>
    /// <param name="userRoles">用户角色列表</param>
    /// <returns>菜单列表</returns>
    private List<MenuItemDto> BuildUserMenus(List<string> userRoles)
    {
        var allMenus = GetSystemMenuStructure();
        var userMenus = new List<MenuItemDto>();

        foreach (var menu in allMenus)
        {
            var filteredMenu = FilterMenuByRoles(menu, userRoles);
            if (filteredMenu != null)
            {
                userMenus.Add(filteredMenu);
            }
        }

        return userMenus;
    }

    /// <summary>
    /// 根据角色过滤菜单
    /// </summary>
    /// <param name="menu">菜单项</param>
    /// <param name="userRoles">用户角色</param>
    /// <returns>过滤后的菜单项</returns>
    private MenuItemDto? FilterMenuByRoles(MenuItemDto menu, List<string> userRoles)
    {
        // 检查当前菜单项是否有权限访问
        var hasAccess = !menu.RequiredRoles.Any() || menu.RequiredRoles.Any(role => userRoles.Contains(role));

        if (!hasAccess)
        {
            return null;
        }

        // 过滤子菜单
        var filteredChildren = new List<MenuItemDto>();
        foreach (var child in menu.Children)
        {
            var filteredChild = FilterMenuByRoles(child, userRoles);
            if (filteredChild != null)
            {
                filteredChildren.Add(filteredChild);
            }
        }

        // 如果当前菜单有权限但所有子菜单都没权限，仍然显示当前菜单
        return new MenuItemDto
        {
            Id = menu.Id,
            Name = menu.Name,
            Path = menu.Path,
            Icon = menu.Icon,
            Order = menu.Order,
            IsHidden = menu.IsHidden,
            RequiredRoles = menu.RequiredRoles,
            Children = filteredChildren
        };
    }

    /// <summary>
    /// 获取系统菜单结构定义
    /// </summary>
    /// <returns>菜单结构</returns>
    private List<MenuItemDto> GetSystemMenuStructure()
    {
        return new List<MenuItemDto>
        {
            // 首页
            new MenuItemDto
            {
                Id = "dashboard",
                Name = "首页",
                Path = "/",
                Icon = "dashboard",
                Order = 1,
                RequiredRoles = new List<string>()
            },
            
            // 仓库管理
            new MenuItemDto
            {
                Id = "repositories",
                Name = "仓库管理",
                Path = "/repositories",
                Icon = "repository",
                Order = 2,
                RequiredRoles = new List<string>(),
                Children = new List<MenuItemDto>
                {
                    new MenuItemDto
                    {
                        Id = "repository-list",
                        Name = "仓库列表",
                        Path = "/repositories",
                        Order = 1,
                        RequiredRoles = new List<string>()
                    },
                    new MenuItemDto
                    {
                        Id = "repository-create",
                        Name = "创建仓库",
                        Path = "/repositories/create",
                        Order = 2,
                        RequiredRoles = new List<string> { "admin" }
                    }
                }
            },
            
            // 用户管理
            new MenuItemDto
            {
                Id = "users",
                Name = "用户管理",
                Path = "/admin/users",
                Icon = "user",
                Order = 3,
                RequiredRoles = new List<string> { "admin" }
            },
            
            // 角色管理
            new MenuItemDto
            {
                Id = "roles",
                Name = "角色管理",
                Path = "/admin/roles",
                Icon = "role",
                Order = 4,
                RequiredRoles = new List<string> { "admin" }
            },
            
            // 权限管理
            new MenuItemDto
            {
                Id = "permissions",
                Name = "权限管理",
                Path = "/admin/permissions",
                Icon = "permission",
                Order = 5,
                RequiredRoles = new List<string> { "admin" },
                Children = new List<MenuItemDto>
                {
                    new MenuItemDto
                    {
                        Id = "role-permissions",
                        Name = "角色权限",
                        Path = "/admin/permissions/roles",
                        Order = 1,
                        RequiredRoles = new List<string> { "admin" }
                    },
                    new MenuItemDto
                    {
                        Id = "user-roles",
                        Name = "用户角色",
                        Path = "/admin/permissions/users",
                        Order = 2,
                        RequiredRoles = new List<string> { "admin" }
                    }
                }
            },
            
            // 系统设置
            new MenuItemDto
            {
                Id = "settings",
                Name = "系统设置",
                Path = "/admin/settings",
                Icon = "setting",
                Order = 6,
                RequiredRoles = new List<string> { "admin" },
                Children = new List<MenuItemDto>
                {
                    new MenuItemDto
                    {
                        Id = "general-settings",
                        Name = "基本设置",
                        Path = "/admin/settings/general",
                        Order = 1,
                        RequiredRoles = new List<string> { "admin" }
                    },
                    new MenuItemDto
                    {
                        Id = "system-info",
                        Name = "系统信息",
                        Path = "/admin/settings/system",
                        Order = 2,
                        RequiredRoles = new List<string> { "admin" }
                    }
                }
            },
            
            // 微调管理
            new MenuItemDto
            {
                Id = "finetune",
                Name = "微调管理",
                Path = "/admin/finetune",
                Icon = "finetune",
                Order = 7,
                RequiredRoles = new List<string> { "admin" }
            },
            
            // 统计分析
            new MenuItemDto
            {
                Id = "statistics",
                Name = "统计分析",
                Path = "/admin/statistics",
                Icon = "statistics",
                Order = 8,
                RequiredRoles = new List<string> { "admin" }
            },
            
            // 个人设置
            new MenuItemDto
            {
                Id = "profile",
                Name = "个人设置",
                Path = "/settings",
                Icon = "profile",
                Order = 99,
                RequiredRoles = new List<string>()
            }
        };
    }

    /// <summary>
    /// 检查用户是否有访问指定路径的权限
    /// </summary>
    /// <param name="path">路径</param>
    /// <param name="userId">用户ID</param>
    /// <returns>是否有权限</returns>
    [EndpointSummary("检查用户路径访问权限")]
    [AllowAnonymous]
    public async Task<bool> CheckUserPathPermissionAsync(string path, string? userId = null)
    {
        try
        {
            userId ??= userContext.CurrentUserId;
            
            if (string.IsNullOrEmpty(userId))
            {
                return false;
            }

            // 获取用户角色
            var userRoleIds = await dbContext.UserInRoles
                .Where(ur => ur.UserId == userId)
                .Select(ur => ur.RoleId)
                .ToListAsync();

            var userRoles = await dbContext.Roles
                .Where(r => userRoleIds.Contains(r.Id))
                .Select(r => r.Name)
                .ToListAsync();

            // 查找路径对应的菜单项
            var allMenus = GetSystemMenuStructure();
            var menuItem = FindMenuByPath(allMenus, path);

            if (menuItem == null)
            {
                // 如果路径不在菜单定义中，默认允许访问（比如动态路由）
                return true;
            }

            // 检查权限
            return !menuItem.RequiredRoles.Any() || menuItem.RequiredRoles.Any(role => userRoles.Contains(role));
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "检查用户路径权限失败: Path={Path}, UserId={UserId}", path, userId);
            return false;
        }
    }

    /// <summary>
    /// 根据路径查找菜单项
    /// </summary>
    /// <param name="menus">菜单列表</param>
    /// <param name="path">路径</param>
    /// <returns>菜单项</returns>
    private MenuItemDto? FindMenuByPath(List<MenuItemDto> menus, string path)
    {
        foreach (var menu in menus)
        {
            if (menu.Path == path)
            {
                return menu;
            }

            var childResult = FindMenuByPath(menu.Children, path);
            if (childResult != null)
            {
                return childResult;
            }
        }

        return null;
    }
} 