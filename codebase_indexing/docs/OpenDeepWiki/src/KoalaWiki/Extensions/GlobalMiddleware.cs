using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using KoalaWiki.Options;
using Microsoft.IdentityModel.Tokens;

namespace KoalaWiki.Extensions;

/// <summary>
/// 全局中间件
/// </summary>
public class GlobalMiddleware(ILogger<GlobalMiddleware> logger) : IMiddleware
{
    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        try
        {
            await next(context);
        }
        catch (Exception e)
        {
            logger.LogError(e, "An error occurred while processing the request.");
            context.Response.StatusCode = 500;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsJsonAsync(new
            {
                code = 500,
                message = e.Message
            });
        }
    }
}