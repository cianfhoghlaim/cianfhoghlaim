using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using FastService;
using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains;
using KoalaWiki.Domains.FineTuning;
using KoalaWiki.Dto;
using KoalaWiki.Infrastructure;
using KoalaWiki.KoalaWarehouse;
using KoalaWiki.Options;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;

#pragma warning disable SKEXP0001

namespace KoalaWiki.Services;

[Tags("微调管理")]
[Route("/api/FineTuning")]
[Authorize]
public class FineTuningService(IKoalaWikiContext koala, IUserContext userContext) : FastApi
{
    /// <summary>
    /// 创建训练数据集
    /// </summary>
    [EndpointSummary("微调管理：创建训练数据集")]
    [Filter(typeof(ResultFilter))]
    public async Task<TrainingDataset> CreateDatasetAsync(CreateDatasetInput input)
    {
        var warehouse = await koala.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == input.WarehouseId);

        if (warehouse == null)
        {
            throw new Exception("仓库不存在");
        }

        var dataset = new TrainingDataset
        {
            Id = Guid.NewGuid().ToString(),
            WarehouseId = input.WarehouseId,
            UserId = userContext.CurrentUserId,
            CreatedAt = DateTime.Now,
            UpdatedAt = DateTime.Now,
            Status = TrainingDatasetStatus.NotStarted,
            Name = input.Name,
            Endpoint = input.Endpoint,
            Model = input.Model,
            ApiKey = input.ApiKey,
            Prompt = input.Prompt
        };

        await koala.TrainingDatasets.AddAsync(dataset);
        await koala.SaveChangesAsync();

        return dataset;
    }

    /// <summary>
    /// 获取训练数据集列表
    /// </summary>
    [EndpointSummary("微调管理：获取训练数据集列表")]
    [Filter(typeof(ResultFilter))]
    public async Task<List<TrainingDataset>> GetDatasetsAsync(string? warehouseId)
    {
        return await koala.TrainingDatasets
            .AsNoTracking()
            .Where(x => (string.IsNullOrEmpty(warehouseId) || x.WarehouseId == warehouseId) &&
                        x.UserId == userContext.CurrentUserId)
            .ToListAsync();
    }

    /// <summary>
    /// 获取训练数据集详情
    /// </summary>
    [EndpointSummary("微调管理：获取训练数据集详情")]
    [Filter(typeof(ResultFilter))]
    public async Task<TrainingDataset> GetDatasetAsync(string datasetId)
    {
        var dataset = await koala.TrainingDatasets
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == datasetId && x.UserId == userContext.CurrentUserId);

        if (dataset == null)
        {
            throw new Exception("数据集不存在");
        }

        return dataset;
    }

    /// <summary>
    /// 更新训练数据集
    /// </summary>
    [EndpointSummary("微调管理：更新训练数据集")]
    [Filter(typeof(ResultFilter))]
    public async Task<TrainingDataset> UpdateDatasetAsync(UpdateDatasetInput input)
    {
        var dataset = await koala.TrainingDatasets
            .FirstOrDefaultAsync(x => x.Id == input.DatasetId && x.UserId == userContext.CurrentUserId);

        if (dataset == null)
        {
            throw new Exception("数据集不存在");
        }

        dataset.Name = input.Name;
        dataset.Endpoint = input.Endpoint;
        dataset.ApiKey = input.ApiKey;
        dataset.Prompt = input.Prompt;
        dataset.UpdatedAt = DateTime.Now;

        await koala.SaveChangesAsync();

        return dataset;
    }

    /// <summary>
    /// 删除训练数据集
    /// </summary>
    [EndpointSummary("微调管理：删除训练数据集")]
    [Filter(typeof(ResultFilter))]
    public async Task DeleteDatasetAsync(string datasetId)
    {
        var dataset = await koala.TrainingDatasets
            .FirstOrDefaultAsync(x => x.Id == datasetId && x.UserId == userContext.CurrentUserId);

        if (dataset == null)
        {
            throw new Exception("数据集不存在");
        }

        await koala.FineTuningTasks
            .Where(x => x.TrainingDatasetId == datasetId && x.UserId == userContext.CurrentUserId)
            .ExecuteDeleteAsync();

        await koala.TrainingDatasets
            .Where(x => x.WarehouseId == dataset.WarehouseId && x.UserId == userContext.CurrentUserId)
            .ExecuteDeleteAsync();

        await koala.TrainingDatasets.Where(x => x.Id == datasetId && x.UserId == userContext.CurrentUserId)
            .ExecuteDeleteAsync();
    }

    /// <summary>
    /// 创建微调任务
    /// </summary>
    [EndpointSummary("微调管理：创建微调任务")]
    [Filter(typeof(ResultFilter))]
    public async Task<FineTuningTask> CreateTaskAsync(CreateTaskInput input)
    {
        var dataset = await koala.TrainingDatasets
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == input.TrainingDatasetId && x.UserId == userContext.CurrentUserId);

        if (dataset == null)
        {
            throw new Exception("数据集不存在");
        }

        var task = new FineTuningTask
        {
            Id = Guid.NewGuid().ToString(),
            WarehouseId = dataset.WarehouseId,
            TrainingDatasetId = input.TrainingDatasetId,
            DocumentCatalogId = input.DocumentCatalogId,
            Name = input.Name,
            UserId = userContext.CurrentUserId,
            Description = input.Description,
            CreatedAt = DateTime.Now,
            Status = FineTuningTaskStatus.NotStarted
        };

        await koala.FineTuningTasks.AddAsync(task);
        await koala.SaveChangesAsync();

        return task;
    }

    /// <summary>
    /// 获取微调任务列表
    /// </summary>
    [EndpointSummary("微调管理：获取微调任务列表")]
    [Filter(typeof(ResultFilter))]
    public async Task<List<FineTuningTask>> GetTasksAsync(string warehouseId)
    {
        return await koala.FineTuningTasks
            .AsNoTracking()
            .Where(x => x.WarehouseId == warehouseId && x.UserId == userContext.CurrentUserId)
            .ToListAsync();
    }

    /// <summary>
    /// 获取微调任务详情
    /// </summary>
    [EndpointSummary("微调管理：获取微调任务详情")]
    [Filter(typeof(ResultFilter))]
    public async Task<FineTuningTask> GetTaskAsync(string taskId)
    {
        var task = await koala.FineTuningTasks
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == taskId && x.UserId == userContext.CurrentUserId);

        if (task == null)
        {
            throw new Exception("任务不存在");
        }

        return task;
    }

    /// <summary>
    /// 启动微调任务
    /// </summary>
    [EndpointSummary("微调管理：启动微调任务")]
    public async Task<FineTuningTask> StartTaskAsync(StartTaskInput input, HttpContext context)
    {
        var task = await koala.FineTuningTasks
            .FirstOrDefaultAsync(x => x.Id == input.TaskId && x.UserId == userContext.CurrentUserId);

        if (task == null)
        {
            throw new Exception("任务不存在");
        }

        if (task.Status == FineTuningTaskStatus.InProgress)
        {
            throw new Exception("任务已在进行中，请勿重复启动");
        }

        var dataset = await koala.TrainingDatasets
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == task.TrainingDatasetId);

        if (dataset == null)
        {
            throw new Exception("数据集不存在");
        }

        // 更新任务状态
        task.Status = FineTuningTaskStatus.InProgress;
        task.StartedAt = DateTime.Now;

        var fileItem = await koala.DocumentFileItems
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.DocumentCatalogId == task.DocumentCatalogId);

        if (fileItem == null)
        {
            throw new Exception("当前微调任务的文档内容不存在，请先生成文档内容。");
        }

        var document = await koala.Documents
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.WarehouseId == dataset.WarehouseId);

        var warehouse = await koala.Warehouses
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == dataset.WarehouseId);

        if (document == null)
        {
            throw new Exception("当前微调任务的文档不存在，请先生成文档。");
        }

        await koala.FineTuningTasks.Where(x => x.Id == dataset.Id)
            .ExecuteUpdateAsync(x => x.SetProperty(a => a.Status, FineTuningTaskStatus.InProgress)
                    .SetProperty(a => a.StartedAt, DateTime.Now)
                    .SetProperty(a => a.CreatedAt, DateTime.Now),
                context.RequestAborted);

        try
        {
            // 配置OpenAI客户端
            var kernel = await KernelFactory.GetKernel(dataset.Endpoint,
                dataset.ApiKey, document.GitPath, dataset.Model, false);

            var chat = kernel.GetRequiredService<IChatCompletionService>();

            var prompt = string.IsNullOrEmpty(input.Prompt)
                ? dataset.Prompt.Replace("{{markdown_content}}", fileItem.Content)
                : input.Prompt.Replace("{{markdown_content}}", fileItem.Content);

            if (!string.IsNullOrEmpty(input.Prompt) && input.Prompt != dataset.Prompt)
            {
                await koala.TrainingDatasets.Where(x => x.Id == dataset.Id)
                    .ExecuteUpdateAsync(x => x.SetProperty(a => a.Prompt, input.Prompt));
            }

            // 在prompt的头部增加<catalogue>标签
            prompt += $"<catalogue>\n{document.GetCatalogueSmartFilterOptimized()}\n</catalogue>";

            // 这里可以实现实际的微调训练逻辑
            var history = new ChatHistory();
            history.AddUserMessage(prompt);

            var first = true;
            var sb = new StringBuilder();

            await foreach (var item in chat.GetStreamingChatMessageContentsAsync(history,
                               new OpenAIPromptExecutionSettings()
                               {
                                   MaxTokens = DocumentsHelper.GetMaxTokens(dataset.Model),
                                   ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions,
                                   Temperature = 0.3,
                               }, kernel))
            {
                if (first)
                {
                    // 模拟训练过程更新
                    context.Response.Headers.ContentType = "text/event-stream";
                    context.Response.Headers.CacheControl = "no-cache";

                    first = false;
                    await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new
                    {
                        type = "start",
                        content = "训练开始",
                    }, JsonSerializerOptions.Web)}\n\n");
                }

                if (string.IsNullOrEmpty(item.Content))
                {
                    continue;
                }

                await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new
                {
                    type = "progress",
                    content = item.ToString(),
                }, JsonSerializerOptions.Web)}\n\n");

                sb.Append(item.Content);

                await context.Response.Body.FlushAsync();
            }

            var datasetContent = sb.ToString();

            // 提取<data>标签中的内容
            var regex = new Regex(@"<data>(.*?)</data>", RegexOptions.Singleline);

            var match = regex.Match(datasetContent);
            if (match.Success)
            {
                datasetContent = match.Groups[1].Value;
            }

            // 提取```json```标签中的内容
            regex = new Regex(@"```json(.*?)```", RegexOptions.Singleline);
            match = regex.Match(datasetContent);
            if (match.Success)
            {
                datasetContent = match.Groups[1].Value;
            }


            await koala.FineTuningTasks.Where(x => x.Id == task.Id)
                .ExecuteUpdateAsync(x => x.SetProperty(a => a.Status, FineTuningTaskStatus.Completed)
                        .SetProperty(x => x.Dataset, datasetContent)
                        .SetProperty(x => x.OriginalDataset, sb.ToString())
                        .SetProperty(a => a.CompletedAt, DateTime.Now),
                    context.RequestAborted);

            await koala.TrainingDatasets.Where(x => x.Id == dataset.Id)
                .ExecuteUpdateAsync(x => x.SetProperty(a => a.Status, TrainingDatasetStatus.Completed)
                        .SetProperty(a => a.UpdatedAt, DateTime.Now),
                    context.RequestAborted);

            await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new
            {
                type = "complete",
                content = "训练已完成",
            }, JsonSerializerOptions.Web)}\n\n");
        }
        catch (Exception ex)
        {
            // 处理错误情况
            task.Status = FineTuningTaskStatus.Failed;
            task.Error = ex.Message;
            await koala.SaveChangesAsync();

            await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new
            {
                type = "error",
                content = ex.Message,
            }, JsonSerializerOptions.Web)}\n\n");
        }
        finally
        {
            await context.Response.WriteAsync($"data: [done]\n\n");
        }

        return task;
    }

    /// <summary>
    /// 取消微调任务
    /// </summary>
    [Filter(typeof(ResultFilter))]
    public async Task<FineTuningTask> CancelTaskAsync(string taskId)
    {
        var task = await koala.FineTuningTasks
            .FirstOrDefaultAsync(x => x.Id == taskId && x.UserId == userContext.CurrentUserId);

        if (task == null)
        {
            throw new Exception("任务不存在");
        }

        if (task.Status != FineTuningTaskStatus.InProgress)
        {
            throw new Exception("任务未在进行中，无法取消");
        }

        task.Status = FineTuningTaskStatus.Cancelled;
        await koala.SaveChangesAsync();

        return task;
    }

    /// <summary>
    /// 删除微调任务
    /// </summary>
    [Filter(typeof(ResultFilter))]
    public async Task DeleteTaskAsync(string taskId)
    {
        var task = await koala.FineTuningTasks
            .FirstOrDefaultAsync(x => x.Id == taskId && x.UserId == userContext.CurrentUserId);

        if (task == null)
        {
            throw new Exception("任务不存在");
        }

        koala.FineTuningTasks.Remove(task);
        await koala.SaveChangesAsync();
    }
}