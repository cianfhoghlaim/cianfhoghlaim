using Microsoft.AspNetCore.Mvc;

namespace KoalaWiki.Infrastructure;

public class ResultFilter : IEndpointFilter
{
    public async ValueTask<object?> InvokeAsync(EndpointFilterInvocationContext context, EndpointFilterDelegate next)
    {
        var value = await next(context);

        if (value is EmptyResult)
        {
            return null;
        }

        return new
        {
            code = 200,
            data = value,
        };
    }
}