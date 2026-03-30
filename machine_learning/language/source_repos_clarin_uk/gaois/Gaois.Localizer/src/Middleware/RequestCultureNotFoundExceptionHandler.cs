using System.Globalization;
using System.Net;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;

namespace Gaois.Localizer
{
    /// <summary>
    /// Causes a 404 Not Found HTTP status code to returned when a <see cref="CultureNotFoundException"/> is thrown in the request execution pipeline
    /// </summary>
    public class RequestCultureExceptionHandler
    {
        private readonly RequestDelegate _next;
        private readonly ILogger _logger;

        /// <summary>
        /// Causes a 404 Not Found HTTP status code to returned when a <see cref="CultureNotFoundException"/> is thrown in the request execution pipeline
        /// </summary>
        public RequestCultureExceptionHandler(
            RequestDelegate next,
            ILogger<RequestCultureExceptionHandler> logger)
        {
            _next = next ?? throw new CultureNotFoundException(nameof(next));
            _logger = logger;
        }

        /// <summary>
        /// Async method that listens for events in the request execution pipeline. Will catch <see cref="CultureNotFoundException"/> and return a 404 Not Found HTTP status code in the response.
        /// </summary>
        public async Task Invoke(HttpContext context)
        {
            try
            {
                await _next(context);
            }
            catch (CultureNotFoundException)
            {
                if (context.Response.HasStarted)
                    throw;

                _logger.LogRequestCultureNotFound(context.Request.Path);

                context.Response.Clear();
                context.Response.StatusCode = (int)HttpStatusCode.NotFound;

                return;
            }
        }
    }
}