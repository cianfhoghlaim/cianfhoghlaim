namespace KoalaWiki.Extensions;

public static class CatalogueExtensions
{
    /// <summary>
    /// 获取智能过滤的优化树形目录结构
    /// </summary>
    /// <param name="document"></param>
    /// <param name="format">输出格式</param>
    /// <returns>优化后的目录结构</returns>
    public static string GetCatalogueSmartFilterOptimized(this Document document,
        string format = "compact")
    {
        var path = document.GitPath;

        var ignoreFiles = DocumentsHelper.GetIgnoreFiles(path);
        var pathInfos = new List<PathInfo>();

        // 递归扫描目录所有文件和目录
        DocumentsHelper.ScanDirectory(path, pathInfos, ignoreFiles);

        var fileTree = FileTreeBuilder.BuildTree(pathInfos, path);
        return format.ToLower() switch
        {
            "json" => FileTreeBuilder.ToCompactJson(fileTree),
            "pathlist" => string.Join("\n", FileTreeBuilder.ToPathList(fileTree)),
            "compact" or _ => FileTreeBuilder.ToCompactString(fileTree)
        };
    }
}