using System.Text;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Entities;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Extensions;

public static class SitemapExtensions
{
    private const string UrlTemplate =
        "<url><loc>{0}</loc><changefreq>{1}</changefreq><priority>{2}</priority></url>";

    private static async Task ExecuteAsync(this IKoalaWikiContext koala, HttpContext context)
    {
        // 先获取所有的仓库
        var warehouses = await koala.Warehouses
            .AsNoTracking()
            .Where(x => x.Status == WarehouseStatus.Completed)
            .ToListAsync();

        // 获取上面仓库的所有catalogs
        var catalogs = await koala.DocumentCatalogs
            .AsNoTracking()
            .Where(x => warehouses.Select(w => w.Id).Contains(x.WarehouseId))
            .ToListAsync();

        var sb = new StringBuilder();
        foreach (var catalogUrl in from catalog in catalogs let warehouse = warehouses
                     .FirstOrDefault(x => x.Id == catalog.WarehouseId) select string.Format(UrlTemplate,
                     $"https://{context.Request.Host}/{warehouse?.OrganizationName}/{warehouse?.Name}/{catalog.Url}",
                     "weekly",
                     "0.5"))
        {
            sb.Append(catalogUrl);
        }

        await context.Response.WriteAsync(
            $"""
             <?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">{sb}</urlset>
             """);
    }

    public static IEndpointRouteBuilder MapSitemap(this IEndpointRouteBuilder app)
    {
        app.MapGet("/sitemap.xml", ExecuteAsync);
        app.MapGet("/api/sitemap.xml", ExecuteAsync);

        return app;
    }
}