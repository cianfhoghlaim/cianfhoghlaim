namespace KoalaWiki.Tools;

public class ToolResultInterceptor(ILogger<ToolResultInterceptor> logger) : IFunctionInvocationFilter
{
    public async Task OnFunctionInvocationAsync(FunctionInvocationContext context,
        Func<FunctionInvocationContext, Task> next)
    {
        var functionName = context.Function.Name;
        var requestId = Guid.NewGuid().ToString();

        try
        {
            // 记录函数调用开始
            logger.LogInformation("Function {FunctionName} started. RequestId: {RequestId}",
                functionName, requestId);

            var stopwatch = System.Diagnostics.Stopwatch.StartNew();

            // 执行下一个中间件
            await next(context);

            stopwatch.Stop();

            // 记录函数调用成功完成
            logger.LogInformation("Function {FunctionName} completed successfully. " +
                                  "RequestId: {RequestId}, Duration: {Duration}ms",
                functionName, requestId, stopwatch.ElapsedMilliseconds);
        }
        catch (Exception ex)
        {
            // 记录异常
            logger.LogError(ex, "Function {FunctionName} failed. RequestId: {RequestId}",
                functionName, requestId);
            throw;
        }
    }
}