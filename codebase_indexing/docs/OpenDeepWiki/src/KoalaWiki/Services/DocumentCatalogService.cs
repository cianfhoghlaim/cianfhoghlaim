using FastService;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains;
using KoalaWiki.Entities;
using LibGit2Sharp;
using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations;
using KoalaWiki.Domains.DocumentFile;
using KoalaWiki.Domains.Warehouse;

namespace KoalaWiki.Services;

[Tags("文档目录")]
[Route("/api/DocumentCatalog")]
public class DocumentCatalogService(IKoalaWikiContext dbAccess) : FastApi
{
    /// <summary>
    /// 获取目录列表
    /// </summary>
    /// <param name="organizationName"></param>
    /// <param name="name"></param>
    /// <param name="branch"></param>
    /// <param name="languageCode">语言代码，可选</param>
    /// <returns></returns>
    /// <exception cref="NotFoundException"></exception>
    public async Task<object> GetDocumentCatalogsAsync(string organizationName, string name, string? branch,
        string? languageCode = null)
    {
        var warehouse = await dbAccess.Warehouses
            .AsNoTracking()
            .Where(x => x.Name == name && x.OrganizationName == organizationName &&
                        (string.IsNullOrEmpty(branch) || x.Branch == branch) &&
                        (x.Status == WarehouseStatus.Completed || x.Status == WarehouseStatus.Processing))
            .FirstOrDefaultAsync();

        // 如果没有找到仓库，返回空列表
        if (warehouse == null)
        {
            throw new NotFoundException($"仓库不存在，请检查仓库名称和组织名称:{organizationName} {name}");
        }

        var document = await dbAccess.Documents
            .AsNoTracking()
            .Where(x => x.WarehouseId.ToLower() == warehouse.Id.ToLower())
            .FirstOrDefaultAsync();

        var documentCatalogs = await dbAccess.DocumentCatalogs
            .Where(x => x.WarehouseId.ToLower() == warehouse.Id.ToLower() && x.IsDeleted == false)
            .Include(x => x.I18nTranslations)
            .ToListAsync();

        var branchs =
            (await dbAccess.Warehouses
                .Where(x => x.Name == name && x.OrganizationName == organizationName && x.Type == "git" &&
                            (x.Status == WarehouseStatus.Completed  || x.Status == WarehouseStatus.Processing))
                .OrderByDescending(x => x.Status == WarehouseStatus.Completed)
                .Select(x => x.Branch)
                .ToArrayAsync());

        int progress;
        if (documentCatalogs.Count == 0)
        {
            progress = 0;
        }
        else
        {
            progress = documentCatalogs.Count(x => x.IsCompleted) * 100 / documentCatalogs.Count;
        }

        // 检查仓库是否支持i18n
        var supportedLanguages = await GetWarehouseSupportedLanguagesAsync(warehouse.Id);
        var hasI18nSupport = supportedLanguages.Count > 0;

        return new
        {
            items = BuildDocumentTree(documentCatalogs, languageCode),
            lastUpdate = document?.LastUpdate,
            document?.Description,
            progress = progress,
            git = warehouse.Address,
            branchs = branchs,
            document?.WarehouseId,
            document?.LikeCount,
            document?.Status,
            document?.CommentCount,
            supportedLanguages = supportedLanguages,
            hasI18nSupport = hasI18nSupport,
            currentLanguage = languageCode ?? "zh-CN"
        };
    }

    /// <summary>
    /// 根据目录id获取文件
    /// </summary>
    /// <returns></returns>
    public async Task GetDocumentByIdAsync(string owner, string name, string? branch,
        string path, string? languageCode, HttpContext httpContext)
    {
        // URL解码，处理包含特殊字符（如日文字符）的路径
        var decodedPath = System.Web.HttpUtility.UrlDecode(path);
        
        // 先根据仓库名称和组织名称找到仓库
        var warehouse = await dbAccess.Warehouses
            .AsNoTracking()
            .Where(x => x.Name == name && x.OrganizationName == owner &&
                        (string.IsNullOrEmpty(branch) || x.Branch == branch) &&
                        (x.Status == WarehouseStatus.Completed || x.Status == WarehouseStatus.Processing))
            .FirstOrDefaultAsync();

        if (warehouse == null)
        {
            throw new NotFoundException($"仓库不存在，请检查仓库名称和组织名称:{owner} {name}");
        }

        // 找到catalog
        var id = await dbAccess.DocumentCatalogs
            .AsNoTracking()
            .Where(x => x.WarehouseId == warehouse.Id && x.Url == decodedPath && x.IsDeleted == false)
            .Select(x => x.Id)
            .FirstOrDefaultAsync();

        var document = await dbAccess.Documents
            .AsNoTracking()
            .Where(x => x.WarehouseId.ToLower() == warehouse.Id.ToLower())
            .FirstOrDefaultAsync();

        var item = await dbAccess.DocumentFileItems
            .AsNoTracking()
            .Where(x => x.DocumentCatalogId == id)
            .Include(x => x.I18nTranslations)
            .FirstOrDefaultAsync();

        if (item == null)
        {
            throw new NotFoundException("文档内容为空，可能是生成失败或者还没生成成功");
        }

        // 找到所有引用文件
        var fileSource = await dbAccess.DocumentFileItemSources.Where(x => x.DocumentFileItemId == item.Id)
            .ToListAsync();

        // 获取多语言内容
        var localizedTitle = GetLocalizedTitle(item, languageCode);
        var localizedContent = GetLocalizedContent(item, languageCode);
        var localizedDescription = GetLocalizedFileDescription(item, languageCode);

        // 处理fileSource中地址可能是绝对路径
        foreach (var source in fileSource)
        {
            source.Name = source.Name.Replace(document?.GitPath, string.Empty);
            source.Address = source.Address.Replace(document?.GitPath, string.Empty);
        }

        //md
        await httpContext.Response.WriteAsJsonAsync(new
        {
            content = localizedContent,
            title = localizedTitle,
            description = localizedDescription,
            fileSource = fileSource.Select(x => ToFileSource(x, warehouse)),
            address = warehouse?.Address.Replace(".git", string.Empty),
            warehouse?.Branch,
            lastUpdate = item.CreatedAt,
            documentCatalogId = id,
            currentLanguage = languageCode ?? "zh-CN"
        });
    }

    private object ToFileSource(DocumentFileItemSource fileItemSource, Warehouse? warehouse)
    {
        var url = string.Empty;

        if (warehouse != null && !string.IsNullOrEmpty(warehouse.Address))
        {
            if (warehouse.Address.StartsWith("https://github.com") || warehouse.Address.StartsWith("https://gitee.com"))
            {
                // 删除.git后缀
                url = warehouse.Address
                                .Replace(".git", string.Empty)
                                .TrimEnd('/') + $"/tree/{warehouse.Branch}/" + fileItemSource.Address;
            }
            // TODO: 兼容其他提供商
            else if(warehouse.Address.StartsWith("https://gitlab.com"))
            {
                url = warehouse.Address
                                .Replace(".git", string.Empty)
                                .TrimEnd('/') + $"/-/tree/{warehouse.Branch}/" + fileItemSource.Address;
            }
            else
            {
                url = warehouse.Address.TrimEnd('/') + "/" + fileItemSource.Address;
            }
        }
        
        var name = Path.GetFileName(fileItemSource.Address);

        return new
        {
            name = name.TrimStart('/').TrimStart('\\'),
            Address = fileItemSource.Address.TrimStart('/').TrimStart('\\'),
            fileItemSource.CreatedAt,
            url,
            fileItemSource.Id,
            fileItemSource.DocumentFileItemId,
        };
    }

    /// <summary>
    /// 更新目录信息
    /// </summary>
    public async Task<bool> UpdateCatalogAsync([Required] UpdateCatalogRequest request)
    {
        try
        {
            var catalog = await dbAccess.DocumentCatalogs.FindAsync(request.Id);
            if (catalog == null)
            {
                return false;
            }

            catalog.Name = request.Name;
            catalog.Prompt = request.Prompt;

            await dbAccess.SaveChangesAsync();
            return true;
        }
        catch (Exception ex)
        {
            // 记录异常
            Console.WriteLine($"更新目录失败: {ex.Message}");
            return false;
        }
    }

    /// <summary>
    /// 更新文档内容
    /// </summary>
    public async Task<bool> UpdateDocumentContentAsync([Required] UpdateDocumentContentRequest request)
    {
        try
        {
            var item = await dbAccess.DocumentFileItems
                .Where(x => x.DocumentCatalogId == request.Id)
                .FirstOrDefaultAsync();

            if (item == null)
            {
                return false;
            }

            item.Content = request.Content;
            await dbAccess.SaveChangesAsync();
            return true;
        }
        catch (Exception ex)
        {
            // 记录异常
            Console.WriteLine($"更新文档内容失败: {ex.Message}");
            return false;
        }
    }

    /// <summary>
    /// 获取仓库支持的所有语言
    /// </summary>
    /// <param name="warehouseId">仓库ID</param>
    /// <returns>支持的语言代码列表</returns>
    private async Task<List<string>> GetWarehouseSupportedLanguagesAsync(string warehouseId)
    {
        return await dbAccess.DocumentCatalogI18ns
            .AsNoTracking()
            .Join(dbAccess.DocumentCatalogs.AsNoTracking(),
                i18n => i18n.DocumentCatalogId,
                catalog => catalog.Id,
                (i18n, catalog) => new { i18n.LanguageCode, catalog.WarehouseId })
            .Where(x => x.WarehouseId == warehouseId)
            .Select(x => x.LanguageCode)
            .Distinct()
            .ToListAsync();
    }

    /// <summary>
    /// 递归构建文档目录树形结构
    /// </summary>
    /// <param name="documents">所有文档目录列表</param>
    /// <param name="languageCode">语言代码</param>
    /// <returns>树形结构文档目录</returns>
    private List<object> BuildDocumentTree(List<DocumentCatalog> documents, string? languageCode = null)
    {
        var result = new List<object>();

        // 获取顶级目录
        var topLevel = documents.Where(x => x.ParentId == null).OrderBy(x => x.Order).ToList();

        foreach (var item in topLevel)
        {
            var children = GetChildren(item.Id, documents, languageCode);

            // 获取多语言名称和描述
            var displayName = GetLocalizedName(item, languageCode);
            var displayDescription = GetLocalizedDescription(item, languageCode);

            if (children == null || children.Count == 0)
            {
                result.Add(new
                {
                    label = displayName,
                    Url = item.Url,
                    Description = displayDescription,
                    key = item.Id,
                    lastUpdate = item.CreatedAt,
                    // 是否启用
                    disabled = item.IsCompleted == false
                });
            }
            else
            {
                result.Add(new
                {
                    label = displayName,
                    Description = displayDescription,
                    Url = item.Url,
                    key = item.Id,
                    lastUpdate = item.CreatedAt,
                    children,
                    // 是否启用
                    disabled = item.IsCompleted == false
                });
            }
        }

        return result;
    }

    /// <summary>
    /// 获取本地化名称
    /// </summary>
    /// <param name="catalog">文档目录</param>
    /// <param name="languageCode">语言代码</param>
    /// <returns>本地化名称</returns>
    private string GetLocalizedName(DocumentCatalog catalog, string? languageCode)
    {
        if (string.IsNullOrEmpty(languageCode) || catalog.I18nTranslations == null)
        {
            return catalog.Name;
        }

        var translation = catalog.I18nTranslations.FirstOrDefault(x => x.LanguageCode == languageCode);
        return translation?.Name ?? catalog.Name;
    }

    /// <summary>
    /// 获取本地化描述
    /// </summary>
    /// <param name="catalog">文档目录</param>
    /// <param name="languageCode">语言代码</param>
    /// <returns>本地化描述</returns>
    private string GetLocalizedDescription(DocumentCatalog catalog, string? languageCode)
    {
        if (string.IsNullOrEmpty(languageCode) || catalog.I18nTranslations == null)
        {
            return catalog.Description;
        }

        var translation = catalog.I18nTranslations.FirstOrDefault(x => x.LanguageCode == languageCode);
        return translation?.Description ?? catalog.Description;
    }

    /// <summary>
    /// 获取本地化文件标题
    /// </summary>
    /// <param name="fileItem">文档文件</param>
    /// <param name="languageCode">语言代码</param>
    /// <returns>本地化标题</returns>
    private string GetLocalizedTitle(DocumentFileItem fileItem, string? languageCode)
    {
        if (string.IsNullOrEmpty(languageCode) || fileItem.I18nTranslations == null)
        {
            return fileItem.Title;
        }

        var translation = fileItem.I18nTranslations.FirstOrDefault(x => x.LanguageCode == languageCode);
        return translation?.Title ?? fileItem.Title;
    }

    /// <summary>
    /// 获取本地化文件内容
    /// </summary>
    /// <param name="fileItem">文档文件</param>
    /// <param name="languageCode">语言代码</param>
    /// <returns>本地化内容</returns>
    private string GetLocalizedContent(DocumentFileItem fileItem, string? languageCode)
    {
        if (string.IsNullOrEmpty(languageCode) || fileItem.I18nTranslations == null)
        {
            return fileItem.Content;
        }

        var translation = fileItem.I18nTranslations.FirstOrDefault(x => x.LanguageCode == languageCode);
        return translation?.Content ?? fileItem.Content;
    }

    /// <summary>
    /// 获取本地化文件描述
    /// </summary>
    /// <param name="fileItem">文档文件</param>
    /// <param name="languageCode">语言代码</param>
    /// <returns>本地化描述</returns>
    private string GetLocalizedFileDescription(DocumentFileItem fileItem, string? languageCode)
    {
        if (string.IsNullOrEmpty(languageCode) || fileItem.I18nTranslations == null)
        {
            return fileItem.Description;
        }

        var translation = fileItem.I18nTranslations.FirstOrDefault(x => x.LanguageCode == languageCode);
        return translation?.Description ?? fileItem.Description;
    }

    /// <summary>
    /// 递归获取子目录
    /// </summary>
    /// <param name="parentId">父目录ID</param>
    /// <param name="documents">所有文档目录列表</param>
    /// <param name="languageCode">语言代码</param>
    /// <returns>子目录列表</returns>
    private List<object> GetChildren(string parentId, List<DocumentCatalog> documents, string? languageCode = null)
    {
        var children = new List<object>();
        var directChildren = documents.Where(x => x.ParentId == parentId).OrderBy(x => x.Order).ToList();

        foreach (var child in directChildren)
        {
            // 递归获取子目录的子目录
            var subChildren = GetChildren(child.Id, documents, languageCode);

            // 获取多语言名称和描述
            var displayName = GetLocalizedName(child, languageCode);
            var displayDescription = GetLocalizedDescription(child, languageCode);

            if (subChildren == null || subChildren.Count == 0)
            {
                children.Add(new
                {
                    label = displayName,
                    lastUpdate = child.CreatedAt,
                    Url = child.Url,
                    key = child.Id,
                    Description = displayDescription,
                    // 是否启用
                    disabled = child.IsCompleted == false
                });
            }
            else
            {
                children.Add(new
                {
                    label = displayName,
                    key = child.Id,
                    Url = child.Url,
                    Description = displayDescription,
                    lastUpdate = child.CreatedAt,
                    children = subChildren,
                    // 是否启用
                    disabled = child.IsCompleted == false
                });
            }
        }

        return children;
    }
}

/// <summary>
/// 更新目录请求
/// </summary>
public class UpdateCatalogRequest
{
    /// <summary>
    /// 目录ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 目录名称
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 提示词
    /// </summary>
    public string Prompt { get; set; } = string.Empty;
}

/// <summary>
/// 更新文档内容请求
/// </summary>
public class UpdateDocumentContentRequest
{
    /// <summary>
    /// 文档目录ID
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// 文档内容
    /// </summary>
    public string Content { get; set; } = string.Empty;
}