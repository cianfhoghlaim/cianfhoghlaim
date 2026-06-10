using System.Collections.Generic;
using System.Net;
using Microsoft.AspNetCore.Rewrite;
using Microsoft.Extensions.Options;
using Microsoft.Net.Http.Headers;

namespace Gaois.Localizer
{
    /// <summary>
    /// Redirects a request containing a two- or three-letter ISO language code to a URL containing another supported culture
    /// </summary>
    /// <remarks>
    /// Helpful if you wish to migrate your application to a request path scheme that uses a different language or locale format
    /// </remarks>
    public class RedirectLanguageToLocale : IRule
    {
        private readonly IOptions<RouteCultureOptions> _routeCultureOptions;
        private readonly IDictionary<string, string> _languageLocaleMap;
        private readonly int _statusCode;

        /// <summary>
        /// Redirects a request containing a two- or three-letter ISO language code to a URL containing another supported culture
        /// </summary>
        /// <param name="routeCultureOptions">The <see cref="RouteCultureOptions"/> to configure the redirect rule with</param>
        /// <param name="statusCode">The HTTP status code to return in the response. The default is a 302 <see cref="HttpStatusCode.Redirect"/> code.</param>
        public RedirectLanguageToLocale(
            IOptions<RouteCultureOptions> routeCultureOptions,
            int statusCode = (int)HttpStatusCode.Redirect)
        {
            _routeCultureOptions = routeCultureOptions;
            _languageLocaleMap = routeCultureOptions.Value.LanguageLocaleMap;
            _statusCode = statusCode;
        }

        /// <summary>
        /// Checks that the <see cref="RouteCultureOptions.LanguageLocaleMap"/> contains the current request culture. If yes, redirects to a URL containing the matching locale.
        /// </summary>
        /// <param name="context">A <see cref="RewriteContext"/> context</param>
        public void ApplyRule(RewriteContext context)
        {
            var request = context.HttpContext.Request;
            var parts = request.Path.Value.Split('/');
            var culture = parts[_routeCultureOptions.Value.CultureParameterIndex];

            if (!_languageLocaleMap.ContainsKey(culture))
            {
                context.Result = RuleResult.ContinueRules;
                return;
            }

            foreach (var map in _languageLocaleMap)
            {
                if (map.Key == culture)
                {
                    parts[_routeCultureOptions.Value.CultureParameterIndex] = map.Value;
                    break;
                }
            }

            var newPath = string.Join("/", parts);
            var newUrl = UrlUtilities.ReplacePath(request, newPath);

            var response = context.HttpContext.Response;
            response.StatusCode = _statusCode;
            response.Headers[HeaderNames.Location] = newUrl;
            context.Result = RuleResult.EndResponse;  
        }
    }
}