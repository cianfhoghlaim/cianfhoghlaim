using System;
using Gaois.QueryLogger.AspNetCore;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Extension methods for configuring Gaois.QueryLogger
    /// </summary>
    public static class QueryLoggerServiceExtensions
    {
        /// <summary>
        /// Adds Gaois.QueryLogger configuration for logging queries
        /// </summary>
        /// <param name="services">The services collection to configure</param>
        /// <param name="configuration">An <see cref="IConfiguration"/> object</param>
        /// <param name="configureSettings">An <see cref="Action{QueryLoggerSettings}"/> to configure options for Gaois.QueryLogger</param>
        /// <returns>An <see cref="IServiceCollection"/></returns>
        public static IServiceCollection AddQueryLogger(this IServiceCollection services, IConfiguration configuration, Action<QueryLoggerSettings> configureSettings = null)
        {
            services.Configure<QueryLoggerSettings>(configuration);
            return AddQueryLogger(services, configureSettings);
        }

        /// <summary>
        /// Adds Gaois.QueryLogger configuration for logging queries
        /// </summary>
        /// <param name="services">The services collection to configure</param>
        /// <param name="configureSettings">An <see cref="Action{QueryLoggerSettings}"/> to configure options for Gaois.QueryLogger</param>
        /// <returns>An <see cref="IServiceCollection"/></returns>
        public static IServiceCollection AddQueryLogger(this IServiceCollection services, Action<QueryLoggerSettings> configureSettings = null)
        {
            if (configureSettings != null)
                services.Configure(configureSettings);

            services.AddSingleton<IHttpContextAccessor, HttpContextAccessor>();
            services.AddSingleton<ILogStore, SqlLogStore>();
            services.AddTransient<IQueryLogger, QueryLogger>();
            services.AddTransient<IAlertService, EmailAlertService>();
            services.AddTransient<IHttpContextData, HttpContextData>();

            return services;
        }
    }
}