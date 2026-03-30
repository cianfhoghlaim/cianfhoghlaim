using FastService;
using KoalaWiki.Domains.Users;
using KoalaWiki.Dto;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Services
{
    [Tags("用户个人资料管理")]
    [FastService.Route("/api/UserProfile")]
    [Filter(typeof(ResultFilter))]
    [Authorize]
    public class UserProfileService(IKoalaWikiContext koala, IUserContext userContext) : FastApi
    {
        private const long MaxAvatarSize = 5 * 1024 * 1024; // 5MB
        private readonly string[] AllowedImageTypes = { ".jpg", ".jpeg", ".png", ".gif", ".webp" };
        private readonly string AvatarStoragePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "avatars");

        /// <summary>
        /// 获取当前用户个人资料
        /// </summary>
        [HttpGet("/")]
        public async Task<UserProfileOutput> GetProfileAsync()
        {
            var userId = userContext.CurrentUserId ?? throw new Exception("用户未登录");

            var user = await koala.Users
                .AsNoTracking()
                .FirstOrDefaultAsync(x => x.Id == userId);

            if (user == null)
            {
                throw new Exception("用户不存在");
            }

            return MapToOutput(user);
        }

        /// <summary>
        /// 更新用户个人资料
        /// </summary>
        [HttpPut("/")]
        public async Task<UserProfileOutput> UpdateProfileAsync(UpdateProfileInput input)
        {
            var userId = userContext.CurrentUserId ?? throw new Exception("用户未登录");

            var user = await koala.Users
                .FirstOrDefaultAsync(x => x.Id == userId);

            if (user == null)
            {
                throw new Exception("用户不存在");
            }

            // 检查用户名是否已被其他用户使用
            if (!string.IsNullOrWhiteSpace(input.Username) && input.Username != user.Name)
            {
                var existingUser = await koala.Users
                    .AsNoTracking()
                    .FirstOrDefaultAsync(x => x.Name == input.Username && x.Id != userId);

                if (existingUser != null)
                {
                    throw new Exception("用户名已被使用");
                }

                user.Name = input.Username;
            }

            // 检查邮箱是否已被其他用户使用
            if (!string.IsNullOrWhiteSpace(input.Email) && input.Email != user.Email)
            {
                var existingUser = await koala.Users
                    .AsNoTracking()
                    .FirstOrDefaultAsync(x => x.Email == input.Email && x.Id != userId);

                if (existingUser != null)
                {
                    throw new Exception("邮箱已被使用");
                }

                user.Email = input.Email;
            }

            // 更新其他字段
            if (input.Bio != null) user.Bio = input.Bio;
            if (input.Location != null) user.Location = input.Location;
            if (input.Website != null) user.Website = input.Website;
            if (input.Company != null) user.Company = input.Company;

            user.UpdatedAt = DateTime.UtcNow;

            await koala.SaveChangesAsync();

            return MapToOutput(user);
        }

        /// <summary>
        /// 上传用户头像
        /// </summary>
        [HttpPost("/avatar")]
        public async Task<AvatarUploadOutput> UploadAvatarAsync([FromForm] IFormFile avatar)
        {
            var userId = userContext.CurrentUserId ?? throw new Exception("用户未登录");

            if (avatar == null || avatar.Length == 0)
            {
                throw new Exception("请选择要上传的图片");
            }

            // 验证文件大小
            if (avatar.Length > MaxAvatarSize)
            {
                throw new Exception($"图片大小不能超过 {MaxAvatarSize / (1024 * 1024)}MB");
            }

            // 验证文件类型
            var extension = Path.GetExtension(avatar.FileName).ToLowerInvariant();
            if (!AllowedImageTypes.Contains(extension))
            {
                throw new Exception($"不支持的图片格式，请上传 {string.Join(", ", AllowedImageTypes)} 格式的图片");
            }

            var user = await koala.Users
                .FirstOrDefaultAsync(x => x.Id == userId);

            if (user == null)
            {
                throw new Exception("用户不存在");
            }

            // 创建存储目录
            if (!Directory.Exists(AvatarStoragePath))
            {
                Directory.CreateDirectory(AvatarStoragePath);
            }

            // 删除旧头像文件
            if (!string.IsNullOrEmpty(user.Avatar))
            {
                var oldAvatarPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", user.Avatar.TrimStart('/'));
                if (File.Exists(oldAvatarPath))
                {
                    File.Delete(oldAvatarPath);
                }
            }

            // 生成新的文件名
            var fileName = $"{userId}_{DateTime.UtcNow.Ticks}{extension}";
            var filePath = Path.Combine(AvatarStoragePath, fileName);

            // 保存文件
            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await avatar.CopyToAsync(stream);
            }

            // 更新用户头像路径
            user.Avatar = $"/avatars/{fileName}";
            user.UpdatedAt = DateTime.UtcNow;

            await koala.SaveChangesAsync();

            return new AvatarUploadOutput
            {
                AvatarUrl = user.Avatar,
                Message = "头像上传成功"
            };
        }

        /// <summary>
        /// 删除用户头像
        /// </summary>
        [HttpDelete("/avatar")]
        public async Task DeleteAvatarAsync()
        {
            var userId = userContext.CurrentUserId ?? throw new Exception("用户未登录");

            var user = await koala.Users
                .FirstOrDefaultAsync(x => x.Id == userId);

            if (user == null)
            {
                throw new Exception("用户不存在");
            }

            // 删除头像文件
            if (!string.IsNullOrEmpty(user.Avatar))
            {
                var avatarPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", user.Avatar.TrimStart('/'));
                if (File.Exists(avatarPath))
                {
                    File.Delete(avatarPath);
                }
            }

            // 清空用户头像路径
            user.Avatar = string.Empty;
            user.UpdatedAt = DateTime.UtcNow;

            await koala.SaveChangesAsync();
        }

        /// <summary>
        /// 修改密码
        /// </summary>
        [HttpPost("/password")]
        public async Task ChangePasswordAsync(ChangePasswordInput input)
        {
            var userId = userContext.CurrentUserId ?? throw new Exception("用户未登录");

            var user = await koala.Users
                .FirstOrDefaultAsync(x => x.Id == userId);

            if (user == null)
            {
                throw new Exception("用户不存在");
            }

            // 验证旧密码
            if (input.OldPassword != user.Password)
            {
                throw new Exception("旧密码不正确");
            }

            // 更新新密码
            user.Password = input.NewPassword;
            user.UpdatedAt = DateTime.UtcNow;

            await koala.SaveChangesAsync();
        }

        private static UserProfileOutput MapToOutput(User user)
        {
            return new UserProfileOutput
            {
                Id = user.Id,
                Username = user.Name,
                Email = user.Email,
                Avatar = user.Avatar,
                Bio = user.Bio,
                Location = user.Location,
                Website = user.Website,
                Company = user.Company,
                CreatedAt = user.CreatedAt,
                UpdatedAt = user.UpdatedAt,
                LastLoginAt = user.LastLoginAt
            };
        }
    }

// DTO定义
}

namespace KoalaWiki.Dto
{
    public class UserProfileOutput
    {
        public string Id { get; set; } = string.Empty;
        public string Username { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string Avatar { get; set; } = string.Empty;
        public string? Bio { get; set; }
        public string? Location { get; set; }
        public string? Website { get; set; }
        public string? Company { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public DateTime? LastLoginAt { get; set; }
    }

    public class UpdateProfileInput
    {
        public string? Username { get; set; }
        public string? Email { get; set; }
        public string? Bio { get; set; }
        public string? Location { get; set; }
        public string? Website { get; set; }
        public string? Company { get; set; }
    }

    public class AvatarUploadOutput
    {
        public string AvatarUrl { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
    }

    public class ChangePasswordInput
    {
        public string OldPassword { get; set; } = string.Empty;
        public string NewPassword { get; set; } = string.Empty;
    }
}