using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace Gaois.Localizer
{
    /// <summary>
    /// Extension methods that manage the application of request localization middleware
    /// </summary>
    public static class LocalizerExtensions
    {
        /// <summary>
        /// Adds middleware to handle all aspects of request localization
        /// </summary>
        /// <param name="builder">The <see cref="IApplicationBuilder"/></param>
        public static void UseLocalizer(this IApplicationBuilder builder)
        {
            var localizerOptions = builder.ApplicationServices
                .GetService<IOptions<LocalizerOptions>>()
                .Value;

            if (localizerOptions.RequestCultureRerouter.RerouteRequestCultureExceptions)
            {
                builder.UseRequestCultureExceptionRerouter(localizerOptions.RequestCultureRerouter);
            }
            else
            {
                builder.UseRequestCultureExceptionHandler();
            }

            builder.UseRequestCultureValidation();

            var localizationOptions = builder.ApplicationServices
                .GetService<IOptions<RequestLocalizationOptions>>()
                .Value;

            builder.UseRequestLocalization(localizationOptions);

            if (localizerOptions.LocalizationCookies.UseLocalizationCookies)
                builder.UseLocalizationCookies(localizerOptions.LocalizationCookies);

            if (localizerOptions.RequireCulturePathParameter.RequireCulturePathParameter)
                builder.UseRequireCulturePathParameter();
        }
    }
}