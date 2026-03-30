using System;

namespace KoalaWiki.Domains;

public class DocumentCommitRecord : Entity<string>
{
    public string WarehouseId { get; set; } = string.Empty;

    public string CommitId { get; set; } = string.Empty;

    public string CommitMessage { get; set; } = string.Empty;
    
    public string Title { get; set; } = string.Empty;

    public string Author { get; set; } = string.Empty;

    public DateTime LastUpdate { get; set; } = DateTime.Now;
}