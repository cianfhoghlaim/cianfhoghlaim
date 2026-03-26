using System.Security.Claims;
using KoalaWiki.Core.DataAccess;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Infrastructure;

/// <summary>
/// 权限中间件
/// </summary>
public class PermissionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<PermissionMiddleware> _logger;

    public PermissionMiddleware(RequestDelegate next, ILogger<PermissionMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context, IKoalaWikiContext dbContext)
    {
        // 检查是否需要仓库权限验证
        if (IsWarehouseProtectedRoute(context.Request.Path))
        {
            var hasPermission = await CheckWarehousePermissionAsync(context, dbContext);
            if (!hasPermission)
            {
                context.Response.StatusCode = 403;
                await context.Response.WriteAsync("Access denied: Insufficient warehouse permissions");
                return;
            }
        }

        try
        {

            await _next(context);
        }
        catch (UnauthorizedAccessException e)
        {
            _logger.LogWarning(e, "Unauthorized access attempt");
            context.Response.StatusCode = 401; // 未授权
            await context.Response.WriteAsync("Unauthorized access");
        }
    }

    /// <summary>
    /// 检查是否是需要仓库权限保护的路由
    /// </summary>
    /// <param name="path">请求路径</param>
    /// <returns>是否需要保护</returns>
    private bool IsWarehouseProtectedRoute(string path)
    {
        var protectedPatterns = new[]
        {
            "/api/Repository/",
            "/api/FineTuning/"
        };

        return protectedPatterns.Any(pattern => path.StartsWith(pattern, StringComparison.OrdinalIgnoreCase));
    }

    /// <summary>
    /// 检查用户的仓库权限
    /// </summary>
    /// <param name="context">HTTP上下文</param>
    /// <param name="dbContext">数据库上下文</param>
    /// <returns>是否有权限</returns>
    private async Task<bool> CheckWarehousePermissionAsync(HttpContext context, IKoalaWikiContext dbContext)
    {
        try
        {
            // 获取用户ID
            var userId = context.User?.FindFirstValue(ClaimTypes.NameIdentifier);
            if (string.IsNullOrEmpty(userId))
            {
                return false;
            }

            // 检查是否是管理员
            var isAdmin = context.User?.IsInRole("admin") ?? false;
            if (isAdmin)
            {
                return true; // 管理员有所有权限
            }

            // 从请求中提取仓库相关信息
            var warehouseInfo = ExtractWarehouseInfo(context.Request);
            if (warehouseInfo == null)
            {
                // 如果无法提取仓库信息，默认允许访问（可能是通用接口）
                return true;
            }

            // 获取用户角色
            var userRoleIds = await dbContext.UserInRoles
                .Where(ur => ur.UserId == userId)
                .Select(ur => ur.RoleId)
                .ToListAsync();

            if (!userRoleIds.Any())
            {
                return false;
            }

            // 查找仓库
            var warehouse = await FindWarehouseAsync(dbContext, warehouseInfo);
            if (warehouse == null)
            {
                return false;
            }

            // 检查用户是否有该仓库的访问权限
            var hasPermission = await dbContext.WarehouseInRoles
                .AnyAsync(wr => userRoleIds.Contains(wr.RoleId) && wr.WarehouseId == warehouse.Id);

            if (!hasPermission)
            {
                _logger.LogWarning("用户 {UserId} 尝试访问无权限的仓库 {WarehouseId}", userId, warehouse.Id);
            }

            return hasPermission;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "检查仓库权限时发生错误");
            return false;
        }
    }

    /// <summary>
    /// 从请求中提取仓库信息
    /// </summary>
    /// <param name="request">HTTP请求</param>
    /// <returns>仓库信息</returns>
    private WarehouseInfo? ExtractWarehouseInfo(HttpRequest request)
    {
        // 从查询参数中获取
        var organizationName = request.Query["organizationName"].FirstOrDefault() ?? 
                              request.Query["owner"].FirstOrDefault();
        var warehouseName = request.Query["name"].FirstOrDefault() ??
                           request.Query["warehouseName"].FirstOrDefault();
        var warehouseId = request.Query["warehouseId"].FirstOrDefault() ??
                         request.Query["id"].FirstOrDefault();

        // 从路径中获取
        var pathSegments = request.Path.Value?.Split('/', StringSplitOptions.RemoveEmptyEntries);
        if (pathSegments != null && pathSegments.Length >= 3)
        {
            organizationName ??= pathSegments.ElementAtOrDefault(2);
            warehouseName ??= pathSegments.ElementAtOrDefault(3);
        }

        // 从请求体中获取（如果是POST请求）
        if (request.Method == "POST" && request.ContentType?.Contains("application/json") == true)
        {
            // 这里可以根据需要解析请求体中的仓库信息
            // 为了性能考虑，这里暂时跳过
        }

        if (!string.IsNullOrEmpty(warehouseId))
        {
            return new WarehouseInfo { Id = warehouseId };
        }

        if (!string.IsNullOrEmpty(organizationName) && !string.IsNullOrEmpty(warehouseName))
        {
            return new WarehouseInfo 
            { 
                OrganizationName = organizationName, 
                Name = warehouseName 
            };
        }

        return null;
    }

    /// <summary>
    /// 根据仓库信息查找仓库
    /// </summary>
    /// <param name="dbContext">数据库上下文</param>
    /// <param name="warehouseInfo">仓库信息</param>
    /// <returns>仓库实体</returns>
    private async Task<KoalaWiki.Domains.Warehouse.Warehouse?> FindWarehouseAsync(
        IKoalaWikiContext dbContext, 
        WarehouseInfo warehouseInfo)
    {
        if (!string.IsNullOrEmpty(warehouseInfo.Id))
        {
            return await dbContext.Warehouses
                .AsNoTracking()
                .FirstOrDefaultAsync(w => w.Id == warehouseInfo.Id);
        }

        if (!string.IsNullOrEmpty(warehouseInfo.OrganizationName) && 
            !string.IsNullOrEmpty(warehouseInfo.Name))
        {
            return await dbContext.Warehouses
                .AsNoTracking()
                .FirstOrDefaultAsync(w => w.OrganizationName == warehouseInfo.OrganizationName && 
                                         w.Name == warehouseInfo.Name);
        }

        return null;
    }
}

/// <summary>
/// 仓库信息
/// </summary>
public class WarehouseInfo
{
    public string? Id { get; set; }
    public string? OrganizationName { get; set; }
    public string? Name { get; set; }
}

/// <summary>
/// 权限中间件扩展
/// </summary>
public static class PermissionMiddlewareExtensions
{
    /// <summary>
    /// 使用权限中间件
    /// </summary>
    /// <param name="builder">应用构建器</param>
    /// <returns>应用构建器</returns>
    public static IApplicationBuilder UsePermissionMiddleware(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<PermissionMiddleware>();
    }
} 