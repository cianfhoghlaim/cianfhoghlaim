using FastService;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace KoalaWiki.Services
{
    [Tags("文件存储管理")]
    [FastService.Route("/api/FileStorage")]
    [Filter(typeof(ResultFilter))]
    [Authorize]
    public class FileStorageService(IUserContext userContext) : FastApi
    {
        private const long MaxImageSize = 10 * 1024 * 1024; // 10MB
        private readonly string[] AllowedImageTypes = { ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp" };
        private readonly string ImageStoragePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "uploads", "images");

        /// <summary>
        /// 上传图片文件（仅管理员可用）
        /// </summary>
        [HttpPost("/image")]
        public async Task<ImageUploadOutput> UploadImageAsync([FromForm] IFormFile file)
        {
            // 验证用户权限 - 仅管理员可以上传
            if (!userContext.IsAdmin)
            {
                throw new Exception("权限不足，仅管理员可以上传图片");
            }

            if (file == null || file.Length == 0)
            {
                throw new Exception("请选择要上传的图片");
            }

            // 验证文件大小
            if (file.Length > MaxImageSize)
            {
                throw new Exception($"图片大小不能超过 {MaxImageSize / (1024 * 1024)}MB");
            }

            // 验证文件类型
            var extension = Path.GetExtension(file.FileName).ToLowerInvariant();
            if (!AllowedImageTypes.Contains(extension))
            {
                throw new Exception($"不支持的图片格式，请上传 {string.Join(", ", AllowedImageTypes)} 格式的图片");
            }

            try
            {
                // 创建存储目录结构（按年月组织）
                var dateFolder = DateTime.UtcNow.ToString("yyyy-MM");
                var storagePath = Path.Combine(ImageStoragePath, dateFolder);

                if (!Directory.Exists(storagePath))
                {
                    Directory.CreateDirectory(storagePath);
                }

                // 生成唯一的文件名
                var fileName = $"{Guid.NewGuid()}{extension}";
                var filePath = Path.Combine(storagePath, fileName);

                // 保存文件
                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    await file.CopyToAsync(stream);
                }

                // 返回文件URL路径
                var imageUrl = $"/uploads/images/{dateFolder}/{fileName}";

                return new ImageUploadOutput
                {
                    Url = imageUrl,
                    FileName = fileName,
                    OriginalName = file.FileName,
                    Size = file.Length,
                    Message = "图片上传成功"
                };
            }
            catch (Exception ex)
            {
                throw new Exception($"图片上传失败: {ex.Message}");
            }
        }

        /// <summary>
        /// 批量上传图片（仅管理员可用）
        /// </summary>
        [HttpPost("/images")]
        public async Task<BatchImageUploadOutput> UploadImagesAsync([FromForm] List<IFormFile> files)
        {
            // 验证用户权限 - 仅管理员可以上传
            if (!userContext.IsAdmin)
            {
                throw new Exception("权限不足，仅管理员可以上传图片");
            }

            if (files == null || files.Count == 0)
            {
                throw new Exception("请选择要上传的图片");
            }

            var uploadedImages = new List<ImageInfo>();
            var errors = new List<string>();

            foreach (var file in files)
            {
                try
                {
                    // 验证文件大小
                    if (file.Length > MaxImageSize)
                    {
                        errors.Add($"{file.FileName}: 图片大小超过限制");
                        continue;
                    }

                    // 验证文件类型
                    var extension = Path.GetExtension(file.FileName).ToLowerInvariant();
                    if (!AllowedImageTypes.Contains(extension))
                    {
                        errors.Add($"{file.FileName}: 不支持的图片格式");
                        continue;
                    }

                    // 创建存储目录
                    var dateFolder = DateTime.UtcNow.ToString("yyyy-MM");
                    var storagePath = Path.Combine(ImageStoragePath, dateFolder);

                    if (!Directory.Exists(storagePath))
                    {
                        Directory.CreateDirectory(storagePath);
                    }

                    // 生成文件名并保存
                    var fileName = $"{Guid.NewGuid()}{extension}";
                    var filePath = Path.Combine(storagePath, fileName);

                    using (var stream = new FileStream(filePath, FileMode.Create))
                    {
                        await file.CopyToAsync(stream);
                    }

                    var imageUrl = $"/uploads/images/{dateFolder}/{fileName}";

                    uploadedImages.Add(new ImageInfo
                    {
                        Url = imageUrl,
                        FileName = fileName,
                        OriginalName = file.FileName,
                        Size = file.Length
                    });
                }
                catch (Exception ex)
                {
                    errors.Add($"{file.FileName}: {ex.Message}");
                }
            }

            return new BatchImageUploadOutput
            {
                Images = uploadedImages,
                Errors = errors,
                SuccessCount = uploadedImages.Count,
                ErrorCount = errors.Count,
                Message = $"成功上传 {uploadedImages.Count} 张图片"
            };
        }

        /// <summary>
        /// 删除图片（仅管理员可用）
        /// </summary>
        [HttpDelete("/image")]
        public async Task DeleteImageAsync(string imageUrl)
        {
            // 验证用户权限 - 仅管理员可以删除
            if (!userContext.IsAdmin)
            {
                throw new Exception("权限不足，仅管理员可以删除图片");
            }

            if (string.IsNullOrWhiteSpace(imageUrl))
            {
                throw new Exception("图片URL不能为空");
            }

            try
            {
                // 转换URL为文件路径
                var relativePath = imageUrl.TrimStart('/');
                var filePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", relativePath);

                if (File.Exists(filePath))
                {
                    File.Delete(filePath);
                }
                else
                {
                    throw new Exception("图片文件不存在");
                }
            }
            catch (Exception ex)
            {
                throw new Exception($"删除图片失败: {ex.Message}");
            }

            await Task.CompletedTask;
        }
    }

    // DTO定义
    public class ImageUploadOutput
    {
        public string Url { get; set; } = string.Empty;
        public string FileName { get; set; } = string.Empty;
        public string OriginalName { get; set; } = string.Empty;
        public long Size { get; set; }
        public string Message { get; set; } = string.Empty;
    }

    public class BatchImageUploadOutput
    {
        public List<ImageInfo> Images { get; set; } = new();
        public List<string> Errors { get; set; } = new();
        public int SuccessCount { get; set; }
        public int ErrorCount { get; set; }
        public string Message { get; set; } = string.Empty;
    }

    public class ImageInfo
    {
        public string Url { get; set; } = string.Empty;
        public string FileName { get; set; } = string.Empty;
        public string OriginalName { get; set; } = string.Empty;
        public long Size { get; set; }
    }
}