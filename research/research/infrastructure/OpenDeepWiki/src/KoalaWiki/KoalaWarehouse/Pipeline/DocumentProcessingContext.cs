
using KoalaWiki.Domains.DocumentFile;

namespace KoalaWiki.KoalaWarehouse.Pipeline;

public class DocumentProcessingContext
{
    public Document Document { get; init; } = null!;
    public Warehouse Warehouse { get; init; } = null!;
    public string GitRepository { get; init; } = string.Empty;
    public IKoalaWikiContext DbContext { get; init; } = null!;
    
    // 步骤间共享的数据
    public string? Readme { get; set; }
    public string? Catalogue { get; set; }
    public ClassifyType? Classification { get; set; }
    public string? Overview { get; set; }
    public List<DocumentCatalog>? DocumentCatalogs { get; set; }
    
    // 元数据和配置
    public Dictionary<string, object> Metadata { get; init; } = new();
    public Dictionary<string, object> StepResults { get; init; } = new();
    
    // 内核实例（重用原有逻辑）
    public Kernel? KernelInstance { get; set; }
    public Kernel? FileKernelInstance { get; set; }
    
    // 辅助方法
    public void SetStepResult<T>(string stepName, T result)
    {
        StepResults[stepName] = result!;
    }
    
    public T? GetStepResult<T>(string stepName)
    {
        if (StepResults.TryGetValue(stepName, out var result) && result is T typedResult)
        {
            return typedResult;
        }
        return default;
    }
    
    public void SetMetadata(string key, object value)
    {
        Metadata[key] = value;
    }
    
    public T? GetMetadata<T>(string key)
    {
        if (Metadata.TryGetValue(key, out var value) && value is T typedValue)
        {
            return typedValue;
        }
        return default;
    }
}