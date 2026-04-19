using System.Net;
using Microsoft.AspNetCore.Builder;

namespace Gaois.Localizer
{
    /// <summary>
    /// Extension method to handle requests where no culture parameter is provided
    /// </summary>
    public static class RequireCulturePathParameterExtensions
    {
        /// <summary>
        /// Adds middleware to redirect the request to a localized path when no culture parameter is provided
        /// </summary>
        public static IApplicationBuilder UseRequireCulturePathParameter(
            this IApplicationBuilder builder,
            int statusCode = (int)HttpStatusCode.Redirect) =>
            builder.UseMiddleware<RequireCulturePathParameter>(statusCode);
    }
}