using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Localization;

namespace Gaois.Localizer
{
    /// <summary>
    /// Determines the request's culture information
    /// </summary>
    /// <remarks>
    /// The culture is determined with reference to the following criteria, in order: (1) the culture parameter in URL, (2) the culture request cookie, (3) the HTTP Accept-Language header.
    /// The first criterion to be met will be returned. If no criteria are met, the default culture is returned.
    /// </remarks>
    public class RouteCultureProvider : IRequestCultureProvider
    {
        private readonly IList<CultureInfo>  _supportedCultures;
        private readonly CultureInfo _defaultCulture;
        private readonly CultureInfo _defaultUICulture;
        private readonly int _cultureParameterIndex;

        /// <summary>
        /// Determines the request's culture information
        /// </summary>
        /// <param name="supportedCultures">The cultures supported by the application</param>
        /// <param name="requestCulture">The default culture to use for requests when a supported culture could not be determined by one of the configured <see cref="IRequestCultureProvider"/>s. Defaults to <see cref="CultureInfo.CurrentCulture"/> and <see cref="CultureInfo.CurrentUICulture"/>.</param>
        /// <param name="cultureParameterIndex">Index of the request path parameter that represents the desired culture. The default value is 1.</param>
        /// <remarks>
        /// The culture is determined with reference to the following criteria, in order: (1) the culture parameter in URL, (2) the culture request cookie, (3) the HTTP Accept-Language header.
        /// The first criterion to be met will be returned. If no criteria are met, the default culture is returned.
        /// </remarks>
        public RouteCultureProvider(
            IList<CultureInfo> supportedCultures, 
            RequestCulture requestCulture, 
            int cultureParameterIndex = 1)
        {
            _supportedCultures = supportedCultures;
            _defaultCulture = requestCulture.Culture;
            _defaultUICulture = requestCulture.UICulture;
            _cultureParameterIndex = cultureParameterIndex;
        }

        /// <summary>
        /// Assesses if request culture is provided in URL. If not, culture is inferred from HTTP headers and request cookies. If no culture can be inferred, the default culture is selected. 
        /// </summary>
        public Task<ProviderCultureResult> DetermineProviderCultureResult(HttpContext context)
        {
            var path = context.Request.Path.ToString();

            // If no culture provided in URL, infer from HTTP headers & cookies, or else fall back to default culture
            if (path.Length <= 1)
            {
                // Establish default culture, it will be updated if subsequent criteria are met
                var locale = _defaultCulture.Name;

                // If culture is present in HTTP Accept-Language header
                var acceptLanguages = context.Request.Headers["Accept-Language"].ToString()
                    .Split(',');

                if (acceptLanguages is string[] && acceptLanguages.Length > 0)
                {
                    foreach (var supportedCulture in _supportedCultures)
                    {
                        if (acceptLanguages.Contains(supportedCulture.Name)
                            || acceptLanguages.Contains(supportedCulture.TwoLetterISOLanguageName)
                            || acceptLanguages.Contains(supportedCulture.ThreeLetterISOLanguageName))
                        {
                            locale = supportedCulture.Name;
                            break;
                        }
                    }
                }

                // If culture is present in request cookies
                var cookie = context.Request.Cookies[CookieRequestCultureProvider.DefaultCookieName];

                if (!string.IsNullOrWhiteSpace(cookie))
                {
                    var cookieValue = CookieRequestCultureProvider.ParseCookieValue(cookie);

                    foreach (var supportedCulture in _supportedCultures)
                    {
                        if (cookieValue.Cultures.Contains(supportedCulture.Name)
                            || cookieValue.Cultures.Contains(supportedCulture.TwoLetterISOLanguageName)
                            || cookieValue.Cultures.Contains(supportedCulture.ThreeLetterISOLanguageName))
                        {
                            locale = supportedCulture.Name;
                            break;
                        }
                    }
                }

                return Task.FromResult(new ProviderCultureResult(locale, locale));
            }

            var parameters = context.Request.Path.Value.Split('/');
            var culture = parameters[_cultureParameterIndex];

            // If culture is not formatted correctly, return default culture
            if (!Regex.IsMatch(culture, @"^[a-z]{2}(-[A-Z]{2})*$"))
                return Task.FromResult(new ProviderCultureResult(_defaultCulture.Name, _defaultUICulture.Name));

            // Otherwise, return Culture and UICulture from route culture parameter
            return Task.FromResult(new ProviderCultureResult(culture, culture));
        }
    }
}