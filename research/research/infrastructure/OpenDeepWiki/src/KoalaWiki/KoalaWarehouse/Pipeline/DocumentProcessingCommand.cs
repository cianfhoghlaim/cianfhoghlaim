namespace KoalaWiki.KoalaWarehouse.Pipeline;

public class DocumentProcessingCommand
{
    public Document Document { get; init; } = null!;
    public Warehouse Warehouse { get; init; } = null!;
    public string GitRepository { get; init; } = string.Empty;
    public IKoalaWikiContext DbContext { get; init; } = null!;
}

public class DocumentProcessingResult
{
    public bool Success { get; set; }
    public string? ErrorMessage { get; set; }
    public Exception? Exception { get; set; }
    public DocumentProcessingContext? Context { get; set; }
    
    public static DocumentProcessingResult CreateSuccess(DocumentProcessingContext context)
    {
        return new DocumentProcessingResult
        {
            Success = true,
            Context = context
        };
    }
    
    public static DocumentProcessingResult CreateFailure(string errorMessage, Exception? exception = null)
    {
        return new DocumentProcessingResult
        {
            Success = false,
            ErrorMessage = errorMessage,
            Exception = exception
        };
    }
}