using System.Collections.Generic;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Options;

namespace Gaois.Localizer
{
    /// <summary>
    /// Provides methods to validate that a given request culture is supported by the application
    /// </summary>
    public class CultureSupportValidation
    {
        private readonly IOptions<RequestLocalizationOptions> _localizationOptions;

        /// <summary>
        /// Provides methods to validate that a given request culture is supported by the application
        /// </summary>
        /// <param name="options">The <see cref="RequestLocalizationOptions"/> that define the supported cultures</param>
        public CultureSupportValidation(IOptions<RequestLocalizationOptions> options)
        {  
            _localizationOptions = options;
        }

        /// <summary>
        /// Validates that a given request culture is supported by the application
        /// </summary>
        /// <param name="requestCulture">The culture provided in the request</param>
        public bool IsSupportedCulture(string requestCulture)
        {
            var supportedUICultures = _localizationOptions.Value.SupportedUICultures;

            if (supportedUICultures is null)
                return false;
            
            var supportedCultures = new List<string>();
            
            foreach (var culture in supportedUICultures)
                supportedCultures.Add(culture.Name);

            return supportedCultures.Contains(requestCulture);
        }
    }
}