using System.Collections.Generic;
using System.Globalization;
using Microsoft.AspNetCore.Localization;

namespace Gaois.Localizer
{
    /// <summary>
    /// Specifies options for the Gaois.Localizer middleware
    /// </summary>
    public class LocalizerOptions
    {
        /// <summary>
        /// The cultures supported by the application. The <see cref="RequestLocalizationMiddleware"/> will only set the current request culture to an entry in this list. Defaults to <see cref="CultureInfo.CurrentCulture"/>. 
        /// </summary>
        public IList<CultureInfo> SupportedCultures { get; set; }

        /// <summary>
        /// The UI cultures supported by the application. The <see cref="RequestLocalizationMiddleware"/> will only set the current request culture to an entry in this list. Defaults to <see cref="CultureInfo.CurrentCulture"/>. 
        /// </summary>
        public IList<CultureInfo> SupportedUICultures { get; set; }

        /// <summary>
        /// Gets or sets the default culture to use for requests when a supported culture could not be determined by one of the configured <see cref="RequestCultureProvider"/>s. Defaults to <see cref="CultureInfo.CurrentCulture"/> and <see cref="CultureInfo.CurrentUICulture"/>.
        /// </summary>
        public RequestCulture DefaultRequestCulture { get; set; }

        /// <summary>
        /// Specifies options for the <see cref="RequestCultureExceptionRerouter"/> middleware
        /// </summary>
        public RequestCultureRerouterOptions RequestCultureRerouter { get; set; } = new RequestCultureRerouterOptions();

        /// <summary>
        /// Specifies options for various middleware provided by Gaois.Localizer
        /// </summary>
        public RouteCultureOptions RouteCulture { get; set; } = new RouteCultureOptions();

        /// <summary>
        /// Specifies options for the <see cref="LocalizationCookies"/> middleware
        /// </summary>
        public LocalizationCookiesOptions LocalizationCookies { get; set; } = new LocalizationCookiesOptions();

        /// <summary>
        /// Specifies options for the <see cref="RequireCulturePathParameter"/> middleware
        /// </summary>
        public RequireCulturePathParameterOptions RequireCulturePathParameter { get; set; } = new RequireCulturePathParameterOptions();
    }
}