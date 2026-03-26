using System.Security.Claims;
using KoalaWiki.Core.DataAccess;

namespace KoalaWiki.Infrastructure;

/// <summary>
/// 用户上下文实现
/// </summary>
public class UserContext : IUserContext
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    /// <summary>
    /// 构造函数
    /// </summary>
    /// <param name="httpContextAccessor">HTTP上下文访问器</param>
    public UserContext(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    /// <summary>
    /// 获取当前用户ID
    /// </summary>
    public string? CurrentUserId => _httpContextAccessor.HttpContext?.User?.FindFirstValue(ClaimTypes.NameIdentifier);

    /// <summary>
    /// 获取当前用户名
    /// </summary>
    public string? CurrentUserName => _httpContextAccessor.HttpContext?.User?.FindFirstValue(ClaimTypes.Name);

    /// <summary>
    /// 获取当前用户邮箱
    /// </summary>
    public string? CurrentUserEmail => _httpContextAccessor.HttpContext?.User?.FindFirstValue(ClaimTypes.Email);

    /// <summary>
    /// 获取当前用户角色
    /// </summary>
    public string? CurrentUserRole => _httpContextAccessor.HttpContext?.User?.FindFirstValue(ClaimTypes.Role);

    /// <summary>
    /// 判断用户是否已认证
    /// </summary>
    public bool IsAuthenticated => _httpContextAccessor.HttpContext?.User?.Identity?.IsAuthenticated ?? false;

    /// <summary>
    /// 判断用户是否是管理员
    /// </summary>
    public bool IsAdmin => _httpContextAccessor.HttpContext?.User?.IsInRole("admin") ?? false;
} 