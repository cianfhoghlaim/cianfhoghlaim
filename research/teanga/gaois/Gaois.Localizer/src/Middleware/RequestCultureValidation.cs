using System.Collections.Generic;
using System.Globalization;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Options;

namespace Gaois.Localizer
{
    /// <summary>
    /// Verifies that the request culture is supported by the application
    /// </summary>
    public class RequestCultureValidation
    {
        private readonly RequestDelegate _next;
        private readonly IOptions<RequestLocalizationOptions> _localizationOptions;
        private readonly IOptions<RouteCultureOptions> _routeCultureOptions;
    
        /// <summary>
        /// Verifies that the request culture is supported by the application
        /// </summary>
        public RequestCultureValidation(
            RequestDelegate next, 
            IOptions<RequestLocalizationOptions> localizationOptions, 
            IOptions<RouteCultureOptions> routeCultureOptions)
        {
            _next = next;
            _localizationOptions = localizationOptions;
            _routeCultureOptions = routeCultureOptions;
        }

        /// <summary>
        /// Tests the request culture against supported application cultures and non-culture values. Throws a <see cref="CultureNotFoundException"/> if request culture is not supported.
        /// </summary>
        public Task Invoke(HttpContext context)
        {
            var path = context.Request.Path;
            var parameters = context.Request.Path.Value.Split('/');

            if (parameters is null || parameters.Length <= 1)
                return _next(context);

            var culture = parameters[_routeCultureOptions.Value.CultureParameterIndex];
            var excludedRoutes = _routeCultureOptions.Value.ExcludedRoutes ?? new List<string>();

            if (ExcludedRouteProvider.IsExcludedRoute(excludedRoutes, path))
            {
                return _next(context);
            }
            else if (IsSupportedCulture(culture))
            {
                return _next(context);
            }
            else
            {
                throw new CultureNotFoundException();
            }
        }

        /// <summary>
        /// Tests that a given request culture is supported by the application
        /// </summary>
        /// <param name="requestCulture">The culture provided in the request</param>
        public bool IsSupportedCulture(string requestCulture)
        {
            if (string.IsNullOrWhiteSpace(requestCulture))
                return true;
            
            var culture = new CultureSupportValidation(_localizationOptions);
            return culture.IsSupportedCulture(requestCulture);
        }
    }
}