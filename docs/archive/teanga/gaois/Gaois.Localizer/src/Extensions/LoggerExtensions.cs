using System;
using Microsoft.Extensions.Logging;

namespace Gaois.Localizer
{
    internal static class LoggerExtensions
    {
        private static Action<ILogger, string, Exception> _logRequestCultureNotFound = LoggerMessage.Define<string>(
            logLevel: LogLevel.Information,
            eventId: 1000,
            formatString: "Request culture at '{Path}' is not supported by the application. 404 HTTP status code returned."
        );

        private static Action<ILogger, string, Exception> _logRequestCultureNotFoundRedirect = LoggerMessage.Define<string>(
            logLevel: LogLevel.Information,
            eventId: 1001,
            formatString: "Request culture is not supported by the application. Redirecting to '{Path}'."
        );

        private static Action<ILogger, string, Exception> _logRequiredCultureRedirect = LoggerMessage.Define<string>(
            logLevel: LogLevel.Information,
            eventId: 1002,
            formatString: "No request culture parameter found. Redirecting to '{Path}'."
        );

        private static Action<ILogger, string, Exception> _logLocalizationCookieAppended = LoggerMessage.Define<string>(
            logLevel: LogLevel.Information,
            eventId: 1003,
            formatString: "Localization cookie appended for '{Path}'"
        );

        public static void LogLocalizationCookieAppended(this ILogger logger, string path) => 
            _logLocalizationCookieAppended(logger, path, null);

        public static void LogRequestCultureNotFound(this ILogger logger, string path) => 
            _logRequestCultureNotFound(logger, path, null);

        public static void LogRequestCultureNotFoundRedirect(this ILogger logger, string path) => 
            _logRequestCultureNotFoundRedirect(logger, path, null);

        public static void LogRequiredCultureRedirect(this ILogger logger, string path) => 
            _logRequiredCultureRedirect(logger, path, null);
    }
}