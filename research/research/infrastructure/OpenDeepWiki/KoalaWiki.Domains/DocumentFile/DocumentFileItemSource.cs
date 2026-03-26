namespace KoalaWiki.Domains.DocumentFile;

public class DocumentFileItemSource : Entity<string>
{
    public string DocumentFileItemId { get; set; } = string.Empty;
    
    /// <summary>
    /// 源文件地址
    /// </summary>
    public string Address { get; set; } = string.Empty;
    
    /// <summary>
    /// 源文件名称
    /// </summary>
    public string? Name { get; set; }
    
    public DocumentFileItem DocumentFileItem { get; set; } = null!;
}