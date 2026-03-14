using System.ComponentModel.DataAnnotations;

namespace KoalaWiki.Dto;

/// <summary>
/// 用户创建DTO
/// </summary>
public class CreateUserDto
{
    /// <summary>
    /// 用户名
    /// </summary>
    [Required(ErrorMessage = "用户名不能为空")]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 邮箱
    /// </summary>
    [Required(ErrorMessage = "邮箱不能为空")]
    [EmailAddress(ErrorMessage = "邮箱格式不正确")]
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// 密码
    /// </summary>
    [Required(ErrorMessage = "密码不能为空")]
    [MinLength(6, ErrorMessage = "密码长度不能小于6位")]
    public string Password { get; set; } = string.Empty;

    /// <summary>
    /// 角色
    /// </summary>
    public string Role { get; set; } = "user";

    /// <summary>
    /// 头像
    /// </summary>
    public string? Avatar { get; set; }
}

/// <summary>
/// 用户更新DTO
/// </summary>
public class UpdateUserDto
{
    /// <summary>
    /// 用户名
    /// </summary>
    [Required(ErrorMessage = "用户名不能为空")]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 邮箱
    /// </summary>
    [Required(ErrorMessage = "邮箱不能为空")]
    [EmailAddress(ErrorMessage = "邮箱格式不正确")]
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// 密码（可选）
    /// </summary>
    public string? Password { get; set; }

    /// <summary>
    /// 角色
    /// </summary>
    public string Role { get; set; } = "user";

    /// <summary>
    /// 头像
    /// </summary>
    public string? Avatar { get; set; }
}

/// <summary>
/// 用户信息DTO（返回给前端）
/// </summary>
public class UserInfoDto
{
    /// <summary>
    /// 用户ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 用户名
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 邮箱
    /// </summary>
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// 角色
    /// </summary>
    public string Role { get; set; } = string.Empty;

    /// <summary>
    /// 头像
    /// </summary>
    public string? Avatar { get; set; }

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime? UpdatedAt { get; set; }

    /// <summary>
    /// 最后登录时间
    /// </summary>
    public DateTime? LastLoginAt { get; set; }

    /// <summary>
    /// 最后登录IP
    /// </summary>
    public string? LastLoginIp { get; set; }
}

/// <summary>
/// 更新用户资料DTO
/// </summary>
public class UpdateProfileDto
{
    /// <summary>
    /// 用户名
    /// </summary>
    [Required(ErrorMessage = "用户名不能为空")]
    [StringLength(50, MinimumLength = 2, ErrorMessage = "用户名长度必须在2-50个字符之间")]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 邮箱
    /// </summary>
    [Required(ErrorMessage = "邮箱不能为空")]
    [EmailAddress(ErrorMessage = "邮箱格式不正确")]
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// 头像
    /// </summary>
    public string? Avatar { get; set; }
}

/// <summary>
/// 验证密码DTO
/// </summary>
public class VerifyPasswordDto
{
    /// <summary>
    /// 密码
    /// </summary>
    [Required(ErrorMessage = "密码不能为空")]
    public string Password { get; set; } = string.Empty;
}

/// <summary>
/// 修改密码DTO
/// </summary>
public class ChangePasswordDto
{
    /// <summary>
    /// 当前密码
    /// </summary>
    [Required(ErrorMessage = "当前密码不能为空")]
    public string CurrentPassword { get; set; } = string.Empty;

    /// <summary>
    /// 新密码
    /// </summary>
    [Required(ErrorMessage = "新密码不能为空")]
    [MinLength(8, ErrorMessage = "新密码长度不能小于8位")]
    [RegularExpression(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$",
        ErrorMessage = "新密码必须包含大小写字母和数字")]
    public string NewPassword { get; set; } = string.Empty;
}

/// <summary>
/// 重置密码DTO
/// </summary>
public class ResetPasswordDto
{
    /// <summary>
    /// 新密码
    /// </summary>
    [Required(ErrorMessage = "新密码不能为空")]
    [MinLength(6, ErrorMessage = "新密码长度不能小于6位")]
    public string NewPassword { get; set; } = string.Empty;
}

/// <summary>
/// 分配用户角色DTO
/// </summary>
public class AssignUserRoleDto
{
    /// <summary>
    /// 角色ID列表
    /// </summary>
    [Required(ErrorMessage = "角色ID列表不能为空")]
    public List<string> RoleIds { get; set; } = new();
}

/// <summary>
/// 批量删除用户DTO
/// </summary>
public class BatchDeleteUserDto
{
    /// <summary>
    /// 用户ID列表
    /// </summary>
    [Required(ErrorMessage = "用户ID列表不能为空")]
    [MinLength(1, ErrorMessage = "至少选择一个用户")]
    public List<string> UserIds { get; set; } = new();
}