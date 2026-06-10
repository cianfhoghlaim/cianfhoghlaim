using System.Net;
using Microsoft.AspNetCore.Builder;

namespace Gaois.Localizer
{
    /// <summary>
    /// Extension method that handles a <see cref="System.Globalization.CultureNotFoundException"/> in the request pipeline by returning a 404 HTTP response code
    /// </summary>
    public static class RequestCultureExceptionHandlerExtensions
    {
        /// <summary>
        /// Adds middleware that will return a 404 <see cref="HttpStatusCode.NotFound"/> response whenever a <see cref="System.Globalization.CultureNotFoundException"/> is thrown
        /// </summary>
        /// <remarks>
        /// Use with RequestCultureValidation to test for unsupported cultures in the request and handle the exception. Must be placed before UseRequestCultureValidation() in the request execution pipeline.
        /// </remarks>
        public static IApplicationBuilder UseRequestCultureExceptionHandler(this IApplicationBuilder builder) =>
            builder.UseMiddleware<RequestCultureExceptionHandler>();
    }
}