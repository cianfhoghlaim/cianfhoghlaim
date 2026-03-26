using System.ComponentModel.DataAnnotations;
using KoalaWiki.Domains.Users;

namespace KoalaWiki.Dto;

/// <summary>
/// 角色创建DTO
/// </summary>
public class CreateRoleDto
{
    /// <summary>
    /// 角色名称
    /// </summary>
    [Required(ErrorMessage = "角色名称不能为空")]
    [StringLength(50, MinimumLength = 2, ErrorMessage = "角色名称长度必须在2-50个字符之间")]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 角色描述
    /// </summary>
    [StringLength(200, ErrorMessage = "角色描述长度不能超过200个字符")]
    public string? Description { get; set; }

    /// <summary>
    /// 是否启用
    /// </summary>
    public bool IsActive { get; set; } = true;
}

/// <summary>
/// 角色更新DTO
/// </summary>
public class UpdateRoleDto
{
    /// <summary>
    /// 角色名称
    /// </summary>
    [Required(ErrorMessage = "角色名称不能为空")]
    [StringLength(50, MinimumLength = 2, ErrorMessage = "角色名称长度必须在2-50个字符之间")]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 角色描述
    /// </summary>
    [StringLength(200, ErrorMessage = "角色描述长度不能超过200个字符")]
    public string? Description { get; set; }

    /// <summary>
    /// 是否启用
    /// </summary>
    public bool IsActive { get; set; } = true;
}

/// <summary>
/// 角色信息DTO（返回给前端）
/// </summary>
public class RoleInfoDto
{
    /// <summary>
    /// 角色ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 角色名称
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 角色描述
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// 是否启用
    /// </summary>
    public bool IsActive { get; set; } = true;

    /// <summary>
    /// 是否为系统角色
    /// </summary>
    public bool IsSystemRole { get; set; } = false;

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; }

    /// <summary>
    /// 用户数量
    /// </summary>
    public int UserCount { get; set; }

    /// <summary>
    /// 仓库权限数量
    /// </summary>
    public int WarehousePermissionCount { get; set; }
}

/// <summary>
/// 角色权限分配DTO
/// </summary>
public class RolePermissionDto
{
    /// <summary>
    /// 角色ID
    /// </summary>
    [Required(ErrorMessage = "角色ID不能为空")]
    public string RoleId { get; set; } = string.Empty;

    /// <summary>
    /// 仓库权限列表
    /// </summary>
    public List<WarehousePermissionDto> WarehousePermissions { get; set; } = new();
}

/// <summary>
/// 仓库权限DTO
/// </summary>
public class WarehousePermissionDto
{
    /// <summary>
    /// 仓库ID
    /// </summary>
    public string WarehouseId { get; set; } = string.Empty;

    /// <summary>
    /// 是否只读权限
    /// </summary>
    public bool IsReadOnly { get; set; } = false;

    /// <summary>
    /// 是否有写入权限
    /// </summary>
    public bool IsWrite { get; set; } = false;

    /// <summary>
    /// 是否有删除权限
    /// </summary>
    public bool IsDelete { get; set; } = false;
}

/// <summary>
/// 仓库权限树节点DTO
/// </summary>
public class WarehousePermissionTreeDto
{
    /// <summary>
    /// 节点ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 节点名称
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 节点类型（organization/warehouse）
    /// </summary>
    public string Type { get; set; } = string.Empty;

    /// <summary>
    /// 是否选中
    /// </summary>
    public bool IsSelected { get; set; } = false;

    /// <summary>
    /// 权限设置
    /// </summary>
    public WarehousePermissionDto? Permission { get; set; }

    /// <summary>
    /// 子节点
    /// </summary>
    public List<WarehousePermissionTreeDto> Children { get; set; } = new();
}

/// <summary>
/// 用户角色分配DTO
/// </summary>
public class UserRoleDto
{
    /// <summary>
    /// 用户ID
    /// </summary>
    [Required(ErrorMessage = "用户ID不能为空")]
    public string UserId { get; set; } = string.Empty;

    /// <summary>
    /// 角色ID列表
    /// </summary>
    public List<string> RoleIds { get; set; } = new();
}

/// <summary>
/// 角色详情DTO
/// </summary>
public class RoleDetailDto : RoleInfoDto
{
    /// <summary>
    /// 拥有该角色的用户列表
    /// </summary>
    public List<UserInfoDto> Users { get; set; } = new();

    /// <summary>
    /// 仓库权限列表
    /// </summary>
    public List<WarehousePermissionDetailDto> WarehousePermissions { get; set; } = new();
}

/// <summary>
/// 仓库权限详情DTO
/// </summary>
public class WarehousePermissionDetailDto : WarehousePermissionDto
{
    /// <summary>
    /// 组织名称
    /// </summary>
    public string OrganizationName { get; set; } = string.Empty;

    /// <summary>
    /// 仓库名称
    /// </summary>
    public string WarehouseName { get; set; } = string.Empty;

    /// <summary>
    /// 仓库描述
    /// </summary>
    public string WarehouseDescription { get; set; } = string.Empty;
} 