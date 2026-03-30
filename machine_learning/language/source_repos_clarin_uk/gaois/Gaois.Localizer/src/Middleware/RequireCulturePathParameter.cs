using System.Globalization;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.Net.Http.Headers;

namespace Gaois.Localizer
{
    /// <summary>
    /// Redirects the request to a localized root path if the URL contains no culture parameter
    /// </summary>
    public class RequireCulturePathParameter
    {
        private readonly RequestDelegate _next;
        private readonly IOptions<RouteOptions> _routeOptions;
        private readonly IOptions<RouteCultureOptions> _routeCultureOptions;
        private readonly ILogger _logger;
        private readonly int _statusCode;

        /// <summary>
        /// Redirects the request to a localized root path if the URL contains no culture parameter
        /// </summary>
        public RequireCulturePathParameter(
            RequestDelegate next,
            IOptions<RouteOptions> routeOptions,
            IOptions<RouteCultureOptions> routeCultureOptions,
            ILogger<RequireCulturePathParameter> logger, 
            int statusCode)
        {
            _next = next;
            _routeOptions = routeOptions;
            _routeCultureOptions = routeCultureOptions;
            _logger = logger;
            _statusCode = statusCode;
        }

        /// <summary>
        /// Assesses if request contains a culture parameter. If not, appends current culture name to path and redirects.
        /// </summary>
        /// <remarks>
        /// The redirect URL respects the <see cref="RouteOptions"/> setting as regards whether a trailing slash should be appeneded to the generated URL
        /// </remarks>
        public Task Invoke(HttpContext context)
        {
            var request = context.Request;
            var parameters = request.Path.Value.Split('/');
            var culture = parameters[_routeCultureOptions.Value.CultureParameterIndex];

            if (!string.IsNullOrWhiteSpace(culture))
                return _next(context);

            var newPath = $"/{CultureInfo.CurrentCulture.Name}";

            if (_routeOptions.Value.AppendTrailingSlash)
                newPath += "/";

            var newUrl = UrlUtilities.ReplacePath(request, newPath);

            _logger.LogRequiredCultureRedirect(newPath);

            context.Response.Clear();
            context.Response.StatusCode = _statusCode;
            context.Response.Headers[HeaderNames.Location] = newUrl;

            return _next(context);
        }
    }
}