namespace KoalaWiki.Dto;

public class RegisterInput
{
    /// <summary>
    /// 用户名
    /// </summary>
    public string UserName { get; set; } = string.Empty;

    /// <summary>
    /// 密码
    /// </summary>
    public string Password { get; set; } = string.Empty;

    /// <summary>
    /// 邮箱
    /// </summary>
    public string Email { get; set; } = string.Empty;
}