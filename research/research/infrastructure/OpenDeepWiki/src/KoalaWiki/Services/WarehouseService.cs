using System.IO.Compression;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Web;
using FastService;
using KoalaWiki.Core;
using KoalaWiki.Domains.DocumentFile;
using KoalaWiki.Dto;
using KoalaWiki.Functions;
using KoalaWiki.Tools;
using LibGit2Sharp;
using MapsterMapper;
using Microsoft.AspNetCore.Authorization;
using Microsoft.Extensions.Caching.Memory;

namespace KoalaWiki.Services;

[Tags("仓库管理")]
[Route("/api/Warehouse")]
public class WarehouseService(
    IKoalaWikiContext koala,
    IMapper mapper,
    IUserContext userContext,
    IHttpContextAccessor httpContextAccessor,
    IMemoryCache memoryCache)
    : FastApi
{
    /// <summary>
    /// 检查用户对指定仓库的访问权限
    /// </summary>
    /// <param name="warehouseId">仓库ID</param>
    /// <returns>是否有访问权限</returns>
    private async Task<bool> CheckWarehouseAccessAsync(string warehouseId)
    {
        var currentUserId = userContext.CurrentUserId;
        var isAdmin = httpContextAccessor.HttpContext?.User?.IsInRole("admin") ?? false;

        // 管理员有所有权限
        if (isAdmin) return true;

        // 检查仓库是否存在权限分配
        var hasPermissionAssignment = await koala.WarehouseInRoles
            .AnyAsync(wr => wr.WarehouseId == warehouseId);

        // 如果仓库没有权限分配，则是公共仓库，所有人都可以访问
        if (!hasPermissionAssignment) return true;

        // 如果用户未登录，无法访问有权限分配的仓库
        if (string.IsNullOrEmpty(currentUserId)) return false;

        // 获取用户的角色ID列表
        var userRoleIds = await koala.UserInRoles
            .Where(ur => ur.UserId == currentUserId)
            .Select(ur => ur.RoleId)
            .ToListAsync();

        // 如果用户没有任何角色，无法访问有权限分配的仓库
        if (!userRoleIds.Any()) return false;

        // 检查用户角色是否有该仓库的权限
        return await koala.WarehouseInRoles
            .AnyAsync(wr => userRoleIds.Contains(wr.RoleId) && wr.WarehouseId == warehouseId);
    }

    /// <summary>
    /// 检查用户对指定仓库的管理权限
    /// </summary>
    /// <param name="warehouseId">仓库ID</param>
    /// <returns>是否有管理权限</returns>
    private async Task<bool> CheckWarehouseManageAccessAsync(string warehouseId)
    {
        var currentUserId = userContext.CurrentUserId;
        var isAdmin = httpContextAccessor.HttpContext?.User?.IsInRole("admin") ?? false;

        // 管理员有所有权限
        if (isAdmin) return true;

        // 如果用户未登录，无管理权限
        if (string.IsNullOrEmpty(currentUserId)) return false;

        // 检查仓库是否存在权限分配
        var hasPermissionAssignment = await koala.WarehouseInRoles
            .AnyAsync(wr => wr.WarehouseId == warehouseId);

        // 如果仓库没有权限分配，只有管理员可以管理
        if (!hasPermissionAssignment) return false;

        // 获取用户的角色ID列表
        var userRoleIds = await koala.UserInRoles
            .Where(ur => ur.UserId == currentUserId)
            .Select(ur => ur.RoleId)
            .ToListAsync();

        // 如果用户没有任何角色，无管理权限
        if (!userRoleIds.Any()) return false;

        // 检查用户角色是否有该仓库的写入或删除权限（管理权限）
        return await koala.WarehouseInRoles
            .AnyAsync(wr => userRoleIds.Contains(wr.RoleId) &&
                            wr.WarehouseId == warehouseId &&
                            (wr.IsWrite || wr.IsDelete));
    }

    /// <summary>
    /// 更新仓库状态，并且重新提交
    /// </summary>
    [EndpointSummary("更新仓库状态")]
    public async Task UpdateWarehouseStatusAsync(string warehouseId)
    {
        // 检查管理权限
        if (!await CheckWarehouseManageAccessAsync(warehouseId))
        {
            throw new UnauthorizedAccessException("您没有权限管理此仓库");
        }

        await koala.Warehouses
            .Where(x => x.Id == warehouseId)
            .ExecuteUpdateAsync(x => x.SetProperty(y => y.Status, WarehouseStatus.Pending));
    }

    /// <summary>
    /// 查询上次提交的仓库
    /// </summary>
    /// <returns></returns>
    [EndpointSummary("查询上次提交的仓库")]
    public async Task<object> GetLastWarehouseAsync(string address)
    {
        address = address.Trim().TrimEnd('/').ToLower();

        // 判断是否.git结束，如果不是需要添加
        if (!address.EndsWith(".git"))
        {
            address += ".git";
        }

        var query = await koala.Warehouses
            .AsNoTracking()
            .Where(x => x.Address.ToLower() == address)
            .FirstOrDefaultAsync();

        // 如果没有找到仓库，返回空列表
        if (query == null)
        {
            throw new NotFoundException("仓库不存在");
        }

        return new
        {
            query.Name,
            query.Address,
            query.Description,
            query.Version,
            query.Status,
            query.Error
        };
    }

    public async Task<DocumentCommitRecord?> GetChangeLogAsync(string owner, string name)
    {
        owner = owner.Trim().ToLower();
        name = name.Trim().ToLower();
        var warehouse = await koala.Warehouses
            .AsNoTracking()
            .Where(x => x.Name.ToLower() == name && x.OrganizationName.ToLower() == owner &&
                        (x.Status == WarehouseStatus.Completed || x.Status == WarehouseStatus.Processing))
            .FirstOrDefaultAsync();

        // 如果没有找到仓库，返回空列表
        if (warehouse == null)
        {
            throw new NotFoundException($"仓库不存在，请检查仓库名称和组织名称:{owner} {name}");
        }

        var commit = await koala.DocumentCommitRecords.Where(x => x.WarehouseId == warehouse.Id)
            .ToListAsync();

        var value = new StringBuilder();

        foreach (var record in commit)
        {
            // 拼接一个更新模板
            value.AppendLine($"## {record.LastUpdate:yyyy-MM-dd HH:mm:ss} {record.Title}");
            value.AppendLine($" {record.CommitMessage}");
        }

        return new DocumentCommitRecord()
        {
            CommitId = "",
            CommitMessage = value.ToString(),
            CreatedAt = DateTime.Now,
            Title = "更新日志",
            LastUpdate = DateTime.Now,
            WarehouseId = warehouse.Id,
        };
    }

    /// <summary>
    /// 从URL下载文件到本地
    /// </summary>
    [EndpointSummary("从URL下载文件到本地")]
    [Authorize]
    private async Task<FileInfo> DownloadFileFromUrlAsync(string fileUrl, string organization, string repositoryName)
    {
        using var httpClient = new HttpClient();
        httpClient.Timeout = TimeSpan.FromMinutes(10); // 设置10分钟超时

        try
        {
            // 发送GET请求下载文件
            var response = await httpClient.GetAsync(fileUrl);

            if (!response.IsSuccessStatusCode)
            {
                throw new Exception($"下载文件失败，HTTP状态码: {response.StatusCode}");
            }

            // 优先从响应头中提取文件名
            string fileName = string.Empty;
            if (response.Content.Headers.ContentDisposition != null &&
                !string.IsNullOrEmpty(response.Content.Headers.ContentDisposition.FileName))
            {
                fileName = response.Content.Headers.ContentDisposition.FileName.Trim('"');
            }
            else if (response.Content.Headers.TryGetValues("Content-Disposition", out var values))
            {
                // 兼容部分服务器未标准化ContentDisposition解析
                var disposition = values.FirstOrDefault();
                if (!string.IsNullOrEmpty(disposition))
                {
                    // 优先处理 filename*（RFC 5987）
                    var fileNameStarMarker = "filename*=";
                    var idxStar = disposition.IndexOf(fileNameStarMarker, StringComparison.OrdinalIgnoreCase);
                    if (idxStar >= 0)
                    {
                        var value = disposition.Substring(idxStar + fileNameStarMarker.Length).Trim('"', '\'', ' ');
                        // 处理形如 utf-8''filename.zip
                        var parts = value.Split("''", 2);
                        if (parts.Length == 2)
                        {
                            fileName = parts[1];
                        }
                        else
                        {
                            fileName = value;
                        }
                    }
                    else
                    {
                        var fileNameMarker = "filename=";
                        var idx = disposition.IndexOf(fileNameMarker, StringComparison.OrdinalIgnoreCase);
                        if (idx >= 0)
                        {
                            fileName = disposition.Substring(idx + fileNameMarker.Length).Trim('"', '\'', ' ');
                        }
                    }
                }
            }

            // 如果响应头没有文件名，则从URL中提取
            if (string.IsNullOrEmpty(fileName))
            {
                var uri = new Uri(fileUrl);
                fileName = Path.GetFileName(uri.LocalPath);
            }

            string suffix;

            if (string.IsNullOrEmpty(fileName) || !fileName.Contains('.'))
            {
                // 如果无法从文件名提取后缀，尝试从URL路径推断
                if (fileUrl.Contains("/archive/") && fileUrl.Contains(".zip"))
                {
                    suffix = "zip";
                }
                else if (fileUrl.Contains(".tar.gz"))
                {
                    suffix = "gz";
                }
                else if (fileUrl.Contains(".tar"))
                {
                    suffix = "tar";
                }
                else
                {
                    suffix = "zip"; // 默认使用zip格式
                }
            }
            else
            {
                suffix = fileName.Split('.').Last().ToLower();

                // 验证文件格式
                if (!new[] { "zip", "gz", "tar", "br" }.Contains(suffix))
                {
                    throw new Exception($"不支持的文件格式: {suffix}，只支持zip、gz、tar、br格式");
                }
            }

            var fileInfo = new FileInfo(Path.Combine(Constant.GitPath, organization, repositoryName + "." + suffix));

            if (fileInfo.Directory?.Exists == false)
            {
                fileInfo.Directory.Create();
            }

            // 下载并保存文件
            await using var fileStream = new FileStream(fileInfo.FullName, FileMode.Create);
            await response.Content.CopyToAsync(fileStream);

            return fileInfo;
        }
        catch (HttpRequestException ex)
        {
            throw new Exception($"下载文件时发生网络错误: {ex.Message}");
        }
        catch (TaskCanceledException)
        {
            throw new Exception("下载文件超时，请检查网络连接或尝试更小的文件");
        }
    }

    /// <summary>
    /// 上传并且提交仓库
    /// </summary>
    [EndpointSummary("上传并且提交仓库")]
    [Authorize]
    public async Task UploadAndSubmitWarehouseAsync(HttpContext context)
    {
        if (!DocumentOptions.EnableWarehouseCommit)
        {
            throw new Exception("抱歉，管理员暂时关闭了提交新仓库权限，如果您有需求请联系微信：wk28u9123456789");
        }

        if (!DocumentOptions.EnableFileCommit)
        {
            throw new Exception("抱歉，管理员暂时关闭了提交新仓库权限，如果您有需求请联系微信：wk28u9123456789");
        }

        var organization = context.Request.Form["organization"].ToString();
        var repositoryName = context.Request.Form["repositoryName"].ToString();

        if (string.IsNullOrEmpty(organization) || string.IsNullOrEmpty(repositoryName))
        {
            throw new Exception("组织名称和仓库名称不能为空");
        }

        // URL decode parameters
        var decodedOrganization = HttpUtility.UrlDecode(organization);
        var decodedRepositoryName = HttpUtility.UrlDecode(repositoryName); // 检查是否是URL下载方式

        var fileUrl = context.Request.Form["fileUrl"].ToString();

        FileInfo fileInfo;

        if (!string.IsNullOrEmpty(fileUrl))
        {
            // 从URL下载文件
            fileInfo = await DownloadFileFromUrlAsync(fileUrl, organization, repositoryName);
        }
        else
        {
            // 获取上传的文件
            var file = context.Request.Form.Files["file"];
            if (file == null)
            {
                context.Response.StatusCode = 400;
                throw new Exception("没有文件上传");
            }

            // 只支持压缩包.zip 或gzip 
            if (!file.FileName.EndsWith(".zip") && !file.FileName.EndsWith(".gz") && !file.FileName.EndsWith(".tar") &&
                !file.FileName.EndsWith(".br"))
            {
                context.Response.StatusCode = 400;
                throw new Exception("只支持zip，gz，tar，br格式的文件");
            }

            // 后缀名
            var suffix = file.FileName.Split('.').Last();

            fileInfo = new FileInfo(Path.Combine(Constant.GitPath, organization, repositoryName + "." + suffix));

            if (fileInfo.Directory?.Exists == false)
            {
                fileInfo.Directory.Create();
            }

            await using (var stream = new FileStream(fileInfo.FullName, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }
        }

        var name = fileInfo.FullName.Replace(".zip", "")
            .Replace(".gz", "")
            .Replace(".tar", "")
            .Replace(".br", "");
        // 解压文件，根据后缀名判断解压方式
        if (fileInfo.FullName.EndsWith(".zip"))
        {
            // 解压
            var zipPath = fileInfo.FullName.Replace(".zip", "");
            ZipFile.ExtractToDirectory(fileInfo.FullName, zipPath, true);
        }
        else if (fileInfo.FullName.EndsWith(".gz"))
        {
            await using var inputStream = new FileStream(fileInfo.FullName, FileMode.Open);
            await using var outputStream = new FileStream(name, FileMode.Create);
            await using var decompressionStream = new GZipStream(inputStream, CompressionMode.Decompress);
            await decompressionStream.CopyToAsync(outputStream);
        }
        else if (fileInfo.FullName.EndsWith(".tar"))
        {
            await using var inputStream = new FileStream(fileInfo.FullName, FileMode.Open);
            await using var outputStream = new FileStream(name, FileMode.Create);
            await using var decompressionStream = new GZipStream(inputStream, CompressionMode.Decompress);
            await decompressionStream.CopyToAsync(outputStream);
        }
        else if (fileInfo.FullName.EndsWith(".br"))
        {
            await using var inputStream = new FileStream(fileInfo.FullName, FileMode.Open);
            await using var outputStream = new FileStream(name, FileMode.Create);
            await using var decompressionStream = new BrotliStream(inputStream, CompressionMode.Decompress);
            await decompressionStream.CopyToAsync(outputStream);
        }


        // 如果解压以后目录下只有一个文件夹，那么就将这个文件夹的内容移动到上级目录
        var directory = new DirectoryInfo(name);
        if (directory.Exists)
        {
            var directories = directory.GetDirectories();
            if (directories.Length == 1)
            {
                var subDirectory = directories[0];
                foreach (var fileInfo1 in subDirectory.GetFiles())
                {
                    fileInfo1.MoveTo(Path.Combine(directory.FullName, fileInfo1.Name));
                }

                foreach (var directoryInfo in subDirectory.GetDirectories())
                {
                    directoryInfo.MoveTo(Path.Combine(directory.FullName, directoryInfo.Name));
                }

                subDirectory.Delete(true);
            }
        }

        var value = await koala.Warehouses.FirstOrDefaultAsync(x =>
            x.OrganizationName == decodedOrganization && x.Name == decodedRepositoryName);
        // 判断这个仓库是否已经添加
        if (value?.Status is WarehouseStatus.Completed)
        {
            throw new Exception("该名称渠道已存在且处于完成状态，不可重复创建");
        }
        else if (value?.Status is WarehouseStatus.Pending)
        {
            throw new Exception("该名称渠道已存在且处于待处理状态，请等待处理完成");
        }
        else if (value?.Status is WarehouseStatus.Processing)
        {
            throw new Exception("该名称渠道已存在且正在处理中，请稍后再试");
        }

        // 删除旧的仓库
        var oldWarehouse = await koala.Warehouses
            .Where(x => x.OrganizationName == decodedOrganization && x.Name == decodedRepositoryName)
            .ExecuteDeleteAsync();

        var entity = new Warehouse
        {
            OrganizationName = decodedOrganization,
            Name = decodedRepositoryName,
            Address = name,
            Description = string.Empty,
            Version = string.Empty,
            Error = string.Empty,
            Branch = "main",
            Type = "file",
            CreatedAt = DateTime.UtcNow,
            Id = Guid.NewGuid().ToString(),
            UserId = userContext.CurrentUserId,
            Stars = 0,
            Forks = 0
        };

        await koala.Warehouses.AddAsync(entity);

        await koala.SaveChangesAsync();

        await context.Response.WriteAsJsonAsync(new
        {
            code = 200,
            message = "提交成功"
        });
    }

    /// <summary>
    /// 提交仓库
    /// </summary>
    [EndpointSummary("提交仓库")]
    [Authorize]
    public async Task SubmitWarehouseAsync(WarehouseInput input, HttpContext context)
    {
        if (!DocumentOptions.EnableWarehouseCommit)
        {
            throw new Exception("抱歉，管理员暂时关闭了提交新仓库权限，如果您有需求请联系微信：wk28u9123456789");
        }

        try
        {
            input.Address = input.Address.TrimEnd('/');

            if (!input.Address.EndsWith(".git"))
            {
                input.Address += ".git";
            }

            var (localPath, organization) = GitService.GetRepositoryPath(input.Address);

            organization = organization.Trim().ToLower();

            var names = input.Address.Split('/');

            var repositoryName = names[^1].Replace(".git", "").ToLower();

            // URL decode parameters
            var decodedOrganization = HttpUtility.UrlDecode(organization);
            var decodedRepositoryName = HttpUtility.UrlDecode(repositoryName);

            var value = await koala.Warehouses.FirstOrDefaultAsync(x =>
                x.OrganizationName.ToLower() == decodedOrganization.ToLower() &&
                x.Name.ToLower() == decodedRepositoryName.ToLower() &&
                x.Branch == input.Branch &&
                x.Status == WarehouseStatus.Completed);

            // 判断这个仓库是否已经添加
            if (value?.Status is WarehouseStatus.Completed)
            {
                throw new Exception("该名称渠道已存在且处于完成状态，不可重复创建");
            }
            else if (value?.Status is WarehouseStatus.Pending)
            {
                throw new Exception("该名称渠道已存在且处于待处理状态，请等待处理完成");
            }
            else if (value?.Status is WarehouseStatus.Processing)
            {
                throw new Exception("该名称渠道已存在且正在处理中，请稍后再试");
            }
            else if (!string.IsNullOrEmpty(input.Branch))
            {
                var branch = await koala.Warehouses
                    .AsNoTracking()
                    .Where(x => x.Branch.ToLower() == input.Branch.ToLower() &&
                                x.OrganizationName.ToLower() == decodedOrganization.ToLower() &&
                                x.Name.ToLower() == decodedRepositoryName.ToLower())
                    .FirstOrDefaultAsync();

                if (branch is
                    {
                        Status: WarehouseStatus.Completed or WarehouseStatus.Processing or WarehouseStatus.Pending
                    })
                {
                    throw new Exception("该分支已经存在");
                }
            }

            // 删除旧的仓库
            var oldWarehouse = await koala.Warehouses
                .Where(x => x.OrganizationName == decodedOrganization &&
                            x.Name == decodedRepositoryName && x.Branch == input.Branch)
                .ExecuteDeleteAsync();

            var entity = mapper.Map<Warehouse>(input);
            entity.Name = decodedRepositoryName;
            entity.OrganizationName = decodedOrganization;
            entity.Description = string.Empty;
            entity.Version = string.Empty;
            entity.Error = string.Empty;
            entity.Branch = input.Branch;
            entity.Type = "git";
            entity.CreatedAt = DateTime.UtcNow;
            entity.UserId = userContext.CurrentUserId;
            entity.Id = Guid.NewGuid().ToString();
            entity.Stars = 0;
            entity.Forks = 0;
            await koala.Warehouses.AddAsync(entity);

            await koala.SaveChangesAsync();

            await context.Response.WriteAsJsonAsync(new
            {
                code = 200,
                message = "提交成功"
            });
        }
        catch (Exception e)
        {
            await context.Response.WriteAsJsonAsync(new
            {
                code = 500,
                message = e.Message
            });
        }
    }

    [EndpointSummary("自定义提交仓库")]
    [Authorize]
    public async Task CustomSubmitWarehouseAsync(CustomWarehouseInput input, HttpContext context)
    {
        if (!DocumentOptions.EnableWarehouseCommit)
        {
            throw new Exception("抱歉，管理员暂时关闭了提交新仓库权限，如果您有需求请联系微信：wk28u9123456789");
        }

        try
        {
            input.Organization = input.Organization.Trim().ToLower();

            var repositoryName = input.RepositoryName.Trim().ToLower();

            // URL decode parameters
            var decodedOrganization = HttpUtility.UrlDecode(input.Organization);
            var decodedRepositoryName = HttpUtility.UrlDecode(repositoryName);

            var value = await koala.Warehouses.FirstOrDefaultAsync(x =>
                x.OrganizationName.ToLower() == decodedOrganization.ToLower() &&
                x.Name.ToLower() == decodedRepositoryName.ToLower() &&
                x.Branch == input.Branch &&
                x.Status == WarehouseStatus.Completed);

            // 判断这个仓库是否已经添加
            if (value?.Status is WarehouseStatus.Completed)
            {
                throw new Exception("该名称渠道已存在且处于完成状态，不可重复创建");
            }
            else if (value?.Status is WarehouseStatus.Pending)
            {
                throw new Exception("该名称渠道已存在且处于待处理状态，请等待处理完成");
            }
            else if (value?.Status is WarehouseStatus.Processing)
            {
                throw new Exception("该名称渠道已存在且正在处理中，请稍后再试");
            }
            else if (!string.IsNullOrEmpty(input.Branch))
            {
                var branch = await koala.Warehouses
                    .AsNoTracking()
                    .Where(x => x.Branch == input.Branch && x.OrganizationName == decodedOrganization &&
                                x.Name == decodedRepositoryName)
                    .FirstOrDefaultAsync();

                if (branch is { Status: WarehouseStatus.Completed or WarehouseStatus.Processing })
                {
                    throw new Exception("该分支已经存在");
                }
            }

            // 删除旧的仓库
            var oldWarehouse = await koala.Warehouses
                .Where(x => x.OrganizationName == decodedOrganization &&
                            x.Name == decodedRepositoryName && x.Branch == input.Branch)
                .ExecuteDeleteAsync();

            var entity = mapper.Map<Warehouse>(input);
            entity.Name = decodedRepositoryName;
            entity.OrganizationName = decodedOrganization;
            entity.Description = string.Empty;
            entity.Version = string.Empty;
            entity.Error = string.Empty;
            entity.Branch = input.Branch;
            entity.Type = "git";
            entity.CreatedAt = DateTime.UtcNow;
            entity.Id = Guid.NewGuid().ToString();
            entity.Stars = 0;
            entity.Forks = 0;
            entity.UserId = userContext.CurrentUserId;
            await koala.Warehouses.AddAsync(entity);

            await koala.SaveChangesAsync();

            await context.Response.WriteAsJsonAsync(new
            {
                code = 200,
                message = "提交成功"
            });
        }
        catch (Exception e)
        {
            await context.Response.WriteAsJsonAsync(new
            {
                code = 500,
                message = e.Message
            });
        }
    }


    /// <summary>
    /// 获取知识图谱
    /// </summary>
    /// <returns></returns>
    [EndpointSummary("仓库管理：获取思维导图")]
    [AllowAnonymous]
    public async Task<ResultDto<MiniMapResult>> GetMiniMapAsync(
        string owner,
        string name,
        string? branch = "")
    {
        var warehouse = await koala.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(r => r.OrganizationName == owner && r.Name == name &&
                                      (r.Status == WarehouseStatus.Completed ||
                                       r.Status == WarehouseStatus.Processing) &&
                                      (string.IsNullOrEmpty(branch) || r.Branch == branch));

        var miniMap = await koala.MiniMaps
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.WarehouseId.ToLower() == warehouse.Id.ToLower());

        if (miniMap == null)
        {
            return new ResultDto<MiniMapResult>(200, "没有找到知识图谱", new MiniMapResult());
        }

        var result = JsonSerializer.Deserialize<MiniMapResult>(miniMap.Value, JsonSerializerOptions.Web);

        // 组成点击跳转地址
        var address = warehouse.Address = warehouse.Address.Replace(".git", "").TrimEnd('/').ToLower();

        if (address.Contains("github.com"))
        {
            address += "/tree/" + warehouse.Branch + "/";
        }
        else if (address.Contains("gitee.com"))
        {
            address += "/tree/" + warehouse.Branch + "/";
        }
        else if (address.Contains("gitlab.com") || Regex.IsMatch(address,
                     @"^gitlab\.[\w-]+\.(com|cn|net|org)", RegexOptions.IgnoreCase))
        {
            address += "/-/tree/" + warehouse.Branch + "/";
        }

        // TODO: 需要根据仓库类型判断跳转地址

        foreach (var v in result.Nodes)
        {
            // 使用递归修改v.Url
            void UpdateUrl(MiniMapResult node)
            {
                if (node.Url.StartsWith("http", StringComparison.OrdinalIgnoreCase))
                {
                    // 应该删除前缀
                    node.Url = node.Url.Replace(warehouse.Address, string.Empty, StringComparison.OrdinalIgnoreCase);
                }

                if (node.Url != null && !node.Url.StartsWith("http", StringComparison.OrdinalIgnoreCase))
                {
                    node.Url = address + node.Url.TrimStart('/');
                }

                foreach (var child in node.Nodes)
                {
                    UpdateUrl(child);
                }
            }

            UpdateUrl(v);
        }

        return new ResultDto<MiniMapResult>(200, "获取知识图谱成功", result);
    }


    /// <summary>
    /// 获取用户可访问的仓库ID列表（带缓存）
    /// </summary>
    private async Task<HashSet<string>?> GetAccessibleWarehouseIdsAsync(string? userId, bool isAdmin)
    {
        // 管理员可以访问所有仓库
        if (isAdmin) return null; // null 表示无限制

        // 构建缓存键
        var cacheKey = $"user_accessible_warehouses_{userId ?? "anonymous"}";

        // 尝试从缓存获取
        if (memoryCache.TryGetValue<HashSet<string>>(cacheKey, out var cachedIds))
        {
            return cachedIds;
        }

        var accessibleIds = new HashSet<string>();

        if (string.IsNullOrEmpty(userId))
        {
            // 未登录用户只能访问公共仓库
            var publicIds = await koala.Warehouses
                .Where(w => !koala.WarehouseInRoles.Any(wr => wr.WarehouseId == w.Id))
                .Select(w => w.Id)
                .ToListAsync();

            accessibleIds.UnionWith(publicIds);
        }
        else
        {
            // 使用单个查询获取用户可访问的所有仓库
            var userAccessQuery = from w in koala.Warehouses
                                   let hasRoleAssignment = koala.WarehouseInRoles.Any(wr => wr.WarehouseId == w.Id)
                                   let userHasAccess = koala.UserInRoles
                                       .Where(ur => ur.UserId == userId)
                                       .Join(koala.WarehouseInRoles,
                                           ur => ur.RoleId,
                                           wr => wr.RoleId,
                                           (ur, wr) => wr.WarehouseId)
                                       .Contains(w.Id)
                                   where !hasRoleAssignment || userHasAccess
                                   select w.Id;

            var ids = await userAccessQuery.ToListAsync();
            accessibleIds.UnionWith(ids);
        }

        // 缓存5分钟
        memoryCache.Set(cacheKey, accessibleIds, TimeSpan.FromMinutes(5));
        return accessibleIds;
    }

    /// <summary>
    /// 获取仓库列表的异步方法，支持分页和关键词搜索。
    /// </summary>
    /// <param name="page">当前页码，从1开始。</param>
    /// <param name="pageSize">每页显示的记录数。</param>
    /// <param name="keyword">搜索关键词，用于匹配仓库名称或地址。</param>
    /// <returns>返回一个包含总记录数和当前页仓库数据的分页结果对象。</returns>
    [EndpointSummary("获取仓库列表")]
    public async Task<PageDto<WarehouseDto>> GetWarehouseListAsync(int page, int pageSize, string? keyword)
    {
        // 1. 获取用户权限信息
        var currentUserId = userContext.CurrentUserId;
        var isAdmin = httpContextAccessor.HttpContext?.User?.IsInRole("admin") ?? false;
        var accessibleWarehouseIds = await GetAccessibleWarehouseIdsAsync(currentUserId, isAdmin);

        // 2. 构建基础查询
        var query = koala.Warehouses
            .AsNoTracking()
            .Where(x => x.Status == WarehouseStatus.Completed || x.Status == WarehouseStatus.Processing);

        // 3. 应用权限过滤
        if (accessibleWarehouseIds != null) // null 表示管理员，无需过滤
        {
            query = query.Where(x => accessibleWarehouseIds.Contains(x.Id));
        }

        // 4. 应用关键词搜索
        keyword = keyword?.Trim().ToLower();
        if (!string.IsNullOrWhiteSpace(keyword))
        {
            query = query.Where(x =>
                x.Name.ToLower().Contains(keyword) ||
                x.Address.ToLower().Contains(keyword) ||
                x.Description.ToLower().Contains(keyword));
        }

        // 5. 获取所有符合条件的数据到内存中进行分组
        var allWarehouses = await query
            .OrderByDescending(x => x.IsRecommended)
            .ThenByDescending(x => x.Status == WarehouseStatus.Completed)
            .ThenByDescending(x => x.CreatedAt)
            .ToListAsync();

        // 6. 在内存中进行分组，选择每组中最优先的仓库
        var groupedWarehouses = allWarehouses
            .GroupBy(x => new { x.Name, x.OrganizationName })
            .Select(g => g.OrderByDescending(x => x.IsRecommended)
                .ThenByDescending(x => x.Status == WarehouseStatus.Completed)
                .ThenByDescending(x => x.CreatedAt)
                .First())
            .ToList();

        // 7. 重新排序并进行分页
        var list = groupedWarehouses
            .OrderByDescending(x => x.IsRecommended)
            .ThenByDescending(x => x.Status == WarehouseStatus.Completed)
            .ThenByDescending(x => x.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToList();

        // 8. 获取总数
        var total = groupedWarehouses.Count;

        // 9. 映射到DTO
        var dto = mapper.Map<List<WarehouseDto>>(list);

        // 10. 处理统计信息
        foreach (var repository in dto)
        {
            // 如果有缓存的数据则认为成功
            repository.Success = repository.Stars > 0 || repository.Forks > 0;

            // 清空大字段以减少传输数据量
            repository.OptimizedDirectoryStructure = string.Empty;
            repository.Prompt = string.Empty;
            repository.Readme = string.Empty;
        }

        // 11. 异步更新缺失的统计数据（不阻塞返回）
        var reposNeedingUpdate = dto.Where(x => x.Stars == 0 && x.Forks == 0).ToList();
        if (reposNeedingUpdate.Any())
        {
            _ = Task.Run(async () => await UpdateRepositoryStatsAsync(reposNeedingUpdate));
        }

        return new PageDto<WarehouseDto>(total, dto);
    }

    /// <summary>
    /// 异步更新仓库统计信息
    /// </summary>
    private async Task UpdateRepositoryStatsAsync(List<WarehouseDto> repositories)
    {
        // 批量更新仓库的 stars 和 forks
        var updateTasks = repositories.Select(async repo =>
        {
            try
            {
                // 这里应该调用实际的Git API获取统计
                // 为演示目的，直接返回
                // TODO: 实现实际的API调用逻辑
            }
            catch
            {
                // 静默失败，不影响主流程
            }
        });

        await Task.WhenAll(updateTasks);
    }

    [EndpointSummary("获取指定仓库代码文件")]
    public async Task<ResultDto<string>> GetFileContent(string warehouseId, string path)
    {
        // 检查用户权限
        if (!await CheckWarehouseAccessAsync(warehouseId))
        {
            throw new UnauthorizedAccessException("您没有权限访问此仓库");
        }

        var query = await koala.Documents
            .AsNoTracking()
            .Where(x => x.WarehouseId == warehouseId)
            .FirstOrDefaultAsync();

        if (query == null)
        {
            throw new NotFoundException("文件不存在");
        }

        var fileFunction = new FileTool(query.GitPath, null);

        var result = await fileFunction.ReadFileAsync(path);

        return ResultDto<string>.Success(result);
    }

    /// <summary>
    /// 导出Markdown压缩包
    /// </summary>
    [EndpointSummary("导出Markdown压缩包")]
    [Authorize]
    public async Task ExportMarkdownZip(string warehouseId, HttpContext context)
    {
        // 检查用户权限
        if (!await CheckWarehouseAccessAsync(warehouseId))
        {
            context.Response.StatusCode = 403;
            await context.Response.WriteAsJsonAsync(new
            {
                code = 403,
                message = "您没有权限访问此仓库"
            });
            return;
        }

        var query = await koala.Warehouses
            .AsNoTracking()
            .Where(x => x.Id == warehouseId)
            .FirstOrDefaultAsync();

        if (query == null)
        {
            throw new NotFoundException("文件不存在");
        }

        var fileName = $"{query.Name}.zip";

        // 先获取当前仓库所有目录
        var documents = await koala.Documents
            .AsNoTracking()
            .Where(x => x.WarehouseId == warehouseId)
            .FirstOrDefaultAsync();

        var documentCatalogs = await koala.DocumentCatalogs
            .AsNoTracking()
            .Where(x => x.WarehouseId == warehouseId && x.IsDeleted == false)
            .ToListAsync();

        var catalogsIds = documentCatalogs.Select(x => x.Id).ToList();

        // 获取所有文档条目
        var fileItems = await koala.DocumentFileItems
            .AsNoTracking()
            .Where(x => catalogsIds.Contains(x.DocumentCatalogId))
            .ToListAsync();

        using var memoryStream = new MemoryStream();
        using (var archive = new ZipArchive(memoryStream, ZipArchiveMode.Create, true))
        {
            // 构建目录树结构
            var catalogDict = documentCatalogs.ToDictionary(x => x.Id);
            var rootCatalogs = documentCatalogs.Where(x => string.IsNullOrEmpty(x.ParentId)).ToList();

            // 递归处理目录及其子目录
            await ProcessCatalogs(archive, rootCatalogs, catalogDict, fileItems, "");

            // 递归函数，处理目录及其子目录
            async Task ProcessCatalogs(ZipArchive archive, List<DocumentCatalog> catalogs,
                Dictionary<string, DocumentCatalog> catalogDict,
                List<DocumentFileItem> allFileItems, string currentPath)
            {
                foreach (var catalog in catalogs)
                {
                    var item = allFileItems.FirstOrDefault(x => x.DocumentCatalogId == catalog.Id);

                    // 创建当前目录的路径 - 无论是否有内容都创建目录结构
                    string dirPath = string.IsNullOrEmpty(currentPath)
                        ? catalog.Url.Replace(" ", "_")
                        : Path.Combine(currentPath, catalog.Url.Replace(" ", "_"));

                    // 如果有文档项，处理文档
                    if (item != null)
                    {
                        // 文档路径
                        string entryPath = Path.Combine(dirPath, item.Title.Replace(" ", "_") + ".md");
                    
                        // 创建并写入文档内容
                        var entry = archive.CreateEntry(entryPath.Replace('\\', '/'));
                        await using var writer = new StreamWriter(entry.Open());
                        
                        // 如果内容为空，只写入标题；否则写入标题和内容
                        if (string.IsNullOrEmpty(item.Content))
                        {
                            await writer.WriteAsync($"# {catalog.Name}\n\n");
                        }
                        else
                        {
                            await writer.WriteAsync($"# {catalog.Name}\n\n{item.Content}");
                        }
                    
                        await writer.DisposeAsync();
                    }
                    
                    // 获取并处理子目录 - 无论当前目录是否有内容都处理子目录
                    var children = documentCatalogs.Where(x => x.ParentId == catalog.Id).ToList();
                    if (children.Any())
                    {
                        await ProcessCatalogs(archive, children, catalogDict, allFileItems, catalog.Url);
                    }
                }
            }
        }

        // 将内存流的位置重置到开始
        memoryStream.Position = 0;

        context.Response.ContentType = "application/zip";
        context.Response.Headers["Content-Disposition"] = $"attachment; filename={fileName}";

        // 将zip文件流写入响应
        await memoryStream.CopyToAsync(context.Response.Body);
    }


    /// <summary>
    /// 获取指定组织下仓库的指定文件代码内容
    /// </summary>
    /// <returns></returns>
    [EndpointSummary("获取指定组织下仓库的指定文件代码内容")]
    public async Task<ResultDto<string>> GetFileContentLineAsync(string organizationName, string name, string filePath)
    {
        if (string.IsNullOrEmpty(organizationName) || string.IsNullOrEmpty(name) || string.IsNullOrEmpty(filePath))
        {
            throw new ArgumentException("Organization name, warehouse name and file path cannot be null or empty.");
        }

        // 查找仓库
        var warehouse = await koala.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(x =>
                x.OrganizationName.ToLower() == organizationName.ToLower() &&
                x.Name.ToLower() == name.ToLower());

        if (warehouse == null)
        {
            throw new Exception("Warehouse not found");
        }

        // 查找文档
        var document = await koala.Documents
            .AsNoTracking()
            .Where(x => x.WarehouseId == warehouse.Id)
            .FirstOrDefaultAsync();

        if (document == null)
        {
            throw new Exception("Document not found");
        }

        var fileFunction = new FileTool(document.GitPath, null);

        var value = await fileFunction.ReadFileAsync(filePath);

        return ResultDto<string>.Success(value);
    }

    /// <summary>
    /// 获取Git仓库分支列表
    /// </summary>
    /// <param name="address">仓库地址</param>
    /// <param name="gitUserName">Git用户名（可选）</param>
    /// <param name="gitPassword">Git密码或Token（可选）</param>
    /// <returns>分支列表</returns>
    [EndpointSummary("获取Git仓库分支列表")]
    public async Task<ResultDto<object>> GetBranchListAsync(string address, string? gitUserName = null, string? gitPassword = null)
    {
        try
        {
            address = address.Trim().TrimEnd('/');
            
            // 移除.git后缀用于API调用
            var cleanAddress = address.EndsWith(".git") ? address.Substring(0, address.Length - 4) : address;
            
            var uri = new Uri(cleanAddress);
            var pathSegments = uri.Segments.Where(s => !string.IsNullOrWhiteSpace(s) && s != "/").ToArray();
            
            if (pathSegments.Length < 2)
            {
                return ResultDto<object>.Error("仓库URL格式不正确，至少需要包含组织名和仓库名");
            }
            
            var owner = pathSegments[0].Trim('/');
            var repo = pathSegments[1].Trim('/').Replace(".git", "");
            
            var branches = new List<string>();
            string? defaultBranch = null;
            
            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("User-Agent", "KoalaWiki-App");
            
            // 根据不同的Git平台调用相应的API
            if (uri.Host.Contains("github.com"))
            {
                // GitHub API
                var headers = new Dictionary<string, string>
                {
                    { "Accept", "application/vnd.github.v3+json" }
                };
                
                if (!string.IsNullOrEmpty(gitUserName) && !string.IsNullOrEmpty(gitPassword))
                {
                    var credentials = Convert.ToBase64String(Encoding.UTF8.GetBytes($"{gitUserName}:{gitPassword}"));
                    headers["Authorization"] = $"Basic {credentials}";
                }
                
                foreach (var header in headers)
                {
                    httpClient.DefaultRequestHeaders.Add(header.Key, header.Value);
                }
                
                // 获取仓库信息
                var repoResponse = await httpClient.GetAsync($"https://api.github.com/repos/{owner}/{repo}");
                if (repoResponse.IsSuccessStatusCode)
                {
                    var repoJson = await repoResponse.Content.ReadAsStringAsync();
                    var repoData = JsonSerializer.Deserialize<JsonElement>(repoJson);
                    if (repoData.TryGetProperty("default_branch", out var defaultBranchElement))
                    {
                        defaultBranch = defaultBranchElement.GetString();
                    }
                }
                
                // 获取分支列表
                var branchesResponse = await httpClient.GetAsync($"https://api.github.com/repos/{owner}/{repo}/branches");
                if (branchesResponse.IsSuccessStatusCode)
                {
                    var branchesJson = await branchesResponse.Content.ReadAsStringAsync();
                    var branchesData = JsonSerializer.Deserialize<JsonElement>(branchesJson);
                    if (branchesData.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var branch in branchesData.EnumerateArray())
                        {
                            if (branch.TryGetProperty("name", out var nameElement))
                            {
                                branches.Add(nameElement.GetString() ?? "");
                            }
                        }
                    }
                }
            }
            else if (uri.Host.Contains("gitee.com"))
            {
                // Gitee API
                var repoUrl = $"https://gitee.com/api/v5/repos/{owner}/{repo}";
                var branchesUrl = $"https://gitee.com/api/v5/repos/{owner}/{repo}/branches";
                
                if (!string.IsNullOrEmpty(gitPassword))
                {
                    repoUrl += $"?access_token={gitPassword}";
                    branchesUrl += $"?access_token={gitPassword}";
                }
                
                // 获取仓库信息
                var repoResponse = await httpClient.GetAsync(repoUrl);
                if (repoResponse.IsSuccessStatusCode)
                {
                    var repoJson = await repoResponse.Content.ReadAsStringAsync();
                    var repoData = JsonSerializer.Deserialize<JsonElement>(repoJson);
                    if (repoData.TryGetProperty("default_branch", out var defaultBranchElement))
                    {
                        defaultBranch = defaultBranchElement.GetString();
                    }
                }
                
                // 获取分支列表
                var branchesResponse = await httpClient.GetAsync(branchesUrl);
                if (branchesResponse.IsSuccessStatusCode)
                {
                    var branchesJson = await branchesResponse.Content.ReadAsStringAsync();
                    var branchesData = JsonSerializer.Deserialize<JsonElement>(branchesJson);
                    if (branchesData.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var branch in branchesData.EnumerateArray())
                        {
                            if (branch.TryGetProperty("name", out var nameElement))
                            {
                                branches.Add(nameElement.GetString() ?? "");
                            }
                        }
                    }
                }
            }
            else if (uri.Host.Contains("gitlab"))
            {
                // GitLab API
                var apiBaseUrl = $"{uri.Scheme}://{uri.Host}/api/v4";
                var projectPath = Uri.EscapeDataString($"{owner}/{repo}");
                
                var headers = new Dictionary<string, string>();
                if (!string.IsNullOrEmpty(gitPassword))
                {
                    headers["Authorization"] = $"Bearer {gitPassword}";
                }
                
                foreach (var header in headers)
                {
                    httpClient.DefaultRequestHeaders.Add(header.Key, header.Value);
                }
                
                // 获取项目信息
                var repoResponse = await httpClient.GetAsync($"{apiBaseUrl}/projects/{projectPath}");
                if (repoResponse.IsSuccessStatusCode)
                {
                    var repoJson = await repoResponse.Content.ReadAsStringAsync();
                    var repoData = JsonSerializer.Deserialize<JsonElement>(repoJson);
                    if (repoData.TryGetProperty("default_branch", out var defaultBranchElement))
                    {
                        defaultBranch = defaultBranchElement.GetString();
                    }
                }
                
                // 获取分支列表
                var branchesResponse = await httpClient.GetAsync($"{apiBaseUrl}/projects/{projectPath}/repository/branches");
                if (branchesResponse.IsSuccessStatusCode)
                {
                    var branchesJson = await branchesResponse.Content.ReadAsStringAsync();
                    var branchesData = JsonSerializer.Deserialize<JsonElement>(branchesJson);
                    if (branchesData.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var branch in branchesData.EnumerateArray())
                        {
                            if (branch.TryGetProperty("name", out var nameElement))
                            {
                                branches.Add(nameElement.GetString() ?? "");
                            }
                        }
                    }
                }
            }
            else
            {
                // 不支持的Git平台，返回默认分支
                branches.AddRange(new[] { "main", "master" });
                defaultBranch = "main";
            }
            
            // 如果没有获取到分支，提供默认值
            if (!branches.Any())
            {
                branches.AddRange(new[] { "main", "master" });
                defaultBranch = defaultBranch ?? "main";
            }
            
            // 如果没有默认分支，尝试从分支列表中推断
            if (string.IsNullOrEmpty(defaultBranch) && branches.Any())
            {
                if (branches.Contains("main"))
                {
                    defaultBranch = "main";
                }
                else if (branches.Contains("master"))
                {
                    defaultBranch = "master";
                }
                else
                {
                    defaultBranch = branches.First();
                }
            }
            
            return ResultDto<object>.Success(new
            {
                branches = branches.Distinct().OrderBy(b => b).ToList(),
                defaultBranch = defaultBranch
            });
        }
        catch (Exception ex)
        {
            return ResultDto<object>.Error($"获取分支列表失败: {ex.Message}");
        }
    }
}