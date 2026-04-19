using System;
using System.Collections.Generic;
using System.Globalization;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Localization;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace Gaois.Localizer
{
    /// <summary>
    /// Stores current request culture in a user cookie 
    /// </summary>
    public class LocalizationCookies
    {
        private readonly RequestDelegate _next;
        private readonly IOptions<RouteCultureOptions> _routeCultureOptions;
        private readonly ILogger _logger;
        private readonly DateTimeOffset? _cookieExpires;
        private readonly bool _cookieIsEssential;

        /// <summary>
        /// Stores current request culture in a user cookie
        /// </summary>
        public LocalizationCookies(
            RequestDelegate next, 
            IOptions<RouteCultureOptions> routeCultureOptions,
            ILogger<LocalizationCookies> logger)
        {
            _next = next;
            _routeCultureOptions = routeCultureOptions;
            _logger = logger;
            _cookieExpires = DateTimeOffset.UtcNow.AddYears(1);
            _cookieIsEssential = false;
        }

        /// <summary>
        /// Stores current request culture in a user cookie
        /// </summary>
        public LocalizationCookies(
            RequestDelegate next,
            IOptions<RouteCultureOptions> routeCultureOptions,
            ILogger<LocalizationCookies> logger,
            LocalizationCookiesOptions options)
        {
            _next = next;
            _routeCultureOptions = routeCultureOptions;
            _logger = logger;
            _cookieExpires = options.Expires;
            _cookieIsEssential = options.IsEssential;
        }

        /// <summary>
        /// Appends a culture cookie to the HTTP response, when appropriate, to store the client's culture preference
        /// </summary>
        /// <remarks>
        /// <para>If the current request does not already contain a culture cookie, a new one will be appended to the response.</para>
        /// <para>If the request contains a culture cookie but it is different from the current culture, a new cookie will be appended.</para>
        /// </remarks>
        public Task Invoke(HttpContext context)
        {
            var request = context.Request;
            var path = request.Path;
            var excludedRoutes = _routeCultureOptions.Value.ExcludedRoutes ?? new List<string>();

            if (ExcludedRouteProvider.IsExcludedRoute(excludedRoutes, path))
                return _next(context);

            var locale = CultureInfo.CurrentCulture.Name;
            var cookie = context.Request.Cookies[CookieRequestCultureProvider.DefaultCookieName];
            var cookieValue = CookieRequestCultureProvider.ParseCookieValue(cookie);

            if (!string.IsNullOrWhiteSpace(cookie) && cookieValue.Cultures.Contains(locale))
                return _next(context);
            
            context.Response.Cookies.Append(
                CookieRequestCultureProvider.DefaultCookieName,
                CookieRequestCultureProvider.MakeCookieValue(new RequestCulture(culture: locale, uiCulture: locale)),
                new CookieOptions { Expires = _cookieExpires, IsEssential = _cookieIsEssential }
            );
            
            _logger.LogLocalizationCookieAppended(request.Path);
            
            return _next(context);
        }
    }
}