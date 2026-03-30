namespace KoalaWiki.KoalaWarehouse;

public class DocumentContext
{
    private static readonly AsyncLocal<DocumentHolder> _documentHolder = new();

    public static DocumentStore? DocumentStore
    {
        get => _documentHolder.Value?.DocumentStore;
        set
        {
            _documentHolder.Value ??= new DocumentHolder();

            _documentHolder.Value.DocumentStore = value;
        }
    }


    private class DocumentHolder
    {
        public DocumentStore DocumentStore { get; set; } = new();
    }
}

public class DocumentStore
{

    public List<GitIssusItem> GitIssus { get; set; } = new();
}

public class GitIssusItem
{
    public string Title { get; set; }

    public string Url { get; set; }

    public string Content { get; set; }

    public DateTime? CreatedAt { get; set; }

    public string Author { get; set; }
    
    public string UrlHtml { get; set; }

    public string State { get; set; }

    public string Number { get; set; }
}