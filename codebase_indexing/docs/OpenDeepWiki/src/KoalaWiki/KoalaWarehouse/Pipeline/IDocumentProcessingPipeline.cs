namespace KoalaWiki.KoalaWarehouse.Pipeline;

public interface IDocumentProcessingPipeline
{
    Task<DocumentProcessingResult> ExecuteAsync(
        DocumentProcessingCommand command, 
        CancellationToken cancellationToken = default);
}

public interface IDocumentProcessingOrchestrator
{
    Task<DocumentProcessingResult> ProcessDocumentAsync(
        Document document,
        Warehouse warehouse,
        IKoalaWikiContext dbContext,
        string gitRepository,
        CancellationToken cancellationToken = default);
}