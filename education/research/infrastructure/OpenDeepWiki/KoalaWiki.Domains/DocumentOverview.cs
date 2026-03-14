using KoalaWiki.Domains;

namespace KoalaWiki.Entities;

public class DocumentOverview : Entity<string>
{
    /// <summary>
    /// 绑定的ID
    /// </summary>
    public string DocumentId { get; set; }

    public string Content { get; set; }

    public string Title { get; set; }
}