using System;

namespace KoalaWiki.Domains.Users;

public class User : Entity<string>
{
    /// <summary>
    /// 用户名称
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 用户邮箱
    /// </summary>
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// 用户密码
    /// </summary>
    public string Password { get; set; } = string.Empty;

    /// <summary>
    /// 用户头像
    /// </summary>
    public string Avatar { get; set; } = string.Empty;

    /// <summary>
    /// 用户创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// 用户更新时间
    /// </summary>
    public DateTime? UpdatedAt { get; set; } 

    /// <summary>
    /// 用户最后登录时间
    /// </summary>
    public DateTime? LastLoginAt { get; set; }

    /// <summary>
    /// 用户最后登录IP
    /// </summary>
    public string? LastLoginIp { get; set; }

    /// <summary>
    /// 用户简介
    /// </summary>
    public string? Bio { get; set; }

    /// <summary>
    /// 用户位置
    /// </summary>
    public string? Location { get; set; }

    /// <summary>
    /// 用户个人网站
    /// </summary>
    public string? Website { get; set; }

    /// <summary>
    /// 用户公司
    /// </summary>
    public string? Company { get; set; }
}