using FastService;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains.DocumentFile;
using KoalaWiki.Generate;
using Microsoft.AspNetCore.Mvc;

namespace KoalaWiki.Controllers;

/// <summary>
/// 翻译控制器
/// </summary>
[FastService.Route("api/translation")]
public class TranslationService : FastApi
{
    private readonly TranslateService _translateService;
    private readonly ILogger<TranslationService> _logger;
    private readonly IServiceProvider _serviceProvider;

    public TranslationService(TranslateService translateService, ILogger<TranslationService> logger, IServiceProvider serviceProvider)
    {
        _translateService = translateService;
        _logger = logger;
        _serviceProvider = serviceProvider;
    }

    /// <summary>
    /// 启动仓库翻译任务
    /// </summary>
    /// <param name="request">翻译请求</param>
    /// <returns>任务ID</returns>
    [HttpPost("repository")]
    public async Task<string> StartRepositoryTranslation([FromBody] StartTranslationRequest request)
    {
        try
        {
            // 检查是否有进行中的任务
            var existingTaskId = await _translateService.GetRunningTranslationTaskAsync(
                request.WarehouseId,
                request.TargetLanguage,
                TranslationTaskType.Repository);

            if (existingTaskId != null)
            {
                throw new Exception($"Task {existingTaskId} already exists");
            }

            // 创建新的翻译任务
            var taskId = await _translateService.CreateTranslationTaskAsync(
                request.WarehouseId,
                request.TargetLanguage,
                request.SourceLanguage,
                TranslationTaskType.Repository);

            // 启动后台翻译任务
            _ = Task.Run(async () =>
            {
                using var scope = _serviceProvider.CreateScope();
                var scopedTranslateService = scope.ServiceProvider.GetRequiredService<TranslateService>();
                
                try
                {
                    await scopedTranslateService.UpdateTranslationTaskAsync(taskId, TranslationTaskStatus.Running);

                    var result = await scopedTranslateService.GenerateRepositoryI18nAsync(
                        request.WarehouseId,
                        request.TargetLanguage,
                        request.SourceLanguage);

                    var finalStatus = result.Success ? TranslationTaskStatus.Completed : TranslationTaskStatus.Failed;
                    await scopedTranslateService.UpdateTranslationTaskAsync(
                        taskId,
                        finalStatus,
                        result.ErrorMessage,
                        result.CatalogsTranslated,
                        result.FilesTranslated);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "后台翻译任务 {TaskId} 执行失败", taskId);
                    await scopedTranslateService.UpdateTranslationTaskAsync(
                        taskId,
                        TranslationTaskStatus.Failed,
                        ex.Message);
                }
            });

            return "翻译任务已启动";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "启动仓库翻译任务失败");
            throw new Exception("启动仓库翻译任务失败");
        }
    }

    /// <summary>
    /// 启动单个目录翻译任务
    /// </summary>
    /// <param name="request">目录翻译请求</param>
    /// <returns>任务ID</returns>
    [HttpPost("catalog")]
    public async Task<string> StartCatalogTranslation([FromBody] StartCatalogTranslationRequest request)
    {
        // 检查是否有进行中的任务
        var existingTaskId = await _translateService.GetRunningTranslationTaskAsync(
            request.WarehouseId,
            request.TargetLanguage,
            TranslationTaskType.Catalog,
            request.CatalogId);

        if (existingTaskId != null)
        {
            throw new Exception($"Task {existingTaskId} already exists");
        }

        // 创建新的翻译任务
        var taskId = await _translateService.CreateTranslationTaskAsync(
            request.WarehouseId,
            request.TargetLanguage,
            request.SourceLanguage,
            TranslationTaskType.Catalog,
            request.CatalogId);

        // 启动后台翻译任务
        _ = Task.Run(async () =>
        {
            using var scope = _serviceProvider.CreateScope();
            var scopedTranslateService = scope.ServiceProvider.GetRequiredService<TranslateService>();
            
            try
            {
                await scopedTranslateService.UpdateTranslationTaskAsync(taskId, TranslationTaskStatus.Running);

                var result = await scopedTranslateService.GenerateCatalogI18nAsync(
                    request.CatalogId,
                    request.TargetLanguage,
                    request.SourceLanguage);

                var finalStatus = result.Success ? TranslationTaskStatus.Completed : TranslationTaskStatus.Failed;
                await scopedTranslateService.UpdateTranslationTaskAsync(
                    taskId,
                    finalStatus,
                    result.ErrorMessage,
                    result.CatalogsTranslated,
                    result.FilesTranslated);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "后台目录翻译任务 {TaskId} 执行失败", taskId);
                await scopedTranslateService.UpdateTranslationTaskAsync(
                    taskId,
                    TranslationTaskStatus.Failed,
                    ex.Message);
            }
        });
        return "目录翻译任务已启动";
    }

    /// <summary>
    /// 获取翻译任务状态
    /// </summary>
    /// <param name="taskId">任务ID</param>
    /// <returns>任务状态</returns>
    [HttpGet("task/{taskId}")]
    public async Task<object> GetTranslationTaskStatus(string taskId)
    {
        var task = await _translateService.GetTranslationTaskAsync(taskId);
        if (task == null)
        {
            throw new Exception("翻译任务不存在");
        }

        return new
        {
            taskId = task.Id,
            status = task.Status.ToString(),
            progress = task.Progress,
            catalogsTranslated = task.CatalogsTranslated,
            filesTranslated = task.FilesTranslated,
            totalCatalogs = task.TotalCatalogs,
            totalFiles = task.TotalFiles,
            startedAt = task.StartedAt,
            completedAt = task.CompletedAt,
            duration = task.Duration,
            errorMessage = task.ErrorMessage
        };
    }

    /// <summary>
    /// 获取仓库的翻译任务列表
    /// </summary>
    /// <param name="warehouseId">仓库ID</param>
    /// <param name="targetLanguage">目标语言（可选）</param>
    /// <returns>翻译任务列表</returns>
    [HttpGet("repository/{warehouseId}/tasks")]
    public async Task<object> GetRepositoryTranslationTasks(string warehouseId,
        [FromQuery] string? targetLanguage = null)
    {
        var tasks = await _translateService.GetRepositoryTranslationTasksAsync(warehouseId, targetLanguage);

        var result = tasks.Select(t => new
        {
            taskId = t.Id,
            taskType = t.TaskType.ToString(),
            targetLanguage = t.TargetLanguage,
            sourceLanguage = t.SourceLanguage,
            status = t.Status.ToString(),
            progress = t.Progress,
            catalogsTranslated = t.CatalogsTranslated,
            filesTranslated = t.FilesTranslated,
            totalCatalogs = t.TotalCatalogs,
            totalFiles = t.TotalFiles,
            startedAt = t.StartedAt,
            completedAt = t.CompletedAt,
            duration = t.Duration,
            errorMessage = t.ErrorMessage
        }).ToList();

        return result;
    }

    /// <summary>
    /// 获取仓库支持的语言状态
    /// </summary>
    /// <param name="warehouseId">仓库ID</param>
    /// <returns>语言状态列表</returns>
    [HttpGet("repository/{warehouseId}/languages")]
    public async Task<object> GetRepositoryLanguageStatus(string warehouseId)
    {
        var supportedLanguages = _translateService.GetSupportedLanguages();
        var languageStatuses = new List<object>();

        foreach (var language in supportedLanguages)
        {
            var status = await _translateService.GetLanguageStatusAsync(warehouseId, language.Code);
            languageStatuses.Add(new
            {
                code = language.Code,
                name = language.Name,
                status = status.Status,
                exists = status.Exists,
                lastGenerated = status.LastGenerated,
                progress = status.Progress
            });
        }

        return languageStatuses;
    }

    /// <summary>
    /// 获取支持的语言列表
    /// </summary>
    /// <returns>语言列表</returns>
    [HttpGet("languages")]
    public async Task<object> GetSupportedLanguages()
    {
        var languages = _translateService.GetSupportedLanguages();
        return await Task.FromResult(languages.Select(l => new { code = l.Code, name = l.Name }));
    }
}

/// <summary>
/// 启动翻译任务请求
/// </summary>
public class StartTranslationRequest
{
    /// <summary>
    /// 仓库ID
    /// </summary>
    public string WarehouseId { get; set; } = string.Empty;

    /// <summary>
    /// 目标语言代码
    /// </summary>
    public string TargetLanguage { get; set; } = string.Empty;

    /// <summary>
    /// 源语言代码
    /// </summary>
    public string SourceLanguage { get; set; } = "en-US";
}

/// <summary>
/// 启动目录翻译任务请求
/// </summary>
public class StartCatalogTranslationRequest : StartTranslationRequest
{
    /// <summary>
    /// 目录ID
    /// </summary>
    public string CatalogId { get; set; } = string.Empty;
}