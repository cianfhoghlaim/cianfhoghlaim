using System.Globalization;
using System.Net;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.Net.Http.Headers;

namespace Gaois.Localizer
{
    /// <summary>
    /// Causes the request to be redirected to a page in the default culture when a <see cref="CultureNotFoundException"/> is thrown in the request execution pipeline
    /// </summary>
    public class RequestCultureExceptionRerouter
    {
        private readonly RequestDelegate _next;
        private readonly IOptions<RouteCultureOptions> _routeCultureOptions;
        private readonly ILogger _logger;
        private readonly int _statusCode;
        private readonly string _responsePath;

        /// <summary>
        /// Causes the request to be redirected to a page in the default culture when a <see cref="CultureNotFoundException"/> is thrown in the request execution pipeline
        /// </summary>
        public RequestCultureExceptionRerouter(
            RequestDelegate next,
            IOptions<RouteCultureOptions> routeCultureOptions,
            ILogger<RequestCultureExceptionRerouter> logger)
        {
            _next = next ?? throw new CultureNotFoundException(nameof(next));
            _routeCultureOptions = routeCultureOptions;
            _logger = logger;
            _statusCode = (int)HttpStatusCode.Redirect;
        }

        /// <summary>
        /// Causes the request to be redirected to a page in the default culture when a <see cref="CultureNotFoundException"/> is thrown in the request execution pipeline
        /// </summary>
        /// <param name="next">A task that represents the completion of request processing</param>
        /// <param name="routeCultureOptions">The <see cref="RouteCultureOptions"/> to configure the rerouter with</param>
        /// <param name="logger">An instance of <see cref="ILogger"/></param>
        /// <param name="options">The <see cref="RequestCultureRerouterOptions"/> to configure the middleware with</param>
        public RequestCultureExceptionRerouter(
            RequestDelegate next, 
            IOptions<RouteCultureOptions> routeCultureOptions,
            ILogger<LocalizationCookies> logger, 
            RequestCultureRerouterOptions options)
        {
            _next = next ?? throw new CultureNotFoundException(nameof(next));
            _routeCultureOptions = routeCultureOptions;
            _logger = logger;
            _statusCode = options.StatusCode;
            _responsePath = options.ResponsePath;
        }

        /// <summary>
        /// Async method that listens for events in the request execution pipeline. Will catch <see cref="CultureNotFoundException"/> and return instructions to redirect the request in the response.
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

                var request = context.Request;
                var parts = request.Path.Value.Split('/');

                parts[_routeCultureOptions.Value.CultureParameterIndex] = CultureInfo.CurrentCulture.Name;

                var newPath = (string.IsNullOrWhiteSpace(_responsePath))
                    ? string.Join("/", parts)
                    : _responsePath;
                var newUrl = UrlUtilities.ReplacePath(request, newPath);

                _logger.LogRequestCultureNotFoundRedirect(newPath);

                context.Response.Clear();
                context.Response.StatusCode = _statusCode;
                context.Response.Headers[HeaderNames.Location] = newUrl;

                return;
            }
        } 
    }
}