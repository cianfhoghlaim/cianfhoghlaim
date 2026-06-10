using System.Collections.Generic;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Http;

namespace Gaois.Localizer
{
    /// <summary>
    /// Provides methods to validate that a given route is to be excluded from localization middleware processing
    /// </summary>
    public static class ExcludedRouteProvider
    {
        /// <summary>
        /// Validates that a given route is to be excluded from localization middleware processing
        /// </summary>
        /// <param name="excludedRoutes">A list of regex strings defining routes to be excluded from localization middleware processing</param>
        /// <param name="path">The request path</param>
        public static bool IsExcludedRoute(IList<string> excludedRoutes, PathString path)
        {
            if (!(excludedRoutes is List<string> routes) || routes.Count <= 0)
                return false;

            foreach (var route in routes)
            {
                var regex = new Regex(route, RegexOptions.Compiled);
                var match = regex.Match(path);

                if (match.Success)
                    return true;
            }

            return false;
        }
    }
}