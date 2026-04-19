using System;

namespace KoalaWiki.Core.DataAccess;

/// <summary>
/// 用户上下文接口
/// </summary>
public interface IUserContext
{
    /// <summary>
    /// 获取当前用户ID
    /// </summary>
    string? CurrentUserId { get; }
    
    /// <summary>
    /// 获取当前用户名
    /// </summary>
    string? CurrentUserName { get; }
    
    /// <summary>
    /// 获取当前用户邮箱
    /// </summary>
    string? CurrentUserEmail { get; }
    
    /// <summary>
    /// 获取当前用户角色
    /// </summary>
    string? CurrentUserRole { get; }
    
    /// <summary>
    /// 判断用户是否已认证
    /// </summary>
    bool IsAuthenticated { get; }
    
    /// <summary>
    /// 判断用户是否是管理员
    /// </summary>
    bool IsAdmin { get; }
} 