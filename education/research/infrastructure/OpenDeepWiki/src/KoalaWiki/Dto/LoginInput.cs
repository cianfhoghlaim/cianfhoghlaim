namespace KoalaWiki.Dto;

/// <summary>
/// 登录输入模型
/// </summary>
public class LoginInput
{
    /// <summary>
    /// 用户名或邮箱
    /// </summary>
    public string Username { get; set; } = string.Empty;

    /// <summary>
    /// 密码
    /// </summary>
    public string Password { get; set; } = string.Empty;
}