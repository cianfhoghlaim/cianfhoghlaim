using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace Gaois.Localizer
{
    /// <summary>
    /// Extension methods for configuring the Gaois.Localizer request localization middleware
    /// </summary>
    public static class LocalizerServiceExtensions
    {
        /// <summary>
        /// Adds Gaois.Localizer configuration for handling request localization
        /// </summary>
        /// <param name="services">The services collection to configure.</param>
        /// <param name="configureSettings">An <see cref="Action{LocalizerOptions}"/> to configure the localizer options</param>
        /// <returns>Returns an <see cref="IServiceCollection"/> object</returns>
        public static IServiceCollection AddLocalizer(
            this IServiceCollection services, 
            Action<LocalizerOptions> configureSettings = null)
        {
            if (configureSettings is null)
                return services;

            services.Configure(configureSettings);

            var provider = services.BuildServiceProvider();
            var settings = provider.GetService<IOptions<LocalizerOptions>>().Value;

            if (settings.SupportedCultures is null) 
                throw new ArgumentNullException(nameof(settings.SupportedCultures));

            if (settings.SupportedUICultures is null)
                throw new ArgumentNullException(nameof(settings.SupportedUICultures));

            if (settings.DefaultRequestCulture is null)
                throw new ArgumentNullException(nameof(settings.DefaultRequestCulture));

            services.Configure<LocalizerOptions>(options => 
            {
                options.SupportedCultures = settings.SupportedCultures;
                options.SupportedUICultures = settings.SupportedUICultures;
                options.DefaultRequestCulture = settings.DefaultRequestCulture;
                options.RequireCulturePathParameter = settings.RequireCulturePathParameter;
            });

            services.Configure<RouteCultureOptions>(options =>
            {
                options.CultureParameterIndex = settings.RouteCulture.CultureParameterIndex;
                options.LanguageLocaleMap = settings.RouteCulture.LanguageLocaleMap;
                options.ExcludedRoutes = settings.RouteCulture.ExcludedRoutes;
            });

            services.Configure<RequestLocalizationOptions>(options =>
            {
                options.DefaultRequestCulture = settings.DefaultRequestCulture;
                options.SupportedCultures = settings.SupportedCultures;
                options.SupportedUICultures = settings.SupportedUICultures;
                options.RequestCultureProviders.Clear();
                options.RequestCultureProviders.Add(
                    new RouteCultureProvider(
                        options.SupportedCultures,
                        options.DefaultRequestCulture,
                        settings.RouteCulture.CultureParameterIndex));
            });

            services.Configure<RequestCultureRerouterOptions>(options => 
            {
                options.StatusCode = settings.RequestCultureRerouter.StatusCode;
                options.ResponsePath = settings.RequestCultureRerouter.ResponsePath;
            });

            services.Configure<LocalizationCookiesOptions>(options =>
            {
                options.Expires = settings.LocalizationCookies.Expires;
                options.IsEssential = settings.LocalizationCookies.IsEssential;
            });

            return services;
        }
    }
}