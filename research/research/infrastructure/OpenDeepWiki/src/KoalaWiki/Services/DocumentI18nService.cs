using FastService;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains.DocumentFile;
using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations;

namespace KoalaWiki.Services;

[Tags("文档多语言")]
[Route("/api/DocumentI18n")]
public class DocumentI18nService(IKoalaWikiContext dbAccess) : FastApi
{
    /// <summary>
    /// 获取文档目录的多语言数据
    /// </summary>
    /// <param name="catalogId">目录ID</param>
    /// <param name="languageCode">语言代码</param>
    /// <returns></returns>
    public async Task<DocumentCatalogI18n> GetCatalogI18nAsync(string catalogId, string languageCode)
    {
        return await dbAccess.DocumentCatalogI18ns
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.DocumentCatalogId == catalogId && x.LanguageCode == languageCode);
    }

    /// <summary>
    /// 获取文档目录支持的所有语言
    /// </summary>
    /// <param name="catalogId">目录ID</param>
    /// <returns></returns>
    public async Task<List<string>> GetCatalogSupportedLanguagesAsync(string catalogId)
    {
        return await dbAccess.DocumentCatalogI18ns
            .AsNoTracking()
            .Where(x => x.DocumentCatalogId == catalogId)
            .Select(x => x.LanguageCode)
            .Distinct()
            .ToListAsync();
    }

    /// <summary>
    /// 获取文档文件的多语言数据
    /// </summary>
    /// <param name="fileItemId">文件ID</param>
    /// <param name="languageCode">语言代码</param>
    /// <returns></returns>
    public async Task<DocumentFileItemI18n> GetFileItemI18nAsync(string fileItemId, string languageCode)
    {
        return await dbAccess.DocumentFileItemI18ns
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.DocumentFileItemId == fileItemId && x.LanguageCode == languageCode);
    }

    /// <summary>
    /// 获取文档文件支持的所有语言
    /// </summary>
    /// <param name="fileItemId">文件ID</param>
    /// <returns></returns>
    public async Task<List<string>> GetFileItemSupportedLanguagesAsync(string fileItemId)
    {
        return await dbAccess.DocumentFileItemI18ns
            .AsNoTracking()
            .Where(x => x.DocumentFileItemId == fileItemId)
            .Select(x => x.LanguageCode)
            .Distinct()
            .ToListAsync();
    }
}