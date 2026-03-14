using System.Collections.Generic;

namespace Gaois.Localizer
{
    /// <summary>
    /// Specifies options for various middleware provided by Gaois.Localizer
    /// </summary>
    public class RouteCultureOptions
    {
        /// <summary>
        /// Specifies options for various middleware provided by Gaois.Localizer
        /// </summary>
        public RouteCultureOptions()
        {
            ExcludedRoutes.Add("Error");
        }

        /// <summary>
        /// Index of the request path parameter that represents the desired culture. The default value is 1.
        /// </summary>
        public int CultureParameterIndex { get; set; } = 1;

        /// <summary>
        /// A list of regex strings defining routes to be excluded from localization middleware processing
        /// </summary>
        /// <remarks>
        /// Example values: "^/api", "^/static".
        /// This will avoid throwing a <see cref="System.Globalization.CultureNotFoundException"/> when these strings occupy the route parameter normally reserved for the request culture, e.g. "/api/v1.2/documents/"
        /// Routes containing "Error" are excluded by default. This protects against circular culture exception errors when an error view is called.
        /// </remarks>
        public IList<string> ExcludedRoutes { get; set; } = new List<string>();
        
        /// <summary>
        /// A collection of keys and values where the keys are presumed to be two- or three-letter ISO language codes and the values are locale or extended language subtags
        /// </summary>
        public IDictionary<string, string> LanguageLocaleMap { get; set; } = new Dictionary<string, string>();

        /// <summary>
        /// Get the value of a locale or extended language subtag based on the values provided in the <see cref="LanguageLocaleMap"/>
        /// </summary>
        /// <param name="code">The two- or three-letter language code</param>
        public string InferLocaleFromLanguage(string code)
        {
            if (LanguageLocaleMap.ContainsKey(code))
                return LanguageLocaleMap[code];

            return code;
        }
    }
}