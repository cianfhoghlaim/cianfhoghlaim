namespace KoalaWiki.Dto;

/// <summary>
/// 菜单项DTO
/// </summary>
public class MenuItemDto
{
    /// <summary>
    /// 菜单ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 菜单名称
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 菜单路径
    /// </summary>
    public string Path { get; set; } = string.Empty;

    /// <summary>
    /// 菜单图标
    /// </summary>
    public string? Icon { get; set; }

    /// <summary>
    /// 排序
    /// </summary>
    public int Order { get; set; }

    /// <summary>
    /// 是否隐藏
    /// </summary>
    public bool IsHidden { get; set; } = false;

    /// <summary>
    /// 所需角色
    /// </summary>
    public List<string> RequiredRoles { get; set; } = new();

    /// <summary>
    /// 子菜单
    /// </summary>
    public List<MenuItemDto> Children { get; set; } = new();
}

/// <summary>
/// 用户菜单DTO
/// </summary>
public class UserMenuDto
{
    /// <summary>
    /// 用户信息
    /// </summary>
    public UserInfoDto? User { get; set; }

    /// <summary>
    /// 菜单列表
    /// </summary>
    public List<MenuItemDto> Menus { get; set; } = new();
} 