using Microsoft.AspNetCore.Builder;

namespace Gaois.Localizer
{
    /// <summary>
    /// Extension methods to store localization data in a user cookie
    /// </summary>
    public static class LocalizationCookiesExtensions
    {
        /// <summary>
        /// Adds middleware to store the current request culture in a user cookie
        /// </summary>
        /// <param name="builder">The <see cref="IApplicationBuilder"/></param>
        public static IApplicationBuilder UseLocalizationCookies(this IApplicationBuilder builder) =>
            builder.UseMiddleware<LocalizationCookies>();

        /// <summary>
        /// Adds middleware to store the current request culture in a user cookie
        /// </summary>
        /// <param name="builder">The <see cref="IApplicationBuilder"/></param>
        /// <param name="options">The <see cref="LocalizationCookiesOptions"/> to configure the middleware with</param>
        public static IApplicationBuilder UseLocalizationCookies(
            this IApplicationBuilder builder, 
            LocalizationCookiesOptions options) => 
            builder.UseMiddleware<LocalizationCookies>(options);
    }
}