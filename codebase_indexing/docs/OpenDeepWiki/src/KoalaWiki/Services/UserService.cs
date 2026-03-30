using FastService;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains.Users;
using KoalaWiki.Dto;
using KoalaWiki.Infrastructure;
using Microsoft.EntityFrameworkCore;
using Mapster;
using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;
using Microsoft.AspNetCore.Http;
using System.IO;
using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;

namespace KoalaWiki.Services;

/// <summary>
/// 用户管理服务
/// </summary>
[Tags("用户管理")]
[FastService.Route("/api/user")]
[Filter(typeof(ResultFilter))]
public class UserService(
    IKoalaWikiContext dbContext,
    ILogger<UserService> logger,
    IUserContext userContext) : FastApi
{
    /// <summary>
    /// 获取用户列表
    /// </summary>
    /// <param name="page">页码</param>
    /// <param name="pageSize">每页数量</param>
    /// <param name="keyword">搜索关键词</param>
    /// <returns>用户列表</returns>
    [Authorize(Roles = "admin")]
    [EndpointSummary("获取用户列表")]
    [HttpGet("UserList")]
    public async Task<PageDto<UserInfoDto>> GetUserListAsync(int page, int pageSize, string? keyword)
    {
        var query = dbContext.Users.AsNoTracking();

        // 如果有关键词，则按名称或邮箱搜索
        if (!string.IsNullOrWhiteSpace(keyword))
        {
            query = query.Where(u => u.Name.Contains(keyword) || u.Email.Contains(keyword));
        }

        // 按创建时间降序排序
        query = query.OrderByDescending(u => u.CreatedAt);

        // 计算总数
        var total = await query.CountAsync();

        // 获取分页数据
        var users = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        // 获取用户ID列表
        var userIds = users.Select(u => u.Id).ToList();

        // 批量获取所有用户的角色信息
        var userRoles = await (from ur in dbContext.UserInRoles
                              join r in dbContext.Roles on ur.RoleId equals r.Id
                              where userIds.Contains(ur.UserId)
                              select new { ur.UserId, RoleName = r.Name })
                              .ToListAsync();

        // 按用户ID分组角色
        var userRoleDict = userRoles
            .GroupBy(ur => ur.UserId)
            .ToDictionary(g => g.Key, g => string.Join(',', g.Select(x => x.RoleName)));

        // 将实体映射为DTO并分配角色
        var userDtos = users.Select(u =>
        {
            var userDto = u.Adapt<UserInfoDto>();
            userDto.Role = userRoleDict.GetValueOrDefault(u.Id, string.Empty);
            return userDto;
        }).ToList();

        return new PageDto<UserInfoDto>(total, userDtos);
    }

    /// <summary>
    /// 获取用户详情
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <returns>用户详情</returns>
    [Authorize(Roles = "admin")]
    [EndpointSummary("获取用户详情")]
    [HttpGet("User")]
    public async Task<ResultDto<UserInfoDto>> GetUserAsync(string id)
    {
        var user = await dbContext.Users
            .AsNoTracking()
            .FirstOrDefaultAsync(u => u.Id == id);

        if (user == null)
        {
            return ResultDto<UserInfoDto>.Error("用户不存在");
        }

        // 将实体映射为DTO
        var userDto = user.Adapt<UserInfoDto>();

        // 获取用户角色
        var roleIds = await dbContext.UserInRoles
            .Where(ur => ur.UserId == id)
            .Select(ur => ur.RoleId)
            .ToListAsync();

        var roles = await dbContext.Roles
            .Where(r => roleIds.Contains(r.Id))
            .Select(r => r.Name)
            .ToListAsync();

        userDto.Role = string.Join(',', roles);

        return ResultDto<UserInfoDto>.Success(userDto);
    }

    /// <summary>
    /// 获取当前用户信息
    /// </summary>
    /// <returns>当前用户信息</returns>
    [Authorize]
    [EndpointSummary("获取当前用户信息")]
    [HttpGet("profile")]
    public async Task<ResultDto<UserInfoDto>> GetCurrentUserAsync()
    {
        var userId = userContext.CurrentUserId;
        if (string.IsNullOrEmpty(userId))
        {
            return ResultDto<UserInfoDto>.Error("用户未登录");
        }

        var user = await dbContext.Users
            .AsNoTracking()
            .FirstOrDefaultAsync(u => u.Id == userId);

        if (user == null)
        {
            throw new UnauthorizedAccessException();
        }

        // 将实体映射为DTO
        var userDto = user.Adapt<UserInfoDto>();

        var roleIds = await dbContext.UserInRoles
            .Where(ur => ur.UserId == userId)
            .Select(ur => ur.RoleId)
            .ToListAsync();

        var roles = await dbContext.Roles
            .Where(r => roleIds.Contains(r.Id))
            .Select(r => r.Name)
            .ToListAsync();

        userDto.Role = string.Join(',', roles);
        return ResultDto<UserInfoDto>.Success(userDto);
    }

    /// <summary>
    /// 更新当前用户资料
    /// </summary>
    /// <param name="updateProfileDto">用户资料信息</param>
    /// <returns>更新结果</returns>
    [Authorize]
    [EndpointSummary("更新用户资料")]
    [HttpPut("profile")]
    public async Task<ResultDto<UserInfoDto>> UpdateProfileAsync(UpdateProfileDto updateProfileDto)
    {
        try
        {
            var userId = userContext.CurrentUserId;
            if (string.IsNullOrEmpty(userId))
            {
                return ResultDto<UserInfoDto>.Error("用户未登录");
            }

            var existingUser = await dbContext.Users.FindAsync(userId);
            if (existingUser == null)
            {
                throw new UnauthorizedAccessException();
            }

            // 如果修改了用户名，检查是否已存在
            if (existingUser.Name != updateProfileDto.Name)
            {
                var existingUsername =
                    await dbContext.Users.AnyAsync(u => u.Name == updateProfileDto.Name && u.Id != userId);
                if (existingUsername)
                {
                    return ResultDto<UserInfoDto>.Error("用户名已存在");
                }
            }

            // 如果修改了邮箱，检查是否已存在
            if (existingUser.Email != updateProfileDto.Email)
            {
                var existingEmail =
                    await dbContext.Users.AnyAsync(u => u.Email == updateProfileDto.Email && u.Id != userId);
                if (existingEmail)
                {
                    return ResultDto<UserInfoDto>.Error("邮箱已被注册");
                }
            }

            // 更新用户信息
            existingUser.Name = updateProfileDto.Name;
            existingUser.Email = updateProfileDto.Email;
            existingUser.UpdatedAt = DateTime.UtcNow;
            existingUser.Avatar = updateProfileDto.Avatar;

            // 保存更改
            dbContext.Users.Update(existingUser);
            await dbContext.SaveChangesAsync();

            // 将实体映射为DTO
            var userDto = existingUser.Adapt<UserInfoDto>();

            return ResultDto<UserInfoDto>.Success(userDto);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "更新用户资料失败");
            return ResultDto<UserInfoDto>.Error("更新用户资料失败，请稍后再试");
        }
    }

    /// <summary>
    /// 验证当前密码
    /// </summary>
    /// <param name="verifyPasswordDto">密码验证信息</param>
    /// <returns>验证结果</returns>
    [Authorize]
    [EndpointSummary("验证当前密码")]
    [HttpPost("verify-password")]
    public async Task<ResultDto> VerifyPasswordAsync(VerifyPasswordDto verifyPasswordDto)
    {
        try
        {
            var userId = userContext.CurrentUserId;
            if (string.IsNullOrEmpty(userId))
            {
                return ResultDto<bool>.Error("用户未登录");
            }

            var user = await dbContext.Users
                .AsNoTracking()
                .FirstOrDefaultAsync(u => u.Id == userId);

            if (user == null)
            {
                throw new UnauthorizedAccessException();
            }

            // 这里应该使用密码哈希验证，暂时使用简单比较
            // 在实际项目中，应该使用 BCrypt 或其他安全的密码哈希算法
            var isValid = user.Password == verifyPasswordDto.Password;

            return ResultDto<bool>.Success(isValid);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "验证密码失败");
            return ResultDto<bool>.Error("验证密码失败，请稍后再试");
        }
    }

    /// <summary>
    /// 修改密码
    /// </summary>
    /// <param name="changePasswordDto">修改密码信息</param>
    /// <returns>修改结果</returns>
    [Authorize]
    [EndpointSummary("修改密码")]
    [HttpPut("change-password")]
    public async Task<ResultDto> ChangePasswordAsync(ChangePasswordDto changePasswordDto)
    {
        try
        {
            var userId = userContext.CurrentUserId;
            if (string.IsNullOrEmpty(userId))
            {
                return ResultDto<bool>.Error("用户未登录");
            }

            var existingUser = await dbContext.Users.FindAsync(userId);
            if (existingUser == null)
            {
                return ResultDto<bool>.Error("用户不存在");
            }

            // 验证当前密码
            // 这���应该使用密码哈希验证，暂时使用简单比较
            // 在实际项目中，应该使用 BCrypt 或其他安全的密码哈希算法
            if (existingUser.Password != changePasswordDto.CurrentPassword)
            {
                return ResultDto<bool>.Error("当前密码不正确");
            }

            // 更新密码
            existingUser.Password = changePasswordDto.NewPassword;
            existingUser.UpdatedAt = DateTime.UtcNow;

            // 保存更改
            dbContext.Users.Update(existingUser);
            await dbContext.SaveChangesAsync();

            return ResultDto<bool>.Success(true);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "修改密码失败");
            return ResultDto<bool>.Error("修改密码失败，请稍后再试");
        }
    }

    /// <summary>
    /// 上传头像
    /// </summary>
    /// <param name="context">HTTP上下文</param>
    /// <returns>头像URL</returns>
    [Authorize]
    [EndpointSummary("上传头像")]
    [HttpPost("upload-avatar")]
    public async Task<ResultDto<string>> UploadAvatarAsync(HttpContext context)
    {
        try
        {
            var userId = userContext.CurrentUserId;
            if (string.IsNullOrEmpty(userId))
            {
                return ResultDto<string>.Error("用户未登录");
            }

            var file = context.Request.Form.Files.FirstOrDefault();

            // 验证文件
            if (file == null || file.Length == 0)
            {
                return ResultDto<string>.Error("请选择要上传的文件");
            }

            // 验证文件类型
            var allowedExtensions = new[] { ".jpg", ".jpeg", ".png", ".gif" };
            var fileExtension = Path.GetExtension(file.FileName).ToLowerInvariant();
            if (!allowedExtensions.Contains(fileExtension))
            {
                return ResultDto<string>.Error("只支持 JPG、PNG、GIF 格式的图片");
            }

            // 验证文件大小（限制为2MB）
            if (file.Length > 2 * 1024 * 1024)
            {
                return ResultDto<string>.Error("文件大小不能超过 2MB");
            }

            // 创建头像目录
            var avatarsPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "api", "avatars");
            if (!Directory.Exists(avatarsPath))
            {
                Directory.CreateDirectory(avatarsPath);
            }

            // 生成唯一文件名
            var fileName = $"{userId}_{DateTime.Now:yyyyMMddHHmmss}{fileExtension}";
            var filePath = Path.Combine(avatarsPath, fileName);

            // 如果用户已有头像，删除旧文件
            var existingUser = await dbContext.Users.FindAsync(userId);
            if (existingUser != null && !string.IsNullOrEmpty(existingUser.Avatar))
            {
                var oldAvatarPath = existingUser.Avatar;

                if (oldAvatarPath.StartsWith("/api/avatars/"))
                {
                    var oldFilePath = new FileInfo(Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "api",
                        oldAvatarPath.TrimStart('/')));

                    // 判断文件地址是否在 avatars目录下
                    if (oldFilePath.DirectoryName != avatarsPath)
                    {
                        logger.LogWarning("尝试删除非头像目录下的文件: {FilePath}", oldFilePath.FullName);
                    }
                    else
                    {
                        if (oldFilePath.Exists)
                        {
                            oldFilePath.Delete();
                        }
                    }
                }
            }

            // 保存文件
            await using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }

            // 返回相对URL路径
            var avatarUrl = $"/api/avatars/{fileName}";

            return ResultDto<string>.Success(avatarUrl);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "上传头像失败");
            return ResultDto<string>.Error("上传头像失败，请稍后再试");
        }
    }

    /// <summary>
    /// 创建用户
    /// </summary>
    /// <param name="createUserDto">用户信息</param>
    /// <returns>创建结果</returns>
    [Authorize(Roles = "admin")]
    [EndpointSummary("创建用户")]
    [HttpPost("CreateUser")]
    public async Task<ResultDto<UserInfoDto>> CreateUserAsync(CreateUserDto createUserDto)
    {
        try
        {
            // 检查用户名是否已存在
            var existingUsername = await dbContext.Users.AnyAsync(u => u.Name == createUserDto.Name);
            if (existingUsername)
            {
                return ResultDto<UserInfoDto>.Error("用户名已存在");
            }

            // 检查邮箱是否已存在
            var existingEmail = await dbContext.Users.AnyAsync(u => u.Email == createUserDto.Email);
            if (existingEmail)
            {
                return ResultDto<UserInfoDto>.Error("邮箱已被注册");
            }

            // 将DTO映射为实体
            var user = new User
            {
                Id = Guid.NewGuid().ToString("N"),
                Name = createUserDto.Name,
                Email = createUserDto.Email,
                Password = createUserDto.Password,
                Avatar = createUserDto.Avatar ?? string.Empty,
                CreatedAt = DateTime.UtcNow
            };

            // 获取普通角色
            var userRole = await dbContext.Roles
                .AsNoTracking()
                .FirstOrDefaultAsync(r => r.Name == "user");

            await dbContext.UserInRoles.AddAsync(new UserInRole()
            {
                RoleId = userRole.Id,
                UserId = user.Id
            });

            // 保存用户
            await dbContext.Users.AddAsync(user);
            await dbContext.SaveChangesAsync();

            // 将实体映射为DTO
            var userDto = user.Adapt<UserInfoDto>();

            return ResultDto<UserInfoDto>.Success(userDto);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "创建用户失败");
            return ResultDto<UserInfoDto>.Error("创建用户失败，请稍后再试");
        }
    }

    /// <summary>
    /// 更新用户
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <param name="updateUserDto">用户信息</param>
    /// <returns>更新结果</returns>
    [Authorize(Roles = "admin")]
    [EndpointSummary("更新用户")]
    [HttpPost("UpdateUser")]
    public async Task<ResultDto<UserInfoDto>> UpdateUserAsync(string id, UpdateUserDto updateUserDto)
    {
        try
        {
            var existingUser = await dbContext.Users.FindAsync(id);
            if (existingUser == null)
            {
                return ResultDto<UserInfoDto>.Error("用户不存在");
            }

            // 如果修改了用户名，检查是否已存在
            if (existingUser.Name != updateUserDto.Name)
            {
                var existingUsername = await dbContext.Users.AnyAsync(u => u.Name == updateUserDto.Name && u.Id != id);
                if (existingUsername)
                {
                    return ResultDto<UserInfoDto>.Error("用户名已存在");
                }
            }

            // 如果修改了邮箱，检查是否已存在
            if (existingUser.Email != updateUserDto.Email)
            {
                var existingEmail = await dbContext.Users.AnyAsync(u => u.Email == updateUserDto.Email && u.Id != id);
                if (existingEmail)
                {
                    return ResultDto<UserInfoDto>.Error("邮箱已被注册");
                }
            }

            // 更新用户信息
            existingUser.Name = updateUserDto.Name;
            existingUser.Email = updateUserDto.Email;
            existingUser.Avatar = updateUserDto.Avatar ?? existingUser.Avatar;
            existingUser.UpdatedAt = DateTime.UtcNow;

            // 如果提供了新密码，则更新密码
            if (!string.IsNullOrEmpty(updateUserDto.Password))
            {
                existingUser.Password = updateUserDto.Password;
            }

            // 保存更改
            dbContext.Users.Update(existingUser);
            await dbContext.SaveChangesAsync();

            // 将实体映射为DTO
            var userDto = existingUser.Adapt<UserInfoDto>();

            return ResultDto<UserInfoDto>.Success(userDto);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "更新用户失败");
            return ResultDto<UserInfoDto>.Error("更新用户失败，请稍后再试");
        }
    }

    /// <summary>
    /// 删除用户
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <returns>删除结果</returns>
    [Authorize(Roles = "admin")]
    [EndpointSummary("删除用户")]
    [HttpPost("DeleteUser")]
    public async Task<ResultDto> DeleteUserAsync(string id)
    {
        try
        {
            var user = await dbContext.Users.FindAsync(id);
            if (user == null)
            {
                return ResultDto.Error("用户不存在");
            }

            // 删除用户角色关联
            var userRoles = await dbContext.UserInRoles.Where(ur => ur.UserId == id).ToListAsync();
            if (userRoles.Any())
            {
                dbContext.UserInRoles.RemoveRange(userRoles);
            }

            // 删除用户
            dbContext.Users.Remove(user);
            await dbContext.SaveChangesAsync();

            return ResultDto.Success(true);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "删除用户失败");
            return ResultDto.Error("删除用户失败，请稍后再试");
        }
    }

    /// <summary>
    /// 重置用户密码
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <param name="resetPasswordDto">重置密码信息</param>
    /// <returns>重置结果</returns>
    [Authorize(Roles = "admin")]
    [EndpointSummary("重置用户密码")]
    [HttpPost("ResetPassword")]
    public async Task<ResultDto> ResetUserPasswordAsync(string id, ResetPasswordDto resetPasswordDto)
    {
        try
        {
            var user = await dbContext.Users.FindAsync(id);
            if (user == null)
            {
                return ResultDto.Error("用户不存在");
            }

            // 更新密码
            user.Password = resetPasswordDto.NewPassword;
            user.UpdatedAt = DateTime.UtcNow;

            dbContext.Users.Update(user);
            await dbContext.SaveChangesAsync();

            logger.LogInformation("管理员重置用户密码成功: UserId={UserId}, AdminId={AdminId}", id, userContext.CurrentUserId);

            return ResultDto.Success(true);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "重置用户密码失败");
            return ResultDto.Error("重置用户密码失败，请稍后再试");
        }
    }

    /// <summary>
    /// 为用户分配角色
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <param name="assignRoleDto">角色分配信息</param>
    /// <returns>分配结果</returns>
    [Authorize(Roles = "admin")]
    [EndpointSummary("为用户分配角色")]
    [HttpPost("AssignRoles")]
    public async Task<ResultDto> AssignUserRolesAsync(string id, AssignUserRoleDto assignRoleDto)
    {
        try
        {
            var user = await dbContext.Users.FindAsync(id);
            if (user == null)
            {
                return ResultDto.Error("用户不存在");
            }

            // 验证角色是否存在
            var existingRoles = await dbContext.Roles
                .Where(r => assignRoleDto.RoleIds.Contains(r.Id))
                .Select(r => r.Id)
                .ToListAsync();

            if (existingRoles.Count != assignRoleDto.RoleIds.Count)
            {
                return ResultDto.Error("部分角色不存在");
            }

            // 删除现有角色分配
            var currentUserRoles = await dbContext.UserInRoles.Where(ur => ur.UserId == id).ToListAsync();
            dbContext.UserInRoles.RemoveRange(currentUserRoles);

            // 添加新的角色分配
            var newUserRoles = assignRoleDto.RoleIds.Select(roleId => new UserInRole
            {
                UserId = id,
                RoleId = roleId
            }).ToList();

            await dbContext.UserInRoles.AddRangeAsync(newUserRoles);
            await dbContext.SaveChangesAsync();

            logger.LogInformation("为用户分配角色成功: UserId={UserId}, RoleIds={RoleIds}, AdminId={AdminId}",
                id, string.Join(",", assignRoleDto.RoleIds), userContext.CurrentUserId);

            return ResultDto.Success(true);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "为用户分配角色失败");
            return ResultDto.Error("为用户分配角色失败，请稍后再试");
        }
    }

    /// <summary>
    /// 获取用户角色
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <returns>用户角色列表</returns>
    [Authorize(Roles = "admin")]
    [EndpointSummary("获取用户角色")]
    [HttpGet("UserRoles")]
    public async Task<ResultDto<List<string>>> GetUserRolesAsync(string id)
    {
        try
        {
            var user = await dbContext.Users.AsNoTracking().FirstOrDefaultAsync(u => u.Id == id);
            if (user == null)
            {
                return ResultDto<List<string>>.Error("用户不存在");
            }

            var roleIds = await dbContext.UserInRoles
                .Where(ur => ur.UserId == id)
                .Select(ur => ur.RoleId)
                .ToListAsync();

            return ResultDto<List<string>>.Success(roleIds);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "获取用户角色失败");
            return ResultDto<List<string>>.Error("获取用户角色失败，请稍后再试");
        }
    }

    /// <summary>
    /// 批量删除用户
    /// </summary>
    /// <param name="batchDeleteDto">批量删除信息</param>
    /// <returns>删除结果</returns>
    [Authorize(Roles = "admin")]
    [EndpointSummary("批量删除用户")]
    [HttpPost("BatchDelete")]
    public async Task<ResultDto> BatchDeleteUsersAsync(BatchDeleteUserDto batchDeleteDto)
    {
        try
        {
            var users = await dbContext.Users.Where(u => batchDeleteDto.UserIds.Contains(u.Id)).ToListAsync();
            if (users.Count != batchDeleteDto.UserIds.Count)
            {
                return ResultDto.Error("部分用户不存在");
            }

            // 检查是否尝试删除当前用户
            if (batchDeleteDto.UserIds.Contains(userContext.CurrentUserId))
            {
                return ResultDto.Error("不能删除当前登录用户");
            }

            // 删除用户角色关联
            var userRoles = await dbContext.UserInRoles.Where(ur => batchDeleteDto.UserIds.Contains(ur.UserId)).ToListAsync();
            if (userRoles.Any())
            {
                dbContext.UserInRoles.RemoveRange(userRoles);
            }

            // 删除用户
            dbContext.Users.RemoveRange(users);
            await dbContext.SaveChangesAsync();

            logger.LogInformation("批量删除用户成功: UserIds={UserIds}, AdminId={AdminId}",
                string.Join(",", batchDeleteDto.UserIds), userContext.CurrentUserId);

            return ResultDto.Success(true);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "批量删除用户失败");
            return ResultDto.Error("批量删除用户失败，请稍后再试");
        }
    }
}