namespace KoalaWiki.Dto;

public class CreateCatalogInput
{
    /// <summary>
    /// 目录名称
    /// </summary>
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// 路由
    /// </summary>
    public string Url { get; set; } = string.Empty;

    /// <summary>
    /// 目录描述
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// 目录父级Id
    /// </summary>
    /// <returns></returns>
    public string? ParentId { get; set; } = string.Empty;
    
    /// <summary>
    /// 当前目录排序
    /// </summary>
    public int Order { get; set; } = 0;
    
    /// <summary>
    /// 文档id
    /// </summary>
    public string DucumentId { get; set; } = string.Empty;
    
    public string WarehouseId { get; set; } = string.Empty;
    
    public string Prompt { get; set; } = string.Empty;
    
    public List<string> DependentFile { get; set; } = new();
}